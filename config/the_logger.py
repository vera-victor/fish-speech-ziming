import os
import sys
from loguru import logger as _logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_path = os.path.join(BASE_DIR, 'log')
if not os.path.exists(log_path):
    print('日志目录不存在，新建之: %s' % log_path)
    os.mkdir(log_path)

logger_file_name = os.environ.get('LOGGER_FILE_NAME')
if logger_file_name:
    print(f'环境变量LOGGER_FILE_NAME：{logger_file_name}')
else:
    logger_file_name = 'fish'
    print(f'环境变量LOGGER_FILE_NAME不存在，使用自定义名称：{logger_file_name}')

log_file_path = os.path.join(BASE_DIR, f'log/{logger_file_name}.log')
err_log_file_path = os.path.join(BASE_DIR, f'log/{logger_file_name}_err.log')
print(f'日志完整目录：{log_file_path}  {err_log_file_path}')

_logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
_logger.add(log_file_path, rotation="50 MB", encoding='utf-8')  # Automatically rotate too big file
_logger.add(err_log_file_path, rotation="50 MB", encoding='utf-8', level='WARNING')

log = _logger
logger = _logger

if __name__ == '__main__':
    logger.debug("That's it, beautiful and simple logging!")
    logger.debug("中文日志可以不")
    logger.error("严重错误")
    logger.error('这个有一个错误，参数是:%s' % 12345)
    logger.exception("An exception occurred: {e}")
