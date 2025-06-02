# -*- coding:utf-8 -*-
import json
import os.path
import time
import whisper

from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from pydub import AudioSegment
from io import BytesIO
from pydub.silence import split_on_silence
from config.the_logger import logger

import asr_fun
from config import config
from util import wav_util
from util.http_util import download_file

from util.huawei_obs import upload_obs, upload_obs_mini


def remove_audio_slice(src_wav, remove_slice_out_audio):
    sound = AudioSegment.from_file(src_wav, format="wav")
    chunks = split_on_silence(sound,
                              # must be silent for at least half a second,沉默半秒
                              min_silence_len=1000,
                              # consider it silent if quieter than -16 dBFS
                              silence_thresh=-60,
                              keep_silence=200
                              )
    sum = sound[:1]
    for i, chunk in enumerate(chunks):
        sum = sum + chunk
    sum.export(remove_slice_out_audio, format="wav")


# 阿里语音文件识别 支持8/16K 不超过60s或2M的wav/pcm
def format_asr_input(audio_url, session_dir, session_id, date_string):
    if not audio_url:
        raise Exception("audio_url error")

    file_save_path = session_dir + '/' + 'raw.wav'
    if audio_url.startswith("http"):
        download_file(audio_url, file_save_path)
    else:
        file_save_path = audio_url

    _rt, data = wav_util.clean_wav(file_save_path, cut_duration=30, sample_rate=16000)
    if not _rt:
        raise Exception(f"clean_wav failed:{data}")

    wav_util.split_audio(data, session_dir)
    new_vad_path = data

    # 上传obs的本地文件
    asr_format_audio_url = upload_obs(date_string, new_vad_path, session_id, "asr_format.wav")
    return asr_format_audio_url, new_vad_path





def asr_wav_by_whisper(local_audio_save_path):
    logger.info('asr_wav_by_whisper start')

    model = whisper.load_model("large")
    transcription = model.transcribe(local_audio_save_path)

    if transcription and "segments" in transcription.keys():
        segments = transcription['segments']
        return ",".join([segment['text'] if 'text' in segment.keys() else '' for segment in segments])
    else:
        raise Exception("asr_wav_by_whisper failed")


def fileTrans(akId, akSecret, appKey, fileLink):
    # 地域ID，固定值。
    REGION_ID = "cn-shanghai"
    PRODUCT = "nls-filetrans"
    DOMAIN = "filetrans.cn-shanghai.aliyuncs.com"
    API_VERSION = "2018-08-17"
    POST_REQUEST_ACTION = "SubmitTask"
    GET_REQUEST_ACTION = "GetTaskResult"
    # 请求参数
    KEY_APP_KEY = "appkey"
    KEY_FILE_LINK = "file_link"
    KEY_VERSION = "version"
    KEY_ENABLE_WORDS = "enable_words"
    # 是否开启智能分轨
    KEY_AUTO_SPLIT = "auto_split"
    # 响应参数
    KEY_TASK = "Task"
    KEY_TASK_ID = "TaskId"
    KEY_STATUS_TEXT = "StatusText"
    KEY_RESULT = "Result"
    # 状态值
    STATUS_SUCCESS = "SUCCESS"
    STATUS_RUNNING = "RUNNING"
    STATUS_QUEUEING = "QUEUEING"
    # 创建AcsClient实例
    client = AcsClient(akId, akSecret, REGION_ID)
    # 提交录音文件识别请求
    postRequest = CommonRequest()
    postRequest.set_domain(DOMAIN)
    postRequest.set_version(API_VERSION)
    postRequest.set_product(PRODUCT)
    postRequest.set_action_name(POST_REQUEST_ACTION)
    postRequest.set_method('POST')
    # 新接入请使用4.0版本，已接入（默认2.0）如需维持现状，请注释掉该参数设置。
    # 设置是否输出词信息，默认为false，开启时需要设置version为4.0。
    task = {KEY_APP_KEY: appKey, KEY_FILE_LINK: fileLink, KEY_VERSION: "4.0", KEY_ENABLE_WORDS: False}
    # 开启智能分轨，如果开启智能分轨，task中设置KEY_AUTO_SPLIT为True。
    # task = {KEY_APP_KEY : appKey, KEY_FILE_LINK : fileLink, KEY_VERSION : "4.0", KEY_ENABLE_WORDS : False, KEY_AUTO_SPLIT : True}
    task = json.dumps(task)
    logger.info(task)
    postRequest.add_body_params(KEY_TASK, task)
    try:
        postResponse = client.do_action_with_exception(postRequest)
        postResponse = json.loads(postResponse)
        logger.info(f'asr调用返回结果为：{postResponse}')
        statusText = postResponse[KEY_STATUS_TEXT]
        if statusText == STATUS_SUCCESS:
            logger.info("录音文件识别请求成功响应！")
            taskId = postResponse[KEY_TASK_ID]
        else:
            logger.info("录音文件识别请求失败！")
            return
    except ServerException as e:
        raise Exception(e)
    except ClientException as e:
        raise Exception(e)
    # 创建CommonRequest，设置任务ID。
    getRequest = CommonRequest()
    getRequest.set_domain(DOMAIN)
    getRequest.set_version(API_VERSION)
    getRequest.set_product(PRODUCT)
    getRequest.set_action_name(GET_REQUEST_ACTION)
    getRequest.set_method('GET')
    getRequest.add_query_param(KEY_TASK_ID, taskId)

    while True:
        try:
            getResponse = client.do_action_with_exception(getRequest)
            getResponse = json.loads(getResponse)
            logger.info(f'获取asr：{json.dumps(getResponse, ensure_ascii=False)}')
            statusText = getResponse[KEY_STATUS_TEXT]
            if statusText == STATUS_RUNNING or statusText == STATUS_QUEUEING:
                # 继续轮询
                time.sleep(10)
            else:
                # 退出轮询
                break
        except ServerException as e:
            raise Exception(e)
        except ClientException as e:
            raise Exception(e)
    text = str()

    sentences = []
    if statusText == STATUS_SUCCESS:
        logger.info("录音文件识别成功！")
        sentences = getResponse[KEY_RESULT]['Sentences']
        for sentence in sentences:
            logger.info(sentence)
            text += sentence['Text'] + '\n'
    else:
        logger.info("录音文件识别失败！")
    return text, sentences


