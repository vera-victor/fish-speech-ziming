# -*- coding: utf-8 -*-
# Create Time: 2020/9/30 下午2:00
# Author: Allen

import re

from tools.text_norm.log.log_helper import app_logger
from tools.text_norm.front_end.normalize.number_normalize import NumberNormalize
from tools.text_norm.front_end.utils.custom_data_structure import CustomDataStructure
from tools.text_norm.front_end.utils.name_map import mapping as name_mapping
from tools.text_norm.front_end.utils.pinyin_list import pinyin_list


class MarkNormalizeCNEN(object):
    """ CNEN自定义标识符正则 """

    def __init__(self):
        self.logger = app_logger
        self.num_norm = NumberNormalize()
        self.full_half_mapping = {
            '０': '0',  # 全角数字
            '１': '1',
            '２': '2',
            '３': '3',
            '４': '4',
            '５': '5',
            '６': '6',
            '７': '7',
            '８': '8',
            '９': '9',
            'ａ': 'a',  # 全角小写字母
            'ｂ': 'b',
            'ｃ': 'c',
            'ｄ': 'd',
            'ｅ': 'e',
            'ｆ': 'f',
            'ｇ': 'g',
            'ｈ': 'h',
            'ｉ': 'i',
            'ｊ': 'j',
            'ｋ': 'k',
            'ｌ': 'l',
            'ｍ': 'm',
            'ｎ': 'n',
            'ｏ': 'o',
            'ｐ': 'p',
            'ｑ': 'q',
            'ｒ': 'r',
            'ｓ': 's',
            'ｔ': 't',
            'ｕ': 'u',
            'ｖ': 'v',
            'ｗ': 'w',
            'ｘ': 'x',
            'ｙ': 'y',
            'ｚ': 'z',
            '《': '<',  # 标志符号
            '》': '>',
            '＃': '#',
            '＆': '&',
            '＠': '@',
            '￥': '$'
        }
        self.cds_before = CustomDataStructure()
        self.cds_after = CustomDataStructure()

    def is_start_with_english_char(self, text):
        """判断文本是以英文()开头的"""
        if re.findall(r"^[a-z\' ,%s]" % ''.join(self.full_half_mapping.keys()), text):
            return True
        else:
            return False

    def is_end_with_english_char(self, text):
        """判断文本是以英文()结尾的"""
        if re.findall(r"[a-z\' ,%s]$" % ''.join(self.full_half_mapping.keys()), text):
            return True
        else:
            return False

    @staticmethod
    def clean_repeat_mark(text):
        """
        将连续的标记符删除
        :param text: (str)
        :return: (str)
        """

        text = re.sub(r"(<#[0123]>)(<#[0123]>)+", r"\1", text)  # 同类型韵律标记符取第一个
        text = re.sub(r"(<&[0-9]+>)(<&[0-9]+>)+", r"\1", text)  # 同类型停顿标记符取第一个
        text = re.sub(r"(<[a-z]+[12345]>)(<[a-z]+[12345]>)+", r"\1", text)  # 同类型停顿时长标记符取第一个
        return text

    def mark_chars_half_to_full(self, text):
        """
        标识符字符(数字、小写字母、符号)半角转全角，举例：a -> ａ
        :param text: (str)
        :return: (str)
        """
        mapping_ord = {ord(v): k for k, v in self.full_half_mapping.items()}
        res_text = text.translate(mapping_ord)
        return res_text

    def mark_chars_full_to_half(self, text):
        """
        标识符字符(数字、小写字母、符号)全角转半角，举例：ａ -> a
        :param text: (str)
        :return: (str)
        """
        mapping_ord = {ord(k): v for k, v in self.full_half_mapping.items()}
        res_text = text.translate(mapping_ord)
        return res_text

    def split_uppercase_letter(self, text):
        """
        分类大写字母
        :param text: (str)
        :return: (str)
        """

        def func(match):
            words = match.group(1)
            words = ' '.join(list(words))
            return words

        text = re.sub(r"(.)([A-Z]+)(.)", func, text)
        return text

    def clean_marks(self, text):
        """
        标记符正则，删除错误组合的标记符
        :param text: (str)
        :return: (str)
        """

        # 处理停顿时长标记符
        text = self.clean_repeat_mark(text)

        def func(match):
            left_str = match.group(1)
            mark_str = match.group(2)
            right_str = match.group(3)
            if left_str in ',.?!，。？！' and right_str not in ',.?!，。？！':
                return match.group(0)
            elif left_str not in ',.?!，。？！' and right_str in ',.?!，。？！':
                return match.group(0)
            elif left_str in ',.?!，。？！' and right_str in ',.?!，。？！':
                return left_str
            elif left_str not in ',.?!，。？！' and right_str not in ',.?!，。？！':
                return left_str + mark_str + '，' + right_str

        text = re.sub(r"(.|^)(<&[0-9]+>)(.|$)", func, text)  # 中间的停顿时长标记符删除，保证停顿时长标记只可能出现在两边
        text = re.sub(r"([,.?!，。？！]|^)(<&[0-9]+>)([,.?!，。？！]|$)", func,
                      text)  # 处理只用停顿符的短句，比如：“你好，<&200>，请在下面输入框里输入您想要合成的内容”

        # 处理拼音标记符
        text = self.clean_repeat_mark(text)
        text = re.sub(r"(?<=[\u4e00-\u9fa5])(<#[0123]>)(<[a-z]+[1-5]>)", r"\2\1", text)  # 替换韵律标与拼音标记符，将拼音标符替换到前面
        text = self.clean_repeat_mark(text)
        text = re.sub(r"(?<![\u4e00-\u9fa5])<[a-z]+[12345]>", '', text)  # 前面不是中文的拼音标识符删除，保证所有拼音标记都正确处理

        # 处理韵律标记符
        text = self.clean_repeat_mark(text)
        text = re.sub(r"(^<&[0-9]+>)(<#[0123]>)+", r'\1', text)  # 前面不是中文或拼音标识符的韵律标识符删除
        text = self.clean_repeat_mark(text)
        text = re.sub(r"^<#[0123]>", '', text)  # 前面不是中文或拼音标识符的韵律标识符删除

        text = self.clean_repeat_mark(text)
        return text

    def parse_angle_brackets(self, text):
        """
        解析<>标识符，并转为全角标识符
        :param text: (str)
        :return: (str)
        """

        def func(match):
            """外部匹配为非贪婪匹配，不会出现<>嵌套的情况，若初选其他标识符嵌套则删除"""
            content = match.group(1)[1:-1]

            if re.findall(r"^#[0123]$", content):  # 判断为自定义韵律
                return self.mark_chars_half_to_full("<%s>" % content)
            elif re.findall(r"^&[0-9]+$", content):  # 判断为自定义停顿时长
                return self.mark_chars_half_to_full("<%s>" % content)
            elif re.findall(r"^[a-z]+[12345]$", content) and content in pinyin_list:  # 非判断为自定义拼音
                return self.mark_chars_half_to_full("<%s>" % content)
            else:
                return match.group(1)  # 匹配失败，直接返回

        text = re.sub(r"(<.*?>)", func, text)  # 非贪婪匹配
        return text

    def judge_lang(self, left_text, right_text):
        """
        判断前后字符串是否为英文字符
        :param left_text: (str)
        :param right_text: (str)
        :return: (str) in ['cn', 'en']
        """
        if left_text == '':
            if self.is_start_with_english_char(right_text):
                return 'en'
            else:
                return 'cn'
        elif right_text == '':
            if self.is_end_with_english_char(left_text):
                return 'en'
            else:
                return 'cn'
        elif self.is_end_with_english_char(left_text) and self.is_start_with_english_char(right_text):
            return 'en'
        else:
            return 'cn'

    def parse_round_brackets(self, text):
        """
        解析()标识符，进行数字转换
        :param text: (str)
        :return: (str)
        """

        def func(match):
            """外部匹配为非贪婪匹配，不会出现()嵌套的情况，若初选其他标识符嵌套则删除"""
            content = match.group(1)[1:-1]
            lang = self.judge_lang(left_text=text[: match.span()[0]],
                                   right_text=text[match.span()[1]:])

            # 匹配$
            if re.findall(r"^{mark}[0-9a-zA-Z]+\.[0-9a-zA-Z]*|{mark}[0-9a-zA-Z]+$".format(mark=re.escape('$')),
                          content):  # 优先匹配非负小数，避免对非负整数贪婪匹配
                if '.' in content:  # 判断为非负小数
                    num = str(content[1:])
                else:  # 判断为非负整数
                    num = str(content[1:])
                # print(self.num_norm.call(num, lang, "bitwise"))
                return self.num_norm.call(num, lang, "bitwise")  # 按位读法
            # 匹配@
            elif re.findall(r"^{mark}[0-9]+\.[0-9]*|{mark}[0-9]+$".format(mark=re.escape('@')),
                            content):  # 优先匹配非负小数，避免对非负整数贪婪匹配
                if '.' in content:  # 判断为非负小数
                    num = str(content[1:])
                else:  # 判断为非负整数
                    num = str(content[1:])
                return self.num_norm.call(num, lang, "ordinal")  # 2两读法
            # 匹配#
            elif re.findall(r"^{mark}[0-9]+\.[0-9]*|{mark}[0-9]+$".format(mark=re.escape('#')),
                            content):  # 优先匹配非负小数，避免对非负整数贪婪匹配
                if '.' in content:  # 判断为非负小数
                    num = str(content[1:])
                else:  # 判断为非负整数
                    num = str(content[1:])
                return self.num_norm.call(num, lang, "phone")  # 电话号码
            else:
                return match.group(1)  # 匹配失败，直接返回

        text = re.sub(r"(\(.*?\))", func, text)  # 非贪婪匹配
        return text

    def parse_curly_brackets(self, text):
        """
        解析{}标识符，将{}转写为自定义多音字标识符
        :param text:
        :return:
        """

        def func(match):
            """外部匹配为非贪婪匹配，不会出现{}嵌套的情况，只处理多音字<>嵌套"""
            content = self.mark_chars_full_to_half(match.group(1)[1:-1])
            content = re.sub(r"<&[0-9]+>", '', content)  # 删除自定义时长嵌套
            if re.findall(r"^[\u4e00-\u9fa5%s]+$" % ''.join(self.full_half_mapping.values()), content):  # 判断为纯中文

                self.cds_before.init(content, 'CN')

                clean_name = ''.join(self.cds_before.text_list)
                for k, v in name_mapping.items():
                    if k in clean_name:
                        clean_name = re.sub(r"^(%s)([\u4e00-\u9fa5]+)" % k, r"%s\2" % v, clean_name)  # 姓多音字展开

                # 实现{}内嵌套用户自定义拼音和韵律标记，并且姓名多音字也可指定拼音
                """
                                                 {单单单} -> 单<shan4><#0>单<#0>单<#0>
                                          {单<wang2>单单} -> 单<wang2><#0>单<#0>单<#0>
                            {单<wang2>单<wang2>单<wang2>} -> 单<wang2><#0>单<wang2><#0>单<wang2><#0>
                {单<wang2><#1>单<wang2><#2>单<wang2><#3>} -> 单<wang2><#1>单<wang2><#2>单<wang2><#3>
                """
                clean_name = re.sub(r"([\u4e00-\u9fa5])", r"\1<#0>", clean_name)  # 默认姓名字之间是没有韵律停顿
                clean_name = re.sub(r"(<#[0123]>)(<[a-z]+[1-5]>)", r"\2\1", clean_name)  # 替换韵律标与拼音标记
                self.cds_after.init(clean_name, 'CN')

                res = ""
                for index in range(len(self.cds_before.text_list)):
                    res += self.cds_before.text_list[index]

                    # 添加拼音标记
                    if self.cds_before.grapheme_list[index] != '':  # 优先使用用户自定义的拼音标记
                        res += self.mark_chars_half_to_full('<%s>' % self.cds_before.grapheme_list[index])
                    elif self.cds_after.grapheme_list[index] != '':
                        res += self.mark_chars_half_to_full('<%s>' % self.cds_after.grapheme_list[index])
                    else:
                        res += ""

                    # 添加停顿标记
                    if self.cds_before.prosody_list[index] != '':  # 优先使用用户自定义的韵律标记标记
                        res += self.mark_chars_half_to_full('<%s>' % self.cds_before.prosody_list[index])
                    elif self.cds_after.prosody_list[index] != '':
                        res += self.mark_chars_half_to_full('<%s>' % self.cds_after.prosody_list[index])
                    else:
                        res += ""

                return res
            else:
                return match.group(1)  # 匹配失败，直接返回

        text = re.sub(r"({.*?})", func, text)  # 非贪婪匹配
        return text

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

        text = re.sub(r"([,.?!、，。？！ ]+)$", "", text)
        return text

    def parse_brackets(self, text):
        """标识符解析，把正确的标识符解析出来，错误的标识符删掉"""

        text = self.parse_angle_brackets(text)  # 解析<>标识符，并替换为《》
        text = self.parse_round_brackets(text)  # 解析()标识符，并替换为（）
        text = self.parse_curly_brackets(text)  # 解析{}标识符，并删除{}
        text = re.sub("[<>(){}]+", '、', text)  # 删除非法标识符
        text = text.replace('@', ' at ').replace('&', ' and ').replace('#', ' , ')  # 替换剩余@、&、#
        text = self.pause_char_normalize_CN_EN(text)

        return text

    def call(self, text):
        """
        标记符正则，删除错误组合的标记符
        :param text: (str)
        :return: (str)
        """
        # 标记符正则，删除错误组合的标记符
        self.logger.info("CNEN 特殊标记符号处理，输入:%s"%text)
        text = self.clean_marks(text)
        self.logger.info("CNEN 特殊标记符号处理，clean_marks 输出:%s" % text)
        # self.logger.info("")
        # 标识符解析，解析正确的标识符，并转全角
        text = self.parse_brackets(text)
        self.logger.info("CNEN 特殊标记符号处理，括号解析 输出:%s"%text)
        return text


if __name__ == '__main__':
    mn = MarkNormalizeCNEN()
    text = "T1TNS测试文本<ben2>，hello 2020<#2>, happy ($3.14) new year"
    print(mn.call(text))
