# -*- coding: utf-8 -*-
# Create Time: 2020/9/21 上午9:43
# Author: Allen

import re
from service.modules.preprocess.front_end.utils.custom_data_structure import CustomDataStructure
from service.modules.log.log_helper import app_logger


class CustomDataStructureList(object):
    """自定义数据结构，用于韵律预测模块、拼音校正、韵律校正"""

    def __init__(self):
        pass

    def init(self, text, lang):
        # 分小句
        sentences = [x for x in re.split(r"[，,]", text) if x != '']  # 删除标点
        cds_list = []
        for sentence in sentences:
            cds = CustomDataStructure()
            cds_list.append(cds.init(sentence, lang))
        # print([x.text_list for x in self.cds_list])
        # print([x.prosody_list for x in self.cds_list])
        # print([x.grapheme_list for x in self.cds_list])
        # print([x.before_silence for x in self.cds_list])
        # print([x.after_silence for x in self.cds_list])
        return cds_list


if __name__ == '__main__':
    text = "《＆２０００》 ， 单《ｓｈａｎ４》《＃０》静《＃０》静《＃０》"
    # text = "犹如经历追求时对方一时兴起的tease"

    cdsl = CustomDataStructureList()
    cdsl.init(text, 'CN_EN')