def after_asr_process(asr_ret, sentence_list, local_audio_save_path, audio_bytes, asr_format_audio_url, is_local_request):
    """
    asr完成之后，需要做如下处理：
    1. 判断音频有效时长是否在10到40s之间，小于10s直接报错返回
    2. 音频大于40s，则需要根据asr实际断句内容切割音频，保证音频中句子的完整性和小于40s这个特点
    """
    logger.info(f'asr_with_format start, asr_ret: {asr_ret}, sentences: {sentence_list}')

    if not sentence_list:
        raise Exception('invalid asr response')

    audio = AudioSegment.from_file(BytesIO(audio_bytes), format="wav")
    src_duration = audio.duration_seconds
    if src_duration < config.min_wav_time:
        logger.warning(f'asr处理失败，音频时长小于{config.min_wav_time}s')
        raise Exception(f'audio duration < {config.min_wav_time}s')
    logger.info(f'准备处理asr结果, 原始文件音频时长: {src_duration}')

    if src_duration <= config.max_wav_time:
        logger.info(
            f'asr音频在10s到40s之间，结果符合要求，直接返回: {asr_ret}, asr_format_audio_url: {asr_format_audio_url}')
        return asr_ret, audio_bytes, asr_format_audio_url if not is_local_request else local_audio_save_path

    # 大于40s的音频，需要根据asr实际断句内容切割音频
    max_end_time = 0
    ret_asr_list = []
    for sentence in sentence_list:
        end_time = int(sentence.get('EndTime', -1))
        asr_text = sentence.get('Text', '')
        if config.max_wav_time * 1000 > end_time > max_end_time:
            ret_asr_list.append(asr_text)
            max_end_time = end_time
    logger.info(f'获取的asr最大结束时间为：{max_end_time}')

    audio = audio[:max_end_time]
    audio_data = BytesIO()
    audio.export(audio_data, format="wav")
    with open(local_audio_save_path, "wb") as ff:
        ff.write(audio_data.getvalue())

    # 上传obs
    if not is_local_request:
        upload_obs_mini(local_audio_save_path, asr_format_audio_url)
    else:
        asr_format_audio_url = local_audio_save_path

    logger.info(f'经过处理之后的asr文本为：{ret_asr_list}, asr_format_audio_url: {asr_format_audio_url}')
    return ''.join(ret_asr_list), audio_data.getvalue(), asr_format_audio_url


def asr_with_format(audio_url, lang, session_dir, session_id, date_string):
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
    asr_format_audio_url, local_audio_save_path = format_asr_input(audio_url, session_dir, session_id, date_string)

    if config.is_local:
        asr_ret = asr_fun.asr(local_audio_save_path)
        asr_format_audio_url = local_audio_save_path
    else:
        asr_ret, sentences = asr_wav(lang, asr_format_audio_url)
        # 如果原始url为本地地址，则返回的也是本地地址，不需要经过obs
        asr_format_audio_url = asr_format_audio_url if audio_url.startswith('http') else local_audio_save_path

        # asr_ret, remove_slice_out_audio_bytes, asr_format_audio_url = after_asr_process(asr_ret, sentences, local_audio_save_path, remove_slice_out_audio_bytes, asr_format_audio_url, is_local_request)

    if not asr_ret:
        raise Exception('asr_ret is empty')

    asr_ret = str(asr_ret).replace("\n", "").replace("\r", "")
    logger.info(f'最终返回的asr：{asr_ret}')
    return asr_ret, asr_format_audio_url


# if __name__ == '__main__':
#     asr_ret, remove_slice_out_audio_bytes, asr_format_audio_url = asr_with_format(
#         "https://tts.guiji.ai/open-api/wav/Vu/VuL8ZjBlhKfTRvQ7.wav",
#         "zh",
#         r"E:\code\deeplearning\fish-speech-1.2\sessions\20240715\hhh",
#         "jjsgsgj",
#         "20240715")

if __name__ == '__main__':
    rt = asr_wav('zh',
                 'https://digital-public-dev.obs.myhuaweicloud.com/vcm_server/20241118/ae8f0acc3bf34fa588276abfd2dff057/asr_format.wav')
    logger.info(rt)
