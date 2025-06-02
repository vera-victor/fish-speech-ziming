from websocket import ABNF
from websocket import create_connection
from queue import Queue
import threading
import traceback
import json
import time
from config.the_logger import logger
import wave

from config import config


class funasr_client:
    def __init__(self):
        self.websocket = None
        self.msg_queue = None
        self.thread_msg = None
        self.fun_asr_host = config.fun_asr_host
        self.fun_asr_port = config.fun_asr_port
        self.chunk_size = "5, 10, 5"
        self.chunk_interval = 10
        self.mode = 'offline'
        self.wav_name = 'default'
        self.init_conn()

    def init_conn(self):
        """
           host: server host ip
           port: server port
           is_ssl: True for wss protocol, False for ws
        """
        try:
            uri = "ws://{}:{}".format(self.fun_asr_host, self.fun_asr_port)
            ssl_context = None
            ssl_opt = None

            self.msg_queue = Queue()  # used for recognized result text

            logger.info("connect to url", uri)
            self.websocket = create_connection(uri, ssl=ssl_context, sslopt=ssl_opt)
            self.thread_msg = threading.Thread(target=self.thread_rec_msg)
            self.thread_msg.start()
            chunk_size = [int(x) for x in self.chunk_size.split(",")]

            message = json.dumps({"mode": self.mode, "chunk_size": chunk_size, "encoder_chunk_look_back": 4,
                                  "decoder_chunk_look_back": 1, "chunk_interval": self.chunk_interval,
                                  "wav_name": self.wav_name, "is_speaking": True})

            self.websocket.send(message)
            logger.info(f'建立funasr连接：{message}')
        except Exception as e:
            logger.warning(f'建立funasr连接异常：{e}')
            traceback.print_exc()

    # threads for rev msg
    def thread_rec_msg(self):
        try:
            while True:
                msg = self.websocket.recv()
                if msg is None or len(msg) == 0:
                    continue
                msg = json.loads(msg)
                logger.info(f"收到ws消息：{msg}")

                self.msg_queue.put(msg)
        except Exception as e:
            logger.warning(f'读取ws消息异常：{str(e)}')

    # feed data to asr engine, wait_time means waiting for result until time out
    def feed_chunk(self, chunk, wait_time=0.01):
        try:
            self.websocket.send(chunk, ABNF.OPCODE_BINARY)
            # loop to check if there is a message, timeout in 0.01s
            while True:
                msg = self.msg_queue.get(timeout=wait_time)
                if self.msg_queue.empty():
                    break

            return msg
        except:
            return ""

    def close(self, timeout=1):
        message = json.dumps({"is_speaking": False})
        self.websocket.send(message)
        # sleep for timeout seconds to wait for result
        time.sleep(timeout)
        msg = ""
        while not self.msg_queue.empty():
            msg = self.msg_queue.get()

        self.websocket.close()
        # only resturn the last msg
        return msg


def asr(local_wav_path):
    """
    执行asr操作，参数为本地文件地址
    """
    logger.info(f"fun asr start, wav_path:{local_wav_path}")
    with wave.open(local_wav_path, "rb") as wav_file:
        frames = wav_file.readframes(wav_file.getnframes())
        audio_bytes = bytes(frames)

    stride = int(60 * 10 / 10 / 1000 * 16000 * 2)
    chunk_num = (len(audio_bytes) - 1) // stride + 1
    rcg = funasr_client()
    for i in range(chunk_num):
        beg = i * stride
        data = audio_bytes[beg:beg + stride]

        text = rcg.feed_chunk(data, wait_time=0.02)
        if len(text) > 0:
            logger.info("recv ws text:" + text)
        time.sleep(0.05)

    # get last message
    result: dict = rcg.close(timeout=3)
    if 'text' in result:
        return result['text']
    return None


if __name__ == '__main__':
    # wav_path = r"E:\media\wav\32s_16k.wav"
    wav_path = r"E:\media\wav\6s_16k.wav"
    content = asr(wav_path)
    logger.info(f"asr最终结果：{content}")
