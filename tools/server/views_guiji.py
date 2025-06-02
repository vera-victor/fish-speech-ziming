import datetime
import io
import os
import traceback
import uuid
from http import HTTPStatus

import soundfile as sf
from kui.asgi import Body, HTTPException, JSONResponse, Routes, StreamResponse, request

import asr_fun
from config.the_logger import logger
from typing_extensions import Annotated

from config import config
from asr import asr_with_format
from tools.entity.commons import TrainRequest
from tools.entity.tts import TtsItem, ReferenceAudio
from tools.helper.ali_asr_helper import call_asr
from tools.schema import (
    ServeTTSRequest, ServeReferenceAudio,
)
from tools.server.api_utils import (
    buffer_to_async_generator,
    get_content_type,
    inference_async,
)
from tools.server.inference import inference_wrapper as inference
from tools.server.model_manager import ModelManager
from util import http_util, wav_util
from util.http_util import download_file

MAX_NUM_SAMPLES = int(os.getenv("NUM_SAMPLES", 1))

routes = Routes()


def build_tts_item(req: TrainRequest) -> TtsItem:
    item = TtsItem()
    item.raw_request = req
    now = datetime.datetime.now()
    date_string = now.strftime("%Y%m%d")
    item.session_id = str(uuid.uuid4()).replace("-", "")
    item.session_dir = os.path.join(config.download_path, date_string, item.session_id)
    if not os.path.exists(item.session_dir):
        logger.info(f'创建会话目录：{item.session_dir}')
        os.makedirs(item.session_dir)

    if not req.reference_audio.startswith('http'):  # 本地文件
        req.reference_audio = config.media_path + '/' + req.reference_audio
        logger.info(f'reference_audio不是url地址，本地路径为：{req.reference_audio}')
        if not os.path.exists(req.reference_audio):
            raise Exception('file not exists')
        item.raw_audio_path = req.reference_audio
    else:
        logger.info(f'准备开始下载原始音频：{req.reference_audio}')
        file_save_path = item.session_dir + '/' + 'raw.wav'
        download_file(req.reference_audio, file_save_path)
        if not os.path.exists(file_save_path):
            raise Exception('audio download failed')
        logger.info(f'原始音频下载成功，本地路径为：{file_save_path}')
        item.raw_audio_path = file_save_path

    return item


def generate_reference_info(item: TtsItem):
    _rt, data = wav_util.clean_wav(item.raw_audio_path)
    if not _rt:
        logger.info(f"[{item.session_id}]clean_wav failed:{data}")
        raise Exception(f"clean_wav failed:{data}")

    audio_list = wav_util.split_audio(data, item.session_dir)
    for a_file in audio_list:
        if config.is_local:
            text = asr_fun.asr(a_file)
            obs_url = a_file
        else:
            text, obs_url = call_asr(item.session_id, a_file)

        logger.info(f'开始处理音频[{a_file}], asr内容为：[{text}]')
        if text and text.strip():
            logger.info(f"[{item.session_id}] asr_content:{text}, 增加音频信息")
            item.reference_audios.append(ReferenceAudio(local_audio_path=a_file,
                                                        audio_upload_url=obs_url,
                                                        asr_content=text))
        else:
            logger.info(f"[{item.session_id}]asr_content is empty")
    return True


@routes.http.post("/v1/preprocess_and_tran")
async def api_do_preprocess(
        req: Annotated[TrainRequest, Body(exclusive=True)],
):
    logger.info(f'收到训练请求：{req}')
    if not req.reference_audio or not req.lang:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            content=f"reference_audio or lang is needed",
        )
    try:
        tts_item: TtsItem = build_tts_item(req)
        logger.info(f'构建tts_item成功:{tts_item.model_dump_json()}')
        rt = generate_reference_info(tts_item)
        if rt:
            reference_texts = [x.asr_content for x in tts_item.reference_audios]
            reference_urls = [x.audio_upload_url for x in tts_item.reference_audios]
            if len(reference_texts) > 0:
                ret = {"code": 0, "msg": "success", "reference_audio_text": '|||'.join(reference_texts),
                       "asr_format_audio_url": '|||'.join(reference_urls)}
            else:
                ret = {"code": -1, "msg": "asr failed"}
        else:
            ret = {"code": -1, "msg": "asr failed, generate"}
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"An error occurred: {e}\nStack trace:\n{stack_trace}")
        ret = {"code": -1, "msg": str(e)}

    logger.info(f'训练返回结果：{ret}')
    return JSONResponse(ret)


@routes.http.post("/v1/health")
async def health():
    return JSONResponse({"status": "ok"})


async def _build_solo_reference(reference_audio, reference_text):
    if reference_audio.startswith("http"):
        audio_local_path = config.media_path + '/' + os.path.basename(reference_audio)
        rt, data = await http_util.async_download(reference_audio, audio_local_path)
        if not rt:
            logger.warning(f"tts调用失败，引用音频下载错误：{data}, url:{reference_audio}")
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                content=f"reference_audio is not valid",
            )
    else:
        audio_local_path = reference_audio

    with open(audio_local_path, "rb") as file:
        audio_data = file.read()

    if len(audio_data) < 200:
        logger.warning(f"tts调用失败，引用音频下载错误, len小于200, url:{reference_audio}")
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            content=f"reference_audio is not valid len<200",
        )

    return ServeReferenceAudio(
        audio=audio_data,
        text=reference_text,
    )


async def build_references(reference_audio, reference_text):
    if '|||' in reference_audio:
        reference_audios = reference_audio.split('|||')
        reference_texts = reference_text.split('|||')
        if len(reference_audios) != len(reference_texts):
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                content=f"reference_audio and reference_text is not match",
            )
        references = []
        for reference_audio, reference_text in zip(reference_audios, reference_texts):
            references.append(await _build_solo_reference(reference_audio, reference_text))
        return references
    else:
        return [await _build_solo_reference(reference_audio, reference_text)]


@routes.http.post("/v1/invoke")
async def tts(req: Annotated[ServeTTSRequest, Body(exclusive=True)]):
    logger.info(f"收到tts调用：{req.model_dump_json()}")
    # Get the model from the app
    app_state = request.app.state
    model_manager: ModelManager = app_state.model_manager
    engine = model_manager.tts_inference_engine
    sample_rate = engine.decoder_model.spec_transform.sample_rate

    # Check if the text is too long
    if 0 < app_state.max_text_length < len(req.text):
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            content=f"Text is too long, max length is {app_state.max_text_length}",
        )

    # Check if streaming is enabled
    if req.streaming and req.format != "wav":
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            content="Streaming only supports WAV format",
        )

    req.references = await build_references(req.reference_audio, req.reference_text)

    # Perform TTS
    if req.streaming:
        return StreamResponse(
            iterable=inference_async(req, engine),
            headers={
                "Content-Disposition": f"attachment; filename=audio.{req.format}",
            },
            content_type=get_content_type(req.format),
        )
    else:
        fake_audios = next(inference(req, engine))
        buffer = io.BytesIO()
        sf.write(
            buffer,
            fake_audios,
            sample_rate,
            format=req.format,
        )

        return StreamResponse(
            iterable=buffer_to_async_generator(buffer.getvalue()),
            headers={
                "Content-Disposition": f"attachment; filename=audio.{req.format}",
            },
            content_type=get_content_type(req.format),
        )
