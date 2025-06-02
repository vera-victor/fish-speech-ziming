#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-----------------------------------------------
    File_Name:      log_helper.py
    Description:    TODO
    Author:         z_q_mao
    Create_Date:    7/10/20_4:32 PM
-----------------------------------------------
"""
import os
import socket
from datetime import datetime
import logging
from logging.handlers import SysLogHandler
# from service.modules.config.config_helper import global_config
#
# LOG_PATH = global_config.get_value(section="APP", option="LOG_PATH", default="log")
# SYSLOG_PORT = global_config.get_int(section="APP", option="syslog_port", default=30000)
# SYSLOG_IP = global_config.get_value(section="APP", option="syslog_ip", default="127.0.0.1")
# BASE_DIR = os.path.expanduser("~/log")
LOG_LEVEL = 10

"""
日志分级说明：
critical(严重)
严重错误，表明软件已不能继续运行了。
error(错误)
由于更严重的问题，软件已不能执行一些功能了。
warn(警告)
表明发生了一些意外，或者不久的将来会发生问题（如‘磁盘满了’）。软件还是在正常工作。
info(信息)
证明事情按预期工作。
debug(调试)
详细信息，典型地调试问题时会感兴趣。
"""


def get_log_path(app_port, flag=0):
    """
    日志分为app日志和会话日志两种,会话日志全路径将回复给网关
    :param app_port: 端口号
    :param flag: 返回哪个日志的全路径,0-会话日志, 1-app log
    :return: 返回日志路径
    """
    current = datetime.now().strftime("%Y%m%d")
    if flag == 0:
        log_path = os.path.join('_' + str(app_port))
    else:
        log_path = os.path.join(current + '_' + str(app_port))
    return log_path


# noinspection PyProtectedMember
def create_app_logger(name, port, log_path, loglevel=LOG_LEVEL):
    """
    以loglevel为级别创建日志对象，如果fn有值，则新增FileHandler，以fn作为日志文件名字，分别记录
    :param name: 模块名字
    :param port: port
    :param log_path: log_path
    :param loglevel: log级别
    :param fn: 新增加的文件名字
    :return: 新创建的logger
    """
    fmt = '%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(message)s'
    datefmt = None
    current = str(name) + str('_') + str(port) + '_' + datetime.now().strftime("%Y%m%d%H%M") + '.log'
    filename = os.path.join(log_path, current)
    # set up logging to file
    # logging.basicConfig(
    #     filename=fn,
    #     level=loglevel,
    #     format=fmt,
    #     datefmt=datefmt
    # )

    logger = logging.getLogger(name)
    logger.handlers = []
    logger.setLevel(loglevel)
    formatter = logging.Formatter(fmt, datefmt=datefmt)
    use_stream = False  # for test
    use_syslog = False
    if use_stream:
        _handler = logging.StreamHandler()
        _handler.setLevel(loglevel)
        _handler.setFormatter(formatter)
        logger.addHandler(_handler)
    if filename:
        fh = logging.handlers.WatchedFileHandler(filename, mode='a+', encoding="utf-8")
        fh.setLevel(loglevel)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    # if use_syslog:
    #     try:
    #         log_hdlr = SysLogHandler((SYSLOG_IP, SYSLOG_PORT), SysLogHandler.LOG_AUTH,
    #                                  socktype=socket.SOCK_STREAM)
    #         log_hdlr.setLevel(loglevel)
    #         log_hdlr.setFormatter(formatter)
    #         logger.addHandler(log_hdlr)
    #     except(IOError, TypeError):
    #         pass

    logger.old_info = logger.info
    logger.old_debug = logger.debug
    logger.old_warning = logger.warning
    logger.old_error = logger.error
    logger.old_exception = logger.exception
    logger.old_critical = logger.critical
    import sys
    logging.currentframe = lambda: sys._getframe(3)
    return logger


def get_abs_path(pth):
    if not os.path.isabs(pth):
        # return os.path.realpath(os.path.join(get_app_path(), pth))
        # return os.path.realpath(os.path.join(os.path.expanduser('~'), pth))
        return os.path.realpath(os.path.join(os.path.join(os.path.dirname(__file__), '..'), pth))
    else:
        return pth


app_logger = create_app_logger("gjtts_server", os.environ.get("APP_PORT", "10000"), 'logfile')
