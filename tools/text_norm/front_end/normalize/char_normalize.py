# -*- coding: utf-8 -*-
# Create Time: 2020/9/30 下午1:35
# Author: Allen
import re
from tools.text_norm.log.log_helper import app_logger
from tools.text_norm.front_end.normalize.char_mapping import mapping, en_mapping


class CharNormalize(object):
    """
    标点正则
    功能：
        将任意输入文本中的标点进行正则：
        1.删除不支持的标点
        2.映射支持的标点到有限多个标点
        3.停顿标点正则
    """

    def __init__(self):

        # 支持的中文字符
        self.chinese_char_list = [chr(i) for i in range(ord('\u4e00'), ord('\u9fa5') + 1)]

        # 支持的英文字符
        self.english_char_list = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

        # 支持的数字字符
        self.digit_list = list("0123456789")

        # 支持的标点
        self.punctuation_key_list = list(mapping.keys())
        self.punctuation_value_set = set(''.join(mapping.values()))

        # 映射表的作用是将支持的字符（除中文字符）映射到有限个字符
        # 映射标的value值是由extra_char_list、en_char_list、digit_list组成
        # 即，char_normalize后的文本中只包含extra_char_list、en_char_list、digit_list中的字符
        self.extra_char_list = list("，。？！、\',.?!-+=~<>{}()#@$& %‰￥μ:°/")  # 除了

        assert_error_info = "检查失败，失败字符{}！【修改self.extra_char_list或mapping】".format(
            set(self.extra_char_list + self.english_char_list + self.digit_list) ^ self.punctuation_value_set)
        assert set(
            self.extra_char_list + self.english_char_list + self.digit_list) == self.punctuation_value_set, assert_error_info

        # 所有可以被处理的符号，除此以外的字符都会被替换
        # 中文字符 + 英文字符 + 数字字符 + 标点字符
        self.all_support_char_list = self.chinese_char_list + self.english_char_list + self.digit_list + self.punctuation_key_list

        # 停顿符
        self.chinese_pause_char = ""
        self.english_pause_char = ""

    def replace_unsupported_char(self, text, replace_char='，'):
        """
        将[不支持的]字符替换成replace_char
        :param text: (str)
        :param replace_char: (str) 被替换的字符
        :return: (str)
        """
        text = re.sub(r"[^%s]" % ''.join(self.all_support_char_list), replace_char, text)
        return text

    @staticmethod
    def mapping_supported_char(text):
        """
        将[支持的]字符映射成有限个
        :param text: (str)
        :return: (str)
        """
        # 将中文顿号替换成逗号
        # text = text.replace('、', '，')  # 注释掉，顿号不应该为#3

        mapping_ord = {ord(k): v for k, v in mapping.items()}
        res_text = text.translate(mapping_ord)
        return res_text

    @staticmethod
    def mapping_supported_char_en(text):
        """
        将[支持的]字符映射成有限个
        :param text: (str)
        :return: (str)
        """
        mapping_ord = {ord(k): v for k, v in en_mapping.items()}
        res_text = text.translate(mapping_ord)
        res_text = res_text.replace('、', ' ')  # en_mapping映射中有很多个、号

        return res_text

    def pause_char_normalize_CN_EN(self, text):
        """
        中英混合标点正则：
        :param text: (str)
        :return: (str)
        """
        # 标点与语言统一
        text = text.replace("!", "！").replace("?", "？")

        # 停顿标点去重
        text = re.sub(r"([,.?!、，。？！ ])\1+", r'\1', text)

        # 停顿标点消歧
        ## 前标点
        text = re.sub(r"^([,.?!、，。？！ ]*)", '', text)

        ## 中间标点
        def func_middle(match):
            puns = match.group(1).replace(' ', '')
            if re.findall(r"[.?!。？！]", puns):
                res_pun = re.findall(r"[.?!。？！]", puns)[0]
                if res_pun in '.?!':
                    return "%s " % res_pun
                else:
                    return res_pun
            elif re.findall(r"[,，]", puns):
                res_pun = re.findall(r"[,，]", puns)[0]
                if res_pun in ',':
                    return "%s " % res_pun
                else:
                    return res_pun
            else:
                return puns[0]

        text = re.sub(r"([,.?!、，。？！ ]{2,})", func_middle, text)  # 连续标点个数为1的不处理

        ## 后标点
        def func_end(match):
            puns = match.group(1).replace(" ", '')
            if len(puns) == 1:  # 标点数据正确
                if puns in "？！":
                    return puns
                else:
                    return "。"
            else:  # 标点数量不正确
                return "。"

        if text.endswith('？') or text.endswith('！'):
            pass
        else:
            text += '。'

        text = re.sub(r"([,.?!、，。？！ ]+)$", func_end, text)
        return text

    def pause_char_normalize_CN(self, text):
        """
        CN标点正则：
        :param text: (str)
        :return: (str)
        """

        # 停顿标点与语言统一
        """?!"""  # ,.因为包含数字歧义，在文本正则中处理
        text = text.replace("!", "！").replace("?", "？")

        # 停顿标点去重
        text = re.sub(r"([,.、，。？！ ])\1+", r'\1', text)

        # 停顿标点消歧
        ## 前标点
        text = re.sub(r"^([,.、，。？！ ]*)", '', text)

        # # 中间标点(就近原则)
        def func_middle(match):
            puns = match.group(1).replace(' ', '')
            if re.findall(r"[.?!。？！]", puns):
                res_pun = re.findall(r"[.?!。？！]", puns)[0]
                if res_pun in '.?!':
                    return "%s " % res_pun
                else:
                    return res_pun
            elif re.findall(r"[,，]", puns):
                res_pun = re.findall(r"[,，]", puns)[0]
                if res_pun in ',':
                    return "%s " % res_pun
                else:
                    return res_pun
            else:
                return puns[0]

        text = re.sub(r"([,.、，。？！ ]{2,})", func_middle, text)  # 连续标点个数为1的不处理

        ## 后标点
        def func_end(match):
            puns = match.group(1).replace(" ", '')
            if len(puns) == 1:  # 标点数据正确
                if puns in "？！":
                    return puns
                else:
                    return "。"
            else:  # 标点数量不正确
                return "。"

        if text.endswith('？') or text.endswith('！'):
            pass
        else:
            text += '。'

        text = re.sub(r"([,.、，。？！ ]+)$", func_end, text)
        return text

    def pause_char_normalize_EN(self, text):
        """
        纯英文停顿标点正则：
        :param text: (str)
        :return: (str)
        """

        # 停顿标点与语言统一
        """？！"""  # 因为中文、，。替换为英文的,,.会产生歧义，所以不替换
        text = text.replace("？", "? ").replace("！", '! ').strip()

        # 停顿标点去重
        text = re.sub(r"([,.?!、，。 ])\1+", r'\1', text)

        # 停顿标点消歧
        ## 前标点
        text = re.sub(r"^([,.?!、，。 ]*)", '', text)

        # # 中间标点
        def func_middle(match):
            puns = match.group(1)
            if puns.startswith(' '):
                return "%s " % puns[1]
            elif puns[0] in ',.?!':
                return "%s " % puns[0]
            else:
                return puns[0]

        text = re.sub(r"([,.?!、，。 ]{2,})", func_middle, text)  # 连续标点个数为1的不处理

        ## 后标点
        def func_end(match):
            puns = match.group(1).replace(" ", '')
            if len(puns) == 1:  # 标点数据正确
                if puns in "?!":
                    return puns
                else:
                    return "."
            else:  # 标点数量不正确
                return "."

        if text.endswith('?') or text.endswith('!'):
            pass
        else:
            text += '.'

        text = re.sub(r"([,.?!、，。 ]+)$", func_end, text)
        return text

    def call(self, text, language_id):
        """
        :param text: (str) 用户输入文本
        :param language_id: (str) 语言类型标记 in ["CN", "EN", "CN_EN"]
        :return: (str) 若无有效字符，返回空字符串
        """

        # 替换[不支持的]字符
        app_logger.debug("替换不支持的字符 [输入]: %s" % text)
        text = self.replace_unsupported_char(text)
        app_logger.debug("替换不支持的字符 [输出]: %s" % text)

        # 检查是否包含有效字符
        if not re.findall(r"[0-9A-Za-z\u4e00-\u9fa5]", text):  # 不含有有效字符
            app_logger.info("输入字符串为空")
            return ""
        else:  # 含有有效字符
            # 停顿标点正则
            if language_id == "CN":
                # 映射[支持的]字符到有限多个标点
                text = self.mapping_supported_char(text)
                text = self.pause_char_normalize_CN(text)
            elif language_id == "CN_EN":
                # 映射[支持的]字符到有限多个标点
                text = self.mapping_supported_char(text)
                text = self.pause_char_normalize_CN_EN(text)
            elif language_id == "EN":

                text = self.pause_char_normalize_EN(text)

        return text


if __name__ == '__main__':
    pn = CharNormalize()
    text = "Visitors at the booth of Huawei during the China International Fair for Trade in Services in Beijing in September. [ZHAN MIN/FOR CHINA DAILY]"
    print(text)
    print(pn.call(text, "EN"))
