import json
import time

from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from config import config
from config.the_logger import logger


def asr_wav(lan, wav_url):
    logger.info(f'ali asr_wav start, call asr: {lan}, wav_url: {wav_url}')
    accessKeyId = config.access_key_id
    accessKeySecret = config.access_key_secret
    if lan == 'zh' or lan == 'cn':
        appKey = config.appKey_cn  # 中文
    else:
        appKey = config.appKey_en  # 英文
    # 执行录音文件识别
    return fileTrans(accessKeyId, accessKeySecret, appKey, wav_url)


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


if __name__ == '__main__':
    asr_wav('cn', 'https://digital-public-dev.obs.cn-east-3.myhuaweicloud.com/11/32s_16k.wav')
