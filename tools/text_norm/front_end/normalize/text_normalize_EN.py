# -*- coding: utf-8 -*-
# Create Time: 2020/9/30 上午11:55
# Author: Allen
import re
import string
from tools.text_norm.front_end.utils.normalise.normalize_english import normalize_
from tools.text_norm.log.log_helper import app_logger
from tools.text_norm.front_end.normalize.mark_normalize_EN import MarkNormalizeEN


class TextNormalizeEn(object):
    """ 英文文本正则
    输入：
        英文小写单词+[英文大写字母]+[数字]+[自定义标识符]
    输出：
        正则化后的文本
    """

    def __init__(self):
        self.logger = app_logger

        self.mark_norm_en = MarkNormalizeEN()  # 标识符解析

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

    def split_uppercase_letter(self, text):
        """
        分离大写字母，并将大写字符转全角
        :param text: (str)
        :return: (str)
        """

        def func_middle(match):
            left_str = text[:match.span()[0]]
            right_str = text[match.span()[1]:]
            # print(left_str,right_str)
            if left_str == '' and right_str == '':
                # return ' '.join(list(self.half_to_full(match.group(1))))
                return ' '.join(list(match.group(1)))
            elif left_str == '' and right_str != '':
                if right_str[0] not in string.ascii_lowercase:
                    return '%s ' % ' '.join(list(match.group(1)))
                    # return '%s ' % ' '.join(list(match.group(1)))
                else:
                    return match.group(1)
            elif left_str != '' and right_str == '':
                if left_str[-1] not in string.ascii_lowercase:
                    # return ' %s' % ' '.join(list(self.half_to_full(match.group(1))))
                    return ' %s' % ' '.join(list(match.group(1)))
                else:
                    return match.group(1)
            elif left_str != '' and right_str != '':
                if left_str[-1] not in string.ascii_lowercase and right_str[0] not in string.ascii_lowercase:
                    # return ' %s ' % ' '.join(list(self.half_to_full(match.group(1))))
                    return ' %s ' % ' '.join(list(match.group(1)))
                else:
                    return match.group(1)
        # print('#######',text)
        text = re.sub(r"([A-Z]+)", func_middle, text)
        # print('#######', text)
        text = re.sub(r" +", ' ', text)
        # print('#######', text)
        return text

    def puns_num_transfer(self, text):
        """
        处理默认数字(无自定义标识符的数字)
        :param text: (str)
        :return: (str)
        """
        # 处理数字间的,
        text = re.sub(r"(?<=\d),(?=\d)", '', text)

        # 数字转换(符号在数字中间)
        def func(match):
            match_str = match.group(1)
            return match_str.replace("~", " to ")

        text = re.sub(r"(([0-9]+\.[0-9]+|[0-9]+)+\~([0-9]+\.[0-9]+|[0-9]+))", func, text)

        # 处理~
        text = text.replace("~", ' ')

        return text

    def call(self, text):
        """
        :param text: (str)
        :return: (str) 正则化后的文本
        """
        # 标识符解析
        text = self.mark_norm_en.call(text)
        self.logger.debug("标识符解析 [输出]: %s" % text)
        # print("标识符解析 [输出]: %s" % text)
        # text = re.sub("[、 ]+", " ", text)
        # self.logger.debug("顿号处理 [输出]: %s" % text)

        # 单引号处理
        # text = text.replace(' \'', ' ').replace('\' ', ' ')
        # self.logger.debug("单引号处理 [输出]: %s" % text)

        # 单引号处理
        # text = text.replace(' \'', ' ').replace('\' ', ' ')
        # self.logger.debug("单引号处理 [输出]: %s" % text)

        # 搭配标点的数字转换
        text = self.puns_num_transfer(text)
        self.logger.debug("搭配标点的数字转换 [输出]: %s" % text)
        # print("搭配标点的数字转换 [输出]: %s" % text)
        # 连续大写字母分割
        text = self.split_uppercase_letter(text)
        self.logger.debug("连续大写字母分割 [输出]: %s" % text)
        # print("连续大写字母分割 [输出]: %s" % text)
        # 大小全角半角
        sentences = [x for x in re.split(r"([%s]+)" % ''.join(self.uppercase_letter_half_to_full_mapping.keys()), text)
                     if x != '']  # 全角半角分割
        self.logger.debug("大小全角半角 [输出]: %s" % sentences)

        # normalise正则
        text = ''
        for sentence in sentences:
            if re.findall(r"^[%s]+$" % ''.join(self.uppercase_letter_half_to_full_mapping.keys()), sentence):
                text += ' %s ' % ' '.join(self.full_to_half(sentence).upper())
                # print('#############',text)
            else:
                try:
                    # text_list = [x for x in re.split(r"(,|(?<!\d)\.(?!\d)| )", sentence) if x != '' and x != ' ']
                    # text += ' '.join(normalise(text_list, verbose=False)).lower()
                    # text += ' '.join(normalize_(sentence, verbose=False)).lower()
                    text += normalize_(sentence).lower()
                except:
                    text += " " + sentence
        self.logger.debug("normalise正则 [输出]: %s" % text)
        # print("normalise正则 [输出]: %s" % text)
        # 处理-
        text = text.replace('-', ' ').replace(':', ' ')
        # print('text',text)
        # 添加标点间空格
        text = re.sub(r"([、,.?!，。？！])", r" \1 ", text)
        text = text.strip()
        text = re.sub(r" +", " ", text)

        return text


if __name__ == '__main__':
    # tn = TextNormalizeEn()
    # # tn.call("2008 Tour with Madina Lake")
    # print(tn.call("currently available: British or American"))
    # print(tn.call("s NSW taxonomy, and create a more customisable system"))
    # print(tn.call("the normalisation of non-standard words (NSWs) in English."))
    # exit()
    tn = TextNormalizeEn()
    print(tn.call("Sri Lankawe Diya Eli ( 1st ed ."))
    # print(tn.call("the North Korean People’s Army"))
    # print(tn.call("school's"))
    # print(tn.call("She was named one of 2010's one hundred most influential people in the world by Time magazine ."))
    exit()
    before_file = open('/home/walter/data/tts_data/英文正则化/before_sentences.txt', 'r', encoding='utf-8')
    after_file = open('/home/walter/data/tts_data/英文正则化/after_sentences.txt', 'r', encoding='utf-8')
    before_lines = [line.strip() for line in before_file.readlines()]
    after_lines = [line.strip() for line in after_file.readlines()]
    assert len(before_lines) == len(after_lines)
    process_count = 2000
    count = 0
    of = open("/home/walter/data/tts_data/英文正则化/1111.txt", 'w', encoding='utf-8')
    for i in range(len(before_lines)):
        try:
            text = before_lines[i]
            before_result = tn.call(text)
            before_result = re.sub("[^\da-zA-Z\u4e00-\u9fa5]+", " ", before_result).strip().lower()
            after = re.sub("[^\da-zA-Z\u4e00-\u9fa5]+", " ", after_lines[i]).strip().lower()
            before_result = re.sub(" +", " ", before_result)
            after = re.sub(" +", " ", after)
            if before_result == after:
                count += 1
            else:
                of.write(text + "\t" + after + "\t" + before_result + "\n")
        except Exception as e:
            print(text)
    print("处理了{}条测试数据，正确的有{}条，准确率为：{}".format(process_count, count, count / process_count))
    exit()
    tn = TextNormalizeEn()
    # print(tn.call('-0.987654'))
    # print(normalize_(['administrator', 'at', 'guiji'], verbose=False))
    print(normalize_("administrator at guiji").lower())
