import os

import requests
from config.the_logger import logger


def read_file_bytes(file_path):
    """
    获取文件数据，如果是http文件，则直接下载，否则直接读取本地文件
    """
    if file_path.startswith("http"):
        resp = requests.get(file_path, timeout=60)
        if resp.status_code != 200:
            logger.warning(f'文件下载失败：{file_path}, code:{resp.status_code}, text:{resp.text}')
            raise Exception('fail to download')
        else:
            data = resp.content
    else:
        if not os.path.exists(file_path):
            logger.warning(f'文件非http，但是本地也不存在：{file_path}')
            raise Exception("file not found")
        else:
            with open(file_path, "rb") as ff:
                data = ff.read()
    return data
