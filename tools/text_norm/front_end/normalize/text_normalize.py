# -*- coding: utf-8 -*-
# Create Time: 2020/9/30 下午2:35
# Author: Allen

import json
import os
import re
import string

from tools.text_norm.log.log_helper import app_logger
from tools.text_norm.front_end.normalize.number_normalize import NumberNormalize
from tools.text_norm.front_end.normalize.text_normalize_CN_EN import TextNormalizeCnEn
from tools.text_norm.front_end.normalize.text_normalize_EN import TextNormalizeEn
# 使用正则表达式：
from tools.text_norm.front_end.normalize.text_normalize_CN import TextNormalizeCn
# 使用模型：
# from service.modules.preprocess.front_end.normalize.text_normalize_CN_cluner import TextNormalizeCn

# WORKING_DIR = global_config.get_value(section="APP", option="WORKING_DIR", default="./model")


class TextNormalize(object):
    def __init__(self):
        self.logger = app_logger
        self.text_norm_en = TextNormalizeEn()
        self.text_norm_cn = TextNormalizeCn()
        self.text_norm_cn_en = TextNormalizeCnEn()
        self.num_norm = NumberNormalize()

        english_word_expand_file = os.path.join('tools/text_norm/front_end/normalize/en_word_expand.json')
        self.expand_map = self.load_json2dict(english_word_expand_file)
        self.lower_expand_map = {k.lower(): v for k, v in self.expand_map.items()}

    @staticmethod
    def load_json2dict(json_path):
        with open(json_path, "r") as rf:
            data = json.load(rf)
        return data

    def tmp_process_text(self, text):
        """
        因为自定义拼音标识符中含有小写英文字母，会影响中英文的判断，所以删除文本中的拼音标识符
        :param text: (str)
        :return: (str)
        """
        # 删除拼音自定义标识符
        text = re.sub(r"<.*?>", '', text)
        return text

    def post_process(self, text):
        """将非英文中间的,替换成，因为自定义数据结构是用中文逗号进行分隔的，英文不支持自定义标识符，所以英文逗号前后没有自定义停顿时长"""

        def func(match):
            left_str = text[:match.span()[0]]
            right_str = text[match.span()[1]:]

            # " , "一定出现在中间
            if left_str[-1] in string.ascii_letters + "》" and right_str[0] in string.ascii_letters + "《":
                return match.group(1)
            else:
                return " ， "

        text = re.sub(r"( , )", func, text)
        return text

    def pre_process(self, text):
        """
        根据字典展开英文名词
        :param text
        """
        res = []
        for group in re.finditer("[0-9a-zA-Z][0-9A-Za-z &·@+\*\.\-/]*[0-9a-zA-Z]", text):
            v = self.expand_map.get(group.group())

            if not v:
                v = self.lower_expand_map.get(group.group().lower())
            res.append((group.group(), group.start(), group.end(), v))
        # print('############', res)
        sent = text
        for word, start, end, v in reversed(res):
            prev_sent = sent[:start]
            next_sent = sent[end:]
            if v:
                sent = prev_sent + v + next_sent

        return sent

    def recheck_lang(self, text, pure_number_language_type):
        """
        判断该以“中文”处理，还是“英文”处理，还是“中英文混合”处理
        :param text:
        :param pure_number_language_type:
        :return:
        """
        # 临时处理文本，用于判断中英文
        tmp_text = self.tmp_process_text(text)
        # lang_type = "cn_en"
        # 判断中英文
        if re.findall(r"[\u4e00-\u9fa5]", tmp_text):  # 含有中文字符
            if re.findall(r"[a-z]", tmp_text):  # 含有英文小写单词
                self.logger.debug("'%s' 判断为cn_en" % text)
                lang_type = "cn_en"
            else:  # 不含有英文小写单词
                """ 含有中文字符 + 不含有英文小写单词 => cn """
                self.logger.debug("'%s' 判断为cn" % text)
                lang_type = "cn"
        else:  # 不含有中文字符
            if re.findall(r"[a-z]", tmp_text):  # 含有英文小写字母
                self.logger.debug("'%s' 判断为en" % text)
                lang_type = "en"
            elif pure_number_language_type in ["CN", "CN_EN"]:
                if re.findall(r"^[0-9]+$", text):
                    text = self.num_norm.call(text, 'cn', 'ordinal')
                self.logger.debug("'%s' 判断为cn数字" % text)
                lang_type = "cn"
            elif pure_number_language_type in ['EN']:
                if re.findall(r"^[0-9]+$", text):
                    text = self.num_norm.call(text, 'en', 'ordinal')
                self.logger.debug("'%s' 判断为en数字" % text)
                lang_type = "en"
        return lang_type

    def call(self, text, pure_number_language_type):
        """
        :param text: (str)
                    1.至少包含一个有效字符，有效字符包含：中文、数字、英文
                    2.末尾无标点
                    3.可能包含：中文、英文小写单词、英文大写字母、数字、自定义标识符
                    4.单句，句字中没有分句标点
        :param pure_number_language_type: (str) 纯数字语言类型标记 in ["CN", "EN", "CN_EN"]
        :return: (str) 正则化后的文本
        """
        res_text = None

        lang_type = self.recheck_lang(text, pure_number_language_type)
        print(lang_type,text)
        # lang_type = 'cn_en'
        if lang_type == "cn":
            # 前处理，将专有名词拆成正确的词
            text = self.pre_process(text)
            # self.logger.debug("前处理，将专有名词拆成正确的词[输出]：%s" % text)
            res_text = self.text_norm_cn.call(text)
            res_text = self.post_process(res_text)  # 将非英文中间的,替换成，
            # self.logger.debug("将非英文中间的,替换成 [输出] %s" % res_text)
            # res_text = re.sub("[^a-z A-Z\u4e00-\u9fa5。，]+", "、", res_text)
            res_text = re.sub("，+", "，", res_text)
            res_text = re.sub("。+", "。", res_text)
            res_text = re.sub(" +", " ", res_text)
            # self.logger.debug("【正则化】将无法处理的标点符号全部替换成、 [输出] %s " % res_text)
        elif lang_type == "cn_en":
            # 前处理，将专有名词拆成正确的词
            text = self.pre_process(text)
            # self.logger.debug("前处理，将专有名词拆成正确的词[输出]：%s" % text)
            # print("前处理，将专有名词拆成正确的词[输出]：%s" % text)
            res_text = self.text_norm_cn_en.call(text)
            res_text = self.post_process(res_text)  # 将非英文中间的,替换成，
            res_text = re.sub("，+", "，", res_text)
            res_text = re.sub("。+", "。", res_text)
            res_text = re.sub(" +", " ", res_text)
            # self.logger.debug("将非英文中间的,替换成 [输出] %s" % res_text)
        elif lang_type == "en":
            text = text.replace('、',"'").replace('’',"'")
            res_text = self.text_norm_en.call(text)
            # res_text = re.sub("[^a-z A-Z,.]+", " ", res_text)
            res_text = re.sub(",+", ",", res_text)
            res_text = re.sub("\\.+", ".", res_text)
            res_text = re.sub(" +", " ", res_text)
            # res_text = re.sub(" +", " ", res_text)
            # self.logger.debug("将非英文的字符替换成 [输出] %s" % res_text)
            print(res_text)
        return res_text


if __name__ == '__main__':
    tn = TextNormalize()
    # print(tn.call("TTS测试1997年", "CN"))
    # print(tn.call("TTS测试$12.5", "CN"))
    # print(tn.call("TTS测试￥12.5", "CN"))
    # print(tn.call("TTS测试12.5%", "CN"))
    # print(tn.call("TTS测试10/13", "CN"))
    # print(tn.call("T1TNS测试文本<ben2>，hello 2020<#2>, happy new year", "CN_EN"))

    # print(tn.call("Huawei CANADA and employs over 1,200 people there", "EN"))
    # print(tn.call("Huawei Canada and employs over 1,200 people THERE", "EN"))
