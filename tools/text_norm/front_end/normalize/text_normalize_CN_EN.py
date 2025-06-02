# -*- coding: utf-8 -*-
# Create Time: 2020/9/30 上午11:56
# Author: Allen
import os
import re
import string
import json
from tools.text_norm.log.log_helper import app_logger
from tools.text_norm.front_end.normalize.mark_normalize_CN_EN import MarkNormalizeCNEN
from tools.text_norm.front_end.normalize.number_normalize import NumberNormalize
from tools.text_norm.front_end.normalize.text_normalize_CN import TextNormalizeCn
from tools.text_norm.front_end.normalize.text_normalize_EN import TextNormalizeEn
from tools.text_norm.front_end.utils.normalise.normalize_english import normalize_

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")


class TextNormalizeCnEn(object):
    """ 中英文文本正则
    输入：
        中文字符+英文小写单词+[英文大写字母]+[数字]+[自定义标识符]
    输出：
        正则化后的文本
    约定：
        英文字符部分不进行韵律预测
        数字按照位置进行转写：若在英文中间，转英文；否则转中文
    """

    def __init__(self):
        self.logger = app_logger
        unit_file = os.path.join(config_path, 'units.json')
        self.logger.debug("加载自定义 单位 [%s]" % unit_file)
        self.unit_dict = self.load_json2dict(unit_file)
        self.text_norm_cn = TextNormalizeCn()  # 处理中文+数字
        self.text_norm_en = TextNormalizeEn()  # 处理英文小写单词+数字
        self.num_norm = NumberNormalize()
        self.mark_norm_cn_en = MarkNormalizeCNEN()  # 标识符解析
        self.uppercase_letter_half_to_full_mapping = {
            'Ａ': 'A',  # 全角大写字母
            'Ｂ': 'B',
            'Ｃ': 'C',
            'Ｄ': 'D',
            'Ｅ': 'E',
            'Ｆ': 'F',
            'Ｇ': 'G',
            'Ｈ': 'H',
            'Ｉ': 'I',
            'Ｊ': 'J',
            'Ｋ': 'K',
            'Ｌ': 'L',
            'Ｍ': 'M',
            'Ｎ': 'N',
            'Ｏ': 'O',
            'Ｐ': 'P',
            'Ｑ': 'Q',
            'Ｒ': 'R',
            'Ｓ': 'S',
            'Ｔ': 'T',
            'Ｕ': 'U',
            'Ｖ': 'V',
            'Ｗ': 'W',
            'Ｘ': 'X',
            'Ｙ': 'Y',
            'Ｚ': 'Z'
        }

    @staticmethod
    def load_json2dict(json_path):
        with open(json_path, "r") as rf:
            data = json.load(rf)
        return data

    def half_to_full(self, text):
        """
        半角字母转全角
        :param text:
        :return:
        """
        mapping_ord = {ord(v): k for k, v in self.uppercase_letter_half_to_full_mapping.items()}
        res_text = text.translate(mapping_ord)
        return res_text

    def full_to_half(self, text):
        """
        全角字母转半角
        :param text:
        :return:
        """
        mapping_ord = {ord(k): v for k, v in self.uppercase_letter_half_to_full_mapping.items()}
        res_text = text.translate(mapping_ord)
        return res_text

    def is_start_with_english_char(self, text):
        """判断文本是以英文()开头的"""
        text = text.lstrip()
        text = re.sub(r"《.*?》", '', text)
        text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z\'%s]" % ''.join(self.uppercase_letter_half_to_full_mapping.keys()), '',
                      text)

        if len(text) > 0 and text[0] in string.ascii_letters + ''.join(
                self.uppercase_letter_half_to_full_mapping.keys()):
            return True
        else:
            return False

    def is_end_with_english_char(self, text):
        """判断文本是以英文()结尾的"""
        text = text.rstrip()
        text = re.sub(r"《.*?》", '', text)
        text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z\'%s]" % ''.join(self.uppercase_letter_half_to_full_mapping.keys()), '',
                      text)

        if len(text) > 0 and text[-1] in string.ascii_letters + ''.join(
                self.uppercase_letter_half_to_full_mapping.keys()):
            return True
        else:
            return False

    def is_use_english(self, left_str, right_str):
        if left_str == '' and right_str == '':
            return False
        elif left_str == '' and right_str != '':
            if self.is_start_with_english_char(right_str):
                return True
            else:
                return False
        elif left_str != '' and right_str == '':
            if self.is_end_with_english_char(left_str):
                return True
            else:
                return False
        elif left_str != '' and right_str != '':
            if self.is_end_with_english_char(left_str) and self.is_start_with_english_char(right_str):
                return True
            else:
                return False
        return False

    def split_uppercase_letter(self, text):
        """
        分离大写字母，并将大写字符转全角
        :param text: (str)
        :return: (str)
        """

        def func_middle(match):
            left_str = text[:match.span()[0]]
            right_str = text[match.span()[1]:]
            if left_str == '' and right_str == '':
                return ' '.join(list(self.half_to_full(match.group(1))))
            elif left_str == '' and right_str != '':
                if right_str[0] not in string.ascii_lowercase:
                    return '%s ' % ' '.join(list(self.half_to_full(match.group(1))))
                else:
                    return match.group(1)
            elif left_str != '' and right_str == '':
                if left_str[-1] not in string.ascii_lowercase:
                    return ' %s' % ' '.join(list(self.half_to_full(match.group(1))))
                else:
                    return match.group(1)
            elif left_str != '' and right_str != '':
                if left_str[-1] not in string.ascii_lowercase and right_str[0] not in string.ascii_lowercase:
                    return ' %s ' % ' '.join(list(self.half_to_full(match.group(1))))
                else:
                    return match.group(1)

        text = re.sub(r"([A-Z]+)", func_middle, text)
        text = re.sub(r" +", ' ', text)

        return text

    def split_num_norm(self, text):
        # 以数字进行分割
        text_list = re.split(r"([0-9]+\.[0-9]+|[0-9]+)", text)
        text = ''

        for index, t in enumerate(text_list):
            if re.findall(r"^([0-9]+\.[0-9]+|[0-9]+)$", t):  # 如果为数字
                if index == 0:  # 数字出现在句子开头
                    if self.is_start_with_english_char(text_list[index + 1]):
                        text += self.num_norm.call(t, language='en', style="ordinal")
                    else:
                        text += self.num_norm.call(t, language='cn', style="ordinal")
                elif 0 < index < len(text_list) - 1:  # 数字出现句子中间
                    if self.is_end_with_english_char(text_list[index - 1]) and self.is_start_with_english_char(
                            text_list[index + 1]):
                        text += self.num_norm.call(t, language='en', style="ordinal")
                    else:
                        text += self.num_norm.call(t, language='cn', style="ordinal")
                elif index == len(text_list) - 1:  # 数字出现在句子结尾
                    if self.is_end_with_english_char(text_list[index - 1]):
                        text += self.num_norm.call(t, language='en', style="ordinal")
                    else:
                        text += self.num_norm.call(t, language='cn', style="ordinal")
            else:
                text += t

        return text

    def percent_sign_punc(self, text):
        """
        %(百分号)处理 或 ‰(千分号)处理
        :param text: (str)
        :return: (str)
        """

        # 处理 12%-13%或12%~13%
        def two_num_func(match):
            left_str = text[: match.span()[0]]
            right_str = text[match.span()[1]:]
            if self.is_use_english(left_str, right_str):
                num1 = self.num_norm.call(match.group(1), 'en', 'ordinal')
                num2 = self.num_norm.call(match.group(2), 'en', 'ordinal')
                return " %s percent ot %s percent" % (num1, num2)
            else:
                num1 = self.num_norm.call(match.group(1), 'cn', 'ordinal')
                num2 = self.num_norm.call(match.group(2), 'cn', 'ordinal')
                return "百分之%s至百分之%s" % (num1, num2)

        text = re.sub(r"([0-9]+\.[0-9]+|[0-9]+)%[-~]([0-9]+\.[0-9]+|[0-9]+)%", two_num_func, text)

        # 负数
        def hundred_negative_func(match):
            left_str = text[: match.span()[0]]
            right_str = text[match.span()[1]:]
            if self.is_use_english(left_str, right_str):
                num = match.group(1)
                if '.' in num:
                    num = self.num_norm.call(str(float(num)), 'en', 'ordinal')
                else:
                    num = self.num_norm.call(str(int(num)), 'en', 'ordinal')

                return "minus %s percent" % num
            else:
                num = match.group(1)
                if '.' in num:
                    num = self.num_norm.call(str(float(num)), 'cn', 'ordinal')
                else:
                    num = self.num_norm.call(str(int(num)), 'cn', 'ordinal')

                return "负百分之%s" % num

        text = re.sub(r"-([0-9]+\.[0-9]+|[0-9]+)%", hundred_negative_func, text)

        def thousand_negative_func(match):
            num = match.group(1)
            left_str = text[: match.span()[0]]
            right_str = text[match.span()[1]:]
            if self.is_use_english(left_str, right_str):
                if '.' in num:
                    num = self.num_norm.call(str(float(num)), 'en', 'ordinal')
                else:
                    num = self.num_norm.call(str(int(num)), 'en', 'ordinal')
                return "minus %s per thousand" % num
            else:
                if '.' in num:
                    num = self.num_norm.call(str(float(num)), 'cn', 'ordinal')
                else:
                    num = self.num_norm.call(str(int(num)), 'cn', 'ordinal')
                return "负千分之%s" % num

        text = re.sub(r"-([0-9]+\.[0-9]+|[0-9]+)‰", thousand_negative_func, text)

        # 正数
        def hundred_positive_func(match):
            num = match.group(1)
            left_str = text[: match.span()[0]]
            right_str = text[match.span()[1]:]
            if self.is_use_english(left_str, right_str):
                if '.' in num:
                    num = self.num_norm.call(str(float(num)), 'en', 'ordinal')
                else:
                    num = self.num_norm.call(str(int(num)), 'en', 'ordinal')
                return "%s percent" % num
            else:
                if '.' in num:
                    num = self.num_norm.call(str(float(num)), 'cn', 'ordinal')
                else:
                    num = self.num_norm.call(str(int(num)), 'cn', 'ordinal')
                return "百分之%s" % num

        text = re.sub(r"([0-9]+\.[0-9]+|[0-9]+)%", hundred_positive_func, text)

        def thousand_positive_func(match):
            num = match.group(1)
            left_str = text[: match.span()[0]]
            right_str = text[match.span()[1]:]
            if self.is_use_english(left_str, right_str):
                if '.' in num:
                    num = self.num_norm.call(str(float(num)), 'en', 'ordinal')
                else:
                    num = self.num_norm.call(str(int(num)), 'en', 'ordinal')
                return "%s per thousand" % num
            else:
                if '.' in num:
                    num = self.num_norm.call(str(float(num)), 'cn', 'ordinal')
                else:
                    num = self.num_norm.call(str(int(num)), 'cn', 'ordinal')
                return "千分之%s" % num

        text = re.sub(r"([0-9]+\.[0-9]+|[0-9]+)‰", thousand_positive_func, text)

        # 删除剩余的百分号
        text = text.replace('%', '').replace('‰', '')

        return text

    def wavy_punc(self, text):
        def func_wavy(match):
            """
            30~40 -> 三十只四十
            30~40 -> thirty to forty
            """
            match_str = match.group(1)

            left_str = text[: match.span()[0]]
            right_str = text[match.span()[1]:]

            if self.is_use_english(left_str, right_str):
                return match_str.replace('~', ' to ')
            else:
                return match_str.replace('~', '至')

        # TODO 反例 20~30~40
        text = re.sub(r"(([0-9]+\.[0-9]+|[0-9]+)+\~([0-9]+\.[0-9]+|[0-9]+))", func_wavy, text)
        return text

    def colon_punc(self, text):
        # 数字转换(符号在数字中间)
        def func_colon(match):
            """
            20:30 -> 二十比三十
            """
            match_str = match.group(1)

            left_str = text[: match.span()[0]]
            right_str = text[match.span()[1]:]

            if self.is_use_english(left_str, right_str):
                num1 = self.num_norm.call(match.group(2), 'en', 'ordinal')
                num2 = self.num_norm.call(match.group(3), 'en', 'ordinal')
                return " %s to %s " % (num1, num2)
            else:
                num1 = self.num_norm.call(match.group(2), 'cn', 'ordinal')
                num2 = self.num_norm.call(match.group(3), 'cn', 'ordinal')
                return "%s比%s" % (num1, num2)

        # TODO 反例 20:30:40
        text = re.sub(r"((\d+):(\d+))", func_colon, text)
        return text

    def slash_punc(self, text):
        """
        /(斜杠)处理
        约定：
            两个/按分数转换
            三个/按日期转化
            TODO 处理三个及以上斜杠
        :param text: (str)
        :return: (str)
        """

        # 两个斜杠
        def two_slash_func(match):
            # TODO 数字作为日期需要检查
            left_str = text[: match.span()[0]]
            right_str = text[match.span()[1]:]

            num1 = match.group(1)
            num2 = match.group(2)
            num3 = match.group(3)
            if len(num1) == 4 and 1 <= int(num2) <= 12 and 1 <= int(num3) <= 31:  # 判断为 年月日
                if self.is_use_english(left_str, right_str):
                    return normalize_("{}-{}-{}".format(match.group(1), match.group(2), match.group(3)))
                else:
                    num1 = self.num_norm.call(str(int(num1)), 'cn', 'bitwise')
                    num2 = self.num_norm.call(str(int(num2)), 'cn', 'ordinal')
                    num3 = self.num_norm.call(str(int(num3)), 'cn', 'ordinal')
                    return '%s年%s月%s日' % (num1, num2, num3)
            else:
                if self.is_use_english(left_str, right_str):
                    num1 = self.num_norm.call(str(int(num1)), 'en', 'ordinal')
                    num2 = self.num_norm.call(str(int(num2)), 'en', 'ordinal')
                    num3 = self.num_norm.call(str(int(num3)), 'en', 'ordinal')
                    return '%s %s %s' % (num1, num2, num3)
                else:
                    num1 = self.num_norm.call(str(int(num1)), 'cn', 'ordinal')
                    num2 = self.num_norm.call(str(int(num2)), 'cn', 'ordinal')
                    num3 = self.num_norm.call(str(int(num3)), 'cn', 'ordinal')
                    return '%s/%s/%s' % (num1, num2, num3)

        text = re.sub(r"([0-9]+)[/／]([0-9]+)[/／]([0-9]+)", two_slash_func, text)

        # 一个斜杠 负数
        def one_slash_negative_func(match):
            num1 = self.num_norm.call(str(int(match.group(1))), 'cn', 'ordinal')
            num2 = self.num_norm.call(str(int(match.group(2))), 'cn', 'ordinal')

            return '负%s分之%s' % (num2, num1)

        text = re.sub(r"-([0-9]+)[/／]([0-9]+)", one_slash_negative_func, text)

        # 一个斜杠 正数
        def one_slash_positive_func(match):

            if len(match.group(1)) == 4 and len(match.group(2)) == 4 and "赛季" in text:
                num1 = self.num_norm.call(match.group(1), 'cn', 'bitwise')
                num2 = self.num_norm.call(match.group(2), 'cn', 'bitwise')
                return "%s至%s" % (num1, num2)

            else:
                num1 = self.num_norm.call(str(int(match.group(1))), 'cn', 'ordinal')
                num2 = self.num_norm.call(str(int(match.group(2))), 'cn', 'ordinal')

                return '%s分之%s' % (num2, num1)

        text = re.sub(r"([0-9]+)[/／]([0-9]+)", one_slash_positive_func, text)

        def money_func(match):
            return '%s兑%s' % (match.group(1), match.group(2))

        text = re.sub(r"(英镑|欧元|瑞郎|美元|日元|人民币|港元|越南盾|瑞尔|泰铢|卢比|卢布|韩元|澳元|克朗|马克|荷兰盾|法郎|里拉|加元)[/／]"
                      r"(英镑|欧元|瑞郎|美元|日元|人民币|港元|越南盾|瑞尔|泰铢|卢比|卢布|韩元|澳元|克朗|马克|荷兰盾|法郎|里拉|加元)", money_func, text)

        def unit_func(match):
            return '%s每%s' % (match.group(1), match.group(2))

        text = re.sub(r"(元)[/／](吨|米|千克|克|斤|平米|平方米)", unit_func, text)

        # 删除剩余斜杠
        # text = text.replace('/', '，').replace("／", "，")

        return text

    def hyphen_punc(self, text):
        def func_horizontal(match):
            """2015-12-1 -> 二零一五年十二月一日"""

            left_str = text[: match.span()[0]]
            right_str = text[match.span()[1]:]

            if self.is_use_english(left_str, right_str):
                return normalize_(match.group())
            else:
                y = self.num_norm.call(match.group(2), 'cn', 'bitwise')
                m = self.num_norm.call(match.group(3), 'cn', 'ordinal')
                d = self.num_norm.call(match.group(4), 'cn', 'ordinal')
                return "%s年%s月%s日" % (y, m, d)

        text = re.sub(r"((\d{4})-(\d{1,2})-(\d{1,2}))", func_horizontal, text)

        def two_hyphen_func(match):
            left_str = text[: match.span()[0]]
            right_str = text[match.span()[1]:]
            num1 = match.group(1)
            num2 = match.group(2)
            if self.is_use_english(left_str, right_str):
                num1 = self.num_norm.call(num1, 'en', 'bitwise')
                num2 = self.num_norm.call(num2, 'en', 'bitwise')
                return "%s to %s" % (num1, num2)
            else:
                if len(num1) == 4 and len(num2) == 4 and "赛季" in text:
                    num1 = self.num_norm.call(num1, 'cn', 'bitwise')
                    num2 = self.num_norm.call(num2, 'cn', 'bitwise')
                    return "%s至%s" % (num1, num2)
                elif phone_flage:
                    num1 = self.num_norm.call(num1, 'cn', 'phone')
                    num2 = self.num_norm.call(num2, 'cn', 'phone')
                    return num1 + num2
                elif len(num1) == 4 and (len(num2) == 2 or len(num2) == 4):
                    num1 = self.num_norm.call(num1, 'cn', 'bitwise')
                    num2 = self.num_norm.call(num2, 'cn', 'bitwise')
                    return "%s至%s" % (num1, num2)
                elif score_flage:
                    num1 = self.num_norm.call(str(int(num1)), 'cn', 'ordinal')
                    num2 = self.num_norm.call(str(int(num2)), 'cn', 'ordinal')
                    return "%s比%s" % (num1, num2)
                else:
                    num1 = self.num_norm.call(str(int(num1)), 'cn', 'ordinal')
                    num2 = self.num_norm.call(str(int(num2)), 'cn', 'ordinal')
                    return "%s至%s" % (num1, num2)

        score_flage = False
        if re.findall(r"比分|分数|战胜|领先|击败|险胜|不敌|轻取|女排|男排|篮球|主场|客场|决赛|比赛|冠军|输|赢", text):  # TODO添加更多的关键词
            score_flage = True

        phone_flage = False
        if re.findall(r"固话|手机|号码|电话", text):  #
            phone_flage = True

        text = re.sub(r"([0-9]+)[-—]([0-9]+)", two_hyphen_func, text)

        return text

    def unit_punc(self, text):
        """
        单位符号(符号在数字前后)
        :param text:
        :return:
        """
        def func_unit_quantifier(match):
            left_str = text[: match.span()[0]]
            right_str = text[match.span()[1]:]

            if self.is_use_english(left_str, right_str):
                num = self.num_norm.call(match.group(1), 'en', 'ordinal')
                quan = match.group(2)
                real_quan = self.unit_dict.get(quan, {}).get("en")
                if real_quan:
                    return "%s %s" % (num, real_quan)
            else:
                num = self.num_norm.call(match.group(1), 'cn', 'ordinal')
                quan = match.group(2)
                real_quan = self.unit_dict.get(quan, {}).get("cn")
                if real_quan:
                    return num + real_quan

        units = [unit.replace("/", "\\/") for unit, _ in self.unit_dict.items()]
        units = sorted(units, key=lambda x: len(x), reverse=True)
        regex = "(?:^|(?<=[ \u4e00-\u9fa5,，、》]))([0-9]+\.[0-9]+|[0-9]+)(" + "|".join(units) \
                + ")(?:(?=[ \u4e00-\u9fa5,，、《])|$)"
        text = re.sub(regex, func_unit_quantifier, text)
        return text

    def year_punc(self, text):
        """
        数字搭配年处理
        :param text: (str)
        :return: (str)
        """
        def spec_year_func1(match):
            y = self.num_norm.call(match.group(1), 'cn', 'ordinal')
            return "近%s年" % y

        text = re.sub(r"近(\d+)年", spec_year_func1, text)

        def spec_year_func2(match):
            y = self.num_norm.call(match.group(1), 'cn', 'ordinal')
            return "%s年%s" % (y, match.group(2))

        text = re.sub(r"(\d+)年((以?来)|(之?以?前)|(之?以?后))", spec_year_func2, text)

        # def year_func(match):
        #     """10年 -> 一零年"""
        #     y = self.num_norm.call(match.group(1), 'cn', 'bitwise')
        #     return "%s年" % y
        #
        # text = re.sub(r"([1-3]\d{3}|(([0-2][1-9])|([1-2]\d)))年", year_func, text)

        return text

    def puns_num_transfer(self, text):
        """
        处理默认数字(无自定义标识符的数字)  # TODO 添加 :解析
        :param text: (str)
        :return: (str)
        """

        # 处理数字间的英文逗号,
        text = re.sub(r"(?<=\d),(?=\d)", '', text)
        self.logger.debug("处理数字间的英文逗号 [输出]: %s" % text)

        text = self.colon_punc(text)
        self.logger.debug("处理冒号 [输出]: %s" % text)

        # 处理斜杠
        text = self.slash_punc(text)
        app_logger.debug("处理斜杠 [输出]: %s" % text)

        # 处理百分号、千分号
        text = self.percent_sign_punc(text)
        app_logger.debug("处理百分号、千分号 [输出]: %s" % text)

        text = self.wavy_punc(text)
        self.logger.debug("处理波浪号 [输出]: %s" % text)

        text = self.hyphen_punc(text)
        self.logger.debug("处理短横 [输出]: %s" % text)

        # 数字转换(符号在数字前后)
        text = self.unit_punc(text)
        self.logger.debug("处理单位符号 [输出]: %s" % text)

        text = self.year_punc(text)
        self.logger.debug("处理年 [输出]: %s" % text)

        # 删除没有搭配数字的符号
        text = re.sub(r"[￥%~:：]", '', text)

        return text

    def call(self, text):
        """
        :param text: (str)
        :return: (str) 正则化后的文本
        """
        # 标识符解析
        text = self.mark_norm_cn_en.call(text)
        self.logger.debug("标识符解析 [输出]: %s" % text)

        # 单引号处理
        text = text.replace(' \'', ' ').replace('\' ', ' ')
        self.logger.debug("单引号处理 [输出]: %s" % text)

        # 搭配标点的数字转换
        text = self.puns_num_transfer(text)
        self.logger.debug("搭配标点的数字转换 [输出]: %s" % text)
        # print(text)
        # 连续大写字母分割
        text = self.split_uppercase_letter(text)
        self.logger.debug("连续大写字母分割 [输出]: %s" % text)

        # 空格替换
        text = re.sub(r"(?<=[\u4e00-\u9fa5]) (?=[\u4e00-\u9fa5])", '', text)  # 删除中文间
        text = re.sub(r"(?<=[0-9]) (?=[\u4e00-\u9fa5])", '', text)  # 删除数字与中文间的空格
        text = re.sub(r"(?<=[\u4e00-\u9fa5]) (?=[0-9])", '', text)  # 删除中文间与数字的空格
        self.logger.debug("空格替换 [输出]: %s" % text)

        # 英文单引号删除
        text = text.replace("'", "")
        self.logger.debug("英文单引号删除 [输出]: %s" % text)


        # 以数字进行分割
        text_list = re.split(r"([0-9]+\.[0-9]+|[0-9]+|-[0-9]+\.[0-9]+|-[0-9]+)", text)
        text = ''

        for index, t in enumerate(text_list): # ^[+-]?(0|([1-9]\d*))(\.\d+)?$/
            if re.findall(r"^([0-9]+\.[0-9]+|[0-9]+|-[0-9]+\.[0-9]+|-[0-9]+)$", t):  # 如果为数字
                if index == 0:  # 数字出现在句子开头
                    if self.is_start_with_english_char(text_list[index + 1]):
                        text += self.num_norm.call(t, language='en', style="ordinal") + ' '
                    else:
                        text += self.num_norm.call(t, language='cn', style="ordinal")
                elif 0 < index < len(text_list) - 1:  # 数字出现句子中间
                    if self.is_end_with_english_char(text_list[index - 1]) and self.is_start_with_english_char(
                            text_list[index + 1]):
                        text += ' ' + self.num_norm.call(t, language='en', style="ordinal") + ' '
                    else:
                        text += self.num_norm.call(t, language='cn', style="ordinal")
                elif index == len(text_list) - 1:  # 数字出现在句子结尾
                    if self.is_end_with_english_char(text_list[index - 1]):
                        text += ' ' + self.num_norm.call(t, language='en', style="ordinal")
                    else:
                        text += self.num_norm.call(t, language='cn', style="ordinal")
            else:
                text += t

        # 大小全角转半角
        sentences = [x for x in re.split(r"([%s]+)" % ''.join(self.uppercase_letter_half_to_full_mapping.keys()), text)
                     if x != '']  # 全角半角分割
        text = ''
        for sentence in sentences:
            if re.findall(r"^[%s]+$" % ''.join(self.uppercase_letter_half_to_full_mapping.keys()), sentence):
                text += ' %s ' % ' '.join(self.full_to_half(sentence).upper())
            else:
                text += sentence.lower()
        self.logger.debug("大小全角半角 [输出]: %s" % text)

        # 添加标点间空格
        text = re.sub(r"([、,.?!，。？！])", r" \1 ", text)
        text = text.strip()
        text = re.sub(r" +", " ", text)

        return text


if __name__ == '__main__':
    tn = TextNormalizeCnEn()
    text = '20:30 hello'
    print(tn.call(text))
