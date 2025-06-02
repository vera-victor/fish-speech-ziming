from obs import ObsClient
from config import config
from config.the_logger import logger

obsClient = ObsClient(
    access_key_id=config.obs_access_key,
    secret_access_key=config.obs_secret,
    server=config.obs_end_point)


def upload_file_callback(transferredAmount, totalAmount, totalSeconds):
    logger.info("uploading %f" % (transferredAmount * 100.0 / totalAmount) + "%")


def upload_obs(date_string, final_lang_audio_path, session_id, wav_name):
    obs_wav_key = config.obs_path_prefix + date_string + "/" + session_id + "/" + wav_name
    output_wav_url = config.obs_http_url_prefix + obs_wav_key
    obsClient.putFile(config.obs_bucket_name,
                      obs_wav_key,
                      final_lang_audio_path,
                      progressCallback=upload_file_callback)
    return output_wav_url


def upload_obs_pro(local_file_path, obs_wav_key: str):
    output_wav_url = config.obs_http_url_prefix + obs_wav_key
    obsClient.putFile(config.obs_bucket_name,
                      obs_wav_key,
                      local_file_path,
                      progressCallback=upload_file_callback)
    return output_wav_url


def upload_obs_mini(final_lang_audio_path, target_url: str):
    """
    将wav文件重复上传到同一个url地址
    """
    obs_wav_key = target_url
    if target_url.startswith(config.obs_http_url_prefix):
        obs_wav_key = target_url[len(config.obs_http_url_prefix):]

    obsClient.putFile(config.obs_bucket_name,
                      obs_wav_key,
                      final_lang_audio_path,
                      progressCallback=upload_file_callback)
    return target_url
