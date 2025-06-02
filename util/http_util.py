import contextlib
import json
import os

import aiofiles
import aiohttp
import requests

from config import config
from config.the_logger import log, logger

# http超时时长，默认设置为3秒
http_timeout = 3
download_timeout = (3, 30)


async def async_get(url, headers: dict = None, is_json=True):
    """
    发起异步get请求，请求体和应答体，都是json格式
    :param is_json:
    :param url: 请求地址
    :param headers: 头字段
    :return:
    """
    async with aiohttp.ClientSession() as session:
        if is_json:
            if not headers:
                headers = {'Content-Type': 'application/json'}
            else:
                headers.update({'Content-Type': 'application/json'})
        try:
            async with session.get(url, headers=headers) as response:
                resp_content = await response.text()
                if response.status != 200:
                    log.warning(f'http get获取失败，http text:{resp_content}, url:{url}')
                    return False, 'status code: ' + str(response.status)
                return True, json.loads(resp_content)
        except Exception as e:
            log.error(f'async_get error:{e}')
            return False, str(e)


async def async_post(url, data: dict, headers: dict = None, is_json=True):
    """
    发起异步post请求，请求体和应答体，都是json格式
    :param is_json:
    :param url: 请求地址
    :param data: 请求数据，dict
    :param headers: 头字段
    :return:
    """
    async with aiohttp.ClientSession() as session:
        if is_json:
            if not headers:
                headers = {'Content-Type': 'application/json'}
            else:
                headers.update({'Content-Type': 'application/json'})
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        async with session.post(url, data=data, headers=headers) as response:
            if response.status != 200:
                raise Exception(f'post status code:{response.status}')
            resp_content = await response.text()
            return json.loads(resp_content)


@contextlib.asynccontextmanager
async def async_post_stream_json(url, data: dict, headers: dict = None, ignore_http_200_check=False):
    """
    发起异步请求，并对返回的response做上下文管理

    调用方式：
    with async_post_stream_json(url, payload, headers) as response:
       for chunk in response.iter_lines():
                pass
    :param url:
    :param data:
    :param headers:
    :param ignore_http_200_check: 是否忽略http状态200检查
    :return:
    """
    raw_headers = {'Content-Type': 'application/json'}
    if headers:
        raw_headers.update(headers)

    async with aiohttp.ClientSession() as session:
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        async with session.post(url, data=data, headers=raw_headers) as response:
            if not ignore_http_200_check:
                if response.status != 200:
                    raise Exception(f'post status code:{response.status}')
            yield response


def post_json(url, headers, body):
    try:
        raw_headers = {'Content-Type': 'application/json'}
        if headers:
            raw_headers.update(headers)
        # data = json.dumps(body, ensure_ascii=False).encode('utf-8')
        resp = requests.post(url, headers=raw_headers, json=body)
    except Exception as e:
        return False, str(e)

    if resp.status_code != 200:
        log.warning(f'http get获取失败，http status code:{resp.status_code}, url:{url}')
        return False, f'status code:{resp.status_code}'
    return True, json.loads(resp.text)


def get_json(url, headers=None):
    try:
        raw_headers = {'Content-Type': 'application/json'}
        if headers:
            raw_headers.update(headers)

        if config.enable_proxy:
            resp = requests.get(url, proxies={"https": config.http_proxy_settings}, headers=raw_headers,
                                timeout=http_timeout)
        else:
            resp = requests.get(url, headers=raw_headers, timeout=http_timeout)
    except Exception as e:
        return False, str(e)

    if resp.status_code != 200:
        log.warning(f'http get获取失败，http status code:{resp.status_code}, url:{url}')
        return False, f'status code:{resp.status_code}'
    return True, json.loads(resp.text)


def download_file(file_url, local_path):
    chunk_size = 4096
    lst_size = 0
    total_size = 0
    with requests.get(file_url, stream=True, verify=False, timeout=config.down_load_time_out) as r:  # 请求图片链接
        with open(local_path, "wb") as ff:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if total_size - lst_size > 5 * 1024 * 1024:
                    logger.info("downloading file %f M" % (total_size / (1024 * 1024)))
                    lst_size = total_size
                total_size += len(chunk)
                ff.write(chunk)


async def async_download(url, file_path):
    """
    异步文件下载
    :param url: 文件原始url
    :param file_path: 文件保存路径
    :return:
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(file_path, mode='wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        await f.write(chunk)

                if os.path.exists(file_path):
                    return True, file_path
                else:
                    return False, 'fail to download'
            else:
                log.warning(f'文件下载失败，http status code:{response.status}, url:{url}')
                return False, f'status code:{response.status}'


if __name__ == '__main__':
    # async def download():
    #     url = 'https://digital-public-dev.obs.cn-east-3.myhuaweicloud.com/aaa/%E7%9B%B4%E6%92%AD%E5%B8%B8%E8%A7%81%E9%97%AE%E7%AD%94%EF%BC%88146%E6%AE%B5%EF%BC%89.xlsx'
    #     rt, path = await async_download(url, 'test.xlsx')
    #     print(f'下载结果：{rt}')
    #
    #
    # import asyncio
    # asyncio.run(download())
    pass
