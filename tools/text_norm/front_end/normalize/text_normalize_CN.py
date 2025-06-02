# -*- coding: utf-8 -*-
# Create Time: 2020/9/30 上午11:55
# Author: Allen

import re
import string
from tools.text_norm.log.log_helper import app_logger
from tools.text_norm.front_end.normalize.mark_normalize_CN import MarkNormalizeCN

from tools.text_norm.front_end.normalize.num_punc_normalize_CN import NumberPunctionNormalizeCN


class TextNormalizeCn(object):
    """ 中文文本正则
    输入：
        中文字符+[英文大写字母]+[数字]+[自定义标识符]
    输出：
        正则化后的文本
    """

    def __init__(self):
        self.logger = app_logger

        self.mark_norm_cn = MarkNormalizeCN()  # 标识符解析
        self.num_punc_norm_cn = NumberPunctionNormalizeCN()  # 搭配标点的数字/默认数字转换

    def split_uppercase_letter(self, text):
        """
        分类大写字母
        :param text: (str)
        :return: (str)
        """

        def func_middle(match):
            left_str = text[:match.span()[0]]
            right_str = text[match.span()[1]:]
            if left_str == '' and right_str == '':
                return ' '.join(list(match.group(1)))
            elif left_str == '' and right_str != '':
                if right_str[0] not in string.ascii_lowercase:
                    return '%s ' % ' '.join(list(match.group(1)))
                else:
                    return match.group(1)
            elif left_str != '' and right_str == '':
                if left_str[-1] not in string.ascii_lowercase + '°':
                    return ' %s' % ' '.join(list(match.group(1)))
                else:
                    return match.group(1)
            elif left_str != '' and right_str != '':
                if left_str[-1] not in string.ascii_lowercase + '°' and right_str[0] not in string.ascii_lowercase:
                    return ' %s ' % ' '.join(list(match.group(1)))
                else:
                    return match.group(1)

        text = re.sub(r"([A-Z]+)", func_middle, text)
        text = re.sub(r" +", ' ', text)

        return text

    def call(self, text):
        """
        :param text: (str) 输入文本
        :return: (str) 正则化后的文本
        """
        # 标识符解析
        text = self.mark_norm_cn.call(text)
        self.logger.debug("标识符解析 [输出]: %s" % text)

        # 连续大写字母分割
        text = self.split_uppercase_letter(text)
        self.logger.debug("连续大写字母分割 [输出]: %s" % text)
        # print(text)
        # 搭配标点的数字/默认数字转换
        text = self.num_punc_norm_cn.call(text)
        self.logger.debug("搭配标点的数字/默认数字转换 [输出]: %s" % text)
        # print(text)
        # 空格替换
        text = re.sub(r"(?<=[\u4e00-\u9fa5]) (?=[\u4e00-\u9fa5])", '', text)  # 删除中文间的空格
        text = re.sub(r"(?<=[0-9]) (?=[\u4e00-\u9fa5])", '', text)  # 删除数字与中文间的空格
        text = re.sub(r"(?<=[\u4e00-\u9fa5]) (?=[0-9])", '', text)  # 删除中文间与数字的空格
        self.logger.debug("空格替换 [输出]: %s" % text)

        # 英文单引号删除
        text = text.replace("'", "")
        self.logger.debug("英文单引号删除 [输出]: %s" % text)

        # 添加标点间空格
        text = re.sub(r"([、,.?!，。？！])", r" \1 ", text)
        text = text.strip()
        text = re.sub(r" +", " ", text)
        self.logger.debug("添加标点间空格 [输出]: %s" % text)

        return text


if __name__ == '__main__':
    tn = TextNormalizeCn()
    text = '20年前'
    print(tn.call(text))
