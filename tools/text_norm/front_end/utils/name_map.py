# -*- coding: utf-8 -*-
# Create Time: 2020/10/28 下午7:44
# Author: Allen

import os
import json
from tools.text_norm.log.log_helper import app_logger
# from service.modules.config.config_helper import global_config
#
# WORKING_DIR = global_config.get_value(section="APP", option="WORKING_DIR", default="./model")

name_polyphone_fp = os.path.join("tools/text_norm/front_end/utils/name_polyphone.json")

if os.path.exists(name_polyphone_fp):
    app_logger.info("加载自定义 姓名多音字 [%s]" % name_polyphone_fp)
    with open(name_polyphone_fp, "r") as rf:
        mapping = json.load(rf)
else:
    raise FileNotFoundError(name_polyphone_fp)
