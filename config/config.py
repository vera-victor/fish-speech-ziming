import os

# 是否本地离线版本
is_local = True

download_path = os.path.join(os.getcwd(), "sessions")
# enum 状态
task_start = 1
task_running = 2
task_complete = 3
task_fail = -1

down_load_time_out = 1200
cache_interval = 7200

# 最小音频长度, 单位是秒
min_wav_time = 10
# 最大音频长度, 单位是秒
max_wav_time = 40

# 待训练录音的保存路径
media_path = '/code/data'

# 是否开启compile加速,30系列显卡使用有问题 建议4090开启
is_compile = True
base_reference_text = "无论你是寻找舒适的驾驶体验，还是享受环保的出行方式，吉利银河E8都是你的不二之选。"
base_reference_audio = "https://digital-public-dev.obs.myhuaweicloud.com/TTS_MODELS/20240715/slice_remove.wav"

# obs
obs_end_point = 'http://obs.cn-east-3.myhuaweicloud.com'
obs_access_key = 'A0MGG9DH'
obs_secret = 'JplniUNAiu'
obs_bucket_name = 'digital-public-dev'
obs_path_prefix = 'vcm_server/'
obs_http_url_prefix = 'https://d.obs.myhuaweicloud.com/'

# 阿里asr
access_key_id = 'access_key_data'
access_key_secret = 'access_key_secret'
appKey_cn = 'ZL6BdNok'
appKey_en = 'IN2DNTDme'


# 本地funasr相关信息
fun_asr_host = 'heygem-asr'
fun_asr_port = '10095'

# 字符串分割
split_len = 100
split_symbols = ["。", "?", "？", "！", "!", ";", "；", ",", "，", "、"]

# 参数中chunk_length被强行写为200，避免单句过长，导致强行断句
max_chunk_length = 200
