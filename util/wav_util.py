import os.path

from pydub import AudioSegment
from pydub.silence import detect_nonsilent, split_on_silence
from config.the_logger import logger


def get_audio_duration(file_path):
    """
    获取音频时长，单位为秒
    """
    audio = AudioSegment.from_file(file_path)
    duration_seconds = len(audio) / 1000
    return duration_seconds


def remove_noise(raw_path, raw_output_path):
    logger.info(f"开始给wav去噪, raw_path:{raw_path}, output:{raw_output_path}")
    cmd = f'rnnoise_new {raw_path} {raw_output_path}'
    os.system(cmd)
    if not os.path.exists(raw_output_path):
        logger.warn(f"去噪音失败，文件不存在:{raw_path}")
        return False, 'file not exists'
    return True, raw_output_path


def _process_audio(audio_path, silence_thresh=-40):
    """
    按静音分割音频，并返回符合要求的片段

    参数:
        audio_path (str): 音频文件路径
        silence_thresh (int): 静音能量阈值（单位dBFS）

    返回:
        List[AudioSegment]: 符合条件的音频片段列表（最多2个）
    """
    # 1. 加载音频文件
    audio = AudioSegment.from_file(audio_path)

    # 2. 按静音分割（500ms静音触发分割）
    chunks = split_on_silence(
        audio,
        min_silence_len=500,
        silence_thresh=silence_thresh,
        keep_silence=400
    )

    # 3. 筛选10-20秒的片段
    valid_chunks = [c for c in chunks if 10000 <= len(c) <= 20000]
    if len(valid_chunks) >= 2:
        return valid_chunks[:2]

    # 4. 拼接逻辑（不切割原有片段）
    merged = []
    current_segments = []
    current_duration = 0

    for chunk in chunks:
        chunk_len = len(chunk)

        # 尝试将当前片段加入拼接队列
        if current_duration + chunk_len > 20000:  # 超过20秒
            if 10000 <= current_duration <= 20000:  # 保存已有拼接结果
                merged.append(sum(current_segments))
                if len(merged) >= 2: break
            current_segments = [chunk] if chunk_len <= 20000 else []
            current_duration = chunk_len if chunk_len <= 20000 else 0
        else:
            current_segments.append(chunk)
            current_duration += chunk_len

        # 达到有效时长时保存
        if 10000 <= current_duration <= 20000:
            merged.append(sum(current_segments))
            if len(merged) >= 2: break
            current_segments = []
            current_duration = 0

    # 处理剩余片段
    if len(merged) < 2 and 10000 <= current_duration <= 20000:
        merged.append(sum(current_segments))

    # 如果分割不到任何结果，则直接从原始音频中截取20s返回。
    if len(merged) == 0:
        logger.info(f'根据静音分割失败，尝试从原始音频中截取20s返回, 文件:{audio_path}')
        merged = [audio[0:20000]]

    return merged[:2]


def split_audio(input_file, output_dir):
    duration = get_audio_duration(input_file)
    if duration < 20:
        logger.info(f'原始音频小于20s，不在分割，直接返回, 时长为：{duration}, 文件:{input_file}')
        return [input_file]

    logger.info(f'开始分割文件，原文件:{input_file}, 输出目录：{output_dir}')
    try:
        audio_segment_list = _process_audio(input_file)
    except Exception as e:
        logger.exception(f'音频分割失败:{str(e)}')
        raise Exception(f'fail to split audio')

    # 保存为文件
    rt_list = []
    name_prefix = os.path.splitext(os.path.basename(input_file))
    for i, audio_segment in enumerate(audio_segment_list):
        output_path = os.path.join(output_dir, f'{name_prefix[0]}_part{i}.wav')
        audio_segment.export(output_path, format='wav')
        rt_list.append(output_path)

    logger.info(f'文件分割结束，结果为：{rt_list}')
    return rt_list


def format_wav(wav_path):
    """
    将wav文件转为标准格式：采样率16000， 编码为s16le， 避免后续asr报错
    """
    logger.info(f'开始统一音频格式：{wav_path}')
    wav_dir, name = os.path.split(wav_path)
    new_name = os.path.join(wav_dir, 'format_' + name)
    cmd = f'ffmpeg -i {wav_path}  -ar 16000 -c:a pcm_s16le -y {new_name}'
    logger.info(f'音频统一转为16000 pcm s16，便于后面处理， 命令为：{cmd}')
    os.system(cmd)
    if os.path.exists(new_name):
        logger.info(f'wav标准格式化成功，{wav_path} -> {new_name}')
        os.remove(wav_path)
        return True, new_name
    else:
        return False, 'fail to format'


def clean_wav(wav_path):
    """
    统一音频格式，并去噪
    """
    logger.info(f'开始清理音频：{wav_path}')
    wav_dir, name = os.path.split(wav_path)

    # 切割音频，并转为16000，防止denoise报错
    rt, new_data = format_wav(wav_path)
    if not rt:
        return False, f'format failed: {new_data}'
    wav_cut_path = new_data

    # 去噪
    after_denoise_path = os.path.join(wav_dir, 'denoise_' + name)
    rt, data = remove_noise(wav_cut_path, after_denoise_path)
    if not rt:
        return False, f'denoise failed: {data}'

    # 去噪后，会变为pcm_s32, 需要再次转为16000， pcm_s16le
    rt, final_path = format_wav(data)
    logger.info(f'音频清理完成，新文件路径：{data}')
    return rt, final_path


if __name__ == '__main__':
    wav_file = '/code/sessions/20250213/bf36e304ac6f4e3cb8d4d43679774fcc/denoise_raw.wav'
    s_dir = '/code/sessions/20250213/bf36e304ac6f4e3cb8d4d43679774fcc'
    split_audio(wav_file, s_dir)
