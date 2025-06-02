from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, conint


class ServeReferenceAudio(BaseModel):
    audio: bytes
    text: str


class TrainRequest(BaseModel):
    reference_audio: Optional[str] = None
    format: Literal["wav", "mp3", "flac"] = "wav"
    lang: Optional[str] = "zh"


class ServeTTSRequest(BaseModel):
    text: str
    chunk_length: Annotated[int, conint(ge=100, le=300, strict=True)] = 200

    format: Literal["wav", "pcm", "mp3"] = "wav"
    mp3_bitrate: Literal[64, 128, 192] = 128

    reference_text: Optional[str] = None
    reference_audio: Optional[str] = None
    speaker: Optional[str] = None
    lang: Optional[str] = "zh"

    need_asr: bool = False
    normalize: bool = True
    mp3_bitrate: Optional[int] = 64
    opus_bitrate: Optional[int] = -1000
    # Balance mode will reduce latency to 300ms, but may decrease stability
    latency: Literal["normal", "balanced"] = "normal"
    # not usually used below
    streaming: bool = False
    emotion: Optional[str] = None
    max_new_tokens: int = 1024
    top_p: Annotated[float, Field(ge=0.1, le=1.0, strict=True)] = 0.7
    repetition_penalty: Annotated[float, Field(ge=0.9, le=2.0, strict=True)] = 1.2
    temperature: Annotated[float, Field(ge=0.1, le=1.0, strict=True)] = 0.7
    seed: Optional[int] = None
    is_norm: Optional[int] = None
