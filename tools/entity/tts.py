from typing import Optional

from pydantic import BaseModel

from tools.entity.commons import TrainRequest


class ReferenceAudio(BaseModel):
    # 音频本地路径
    local_audio_path: str = None
    # 音频上传地址
    audio_upload_url: str = None
    # 音频asr内容
    asr_content: str = None


class TtsItem(BaseModel):
    session_id: str = None
    session_dir: str = None
    # 原始请求
    raw_request: TrainRequest = None
    # 原始音频在本地的路径
    raw_audio_path: str = None
    # 生成的参考音频信息
    reference_audios: Optional[list[ReferenceAudio]] = []
