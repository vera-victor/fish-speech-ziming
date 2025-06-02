# -*- coding: utf-8 -*-
# Create Time: 2020/9/30 上午11:27
# Author: Allen

import os
import re
import requests
import json

from tools.text_norm.log.log_helper import app_logger

from tools.text_norm.front_end.normalize.char_normalize import CharNormalize
from tools.text_norm.front_end.normalize.text_normalize import TextNormalize


class TTSFrontEnd(object):
    def __init__(self, language_id):
        """
        Args:
            language_id: (str) in ["CN", "EN", "CN_EN"]
            coding_id: (str) in ["cnen", "cn", "hk"]
        """
        language_id = language_id.upper()
        if language_id not in ["CN", "EN", "CN_EN"]:
            language_id = "CN"
        app_logger.debug("语言类型 %s" % language_id)
        self.language_id = language_id
        # self.coding_id = coding_id

        self.char_norm = CharNormalize()

        self.text_norm = TextNormalize()

    @staticmethod
    def split_sentence(text):
        """
        中英文分句
        :param text: (str)
        :return: (list)
        """
        # 分句逻辑中不使用.，分句的.在之前已经被替换成。
        sentences = [s.strip() for s in re.split(r"(.*?[，,：。？！?!])", text) if s != '' and s is not None]

        return sentences
    @staticmethod
    def prepare_for_EN(text):
        """
        语言类型为EN时：删除所有中文字符

        :param text: (str)
        :return: (str) 包含：英文小写单词+[英文大写字母]+[数字]+[自定义标识符]
        """
        # 删除所有中文标识符
        text = re.sub(r"[\u4e00-\u9fa5]", '', text)

        # text = re.sub(r"<.*?>", "", text)  # 不支持<>自定义标识符
        # text = re.sub(r"\(.*?\)", "", text)
        text = re.sub(r"{.*?}", "", text)  # 不支持{}自定标识符

        # 中文停顿标点替换为英文标点
        mapping = {'，': ', ', '、': ', '}
        for k, v in mapping.items():
            text = text.replace(k, v)

        # 处理空格
        # text = text.strip()  # 处理前后空格
        # text = re.sub(r" +", ' ', text)  # 处理中间多余空格

        return text

    @staticmethod
    def prepare_for_CN(text):
        """
        语言类型为CN时：将英文字母变大写
        :param text: (str)
        :return: (str) 包含：中文字符+[英文大写字母]+[数字]+[自定义标识符]
        """
        text = text.upper()

        def func(match):
            mark = match.group(1)
            return mark.lower()

        text = re.sub(r"(<[A-Z]+\d>)", func, text)  # 将拼音标识符恢复成小写

        return text

    @staticmethod
    def prepare_for_CN_EN(text):
        """
        语言类型为CN_EN时：
        :param text: (str)
        :return: (str) 包含：中文字符+英文小写单词+[英文大写字母]+[数字]+[自定义标识符]
        """

        # 将独立出现的英文小写字母变大写
        def func(match):
            word = match.group(1)
            return word.upper()

        text = re.sub(
            r"((?<![a-zA-Z\'0-9 ])[a-z](?![a-zA-Z\'0-9 ])|^[a-z](?![a-zA-Z\'0-9 ])|(?<![a-zA-Z\'0-9 ])[a-z]$)", func,
            text)

        # 将拼音标识符恢复成小写
        def pinyin_func(match):
            mark = match.group(1)
            return mark.lower()

        text = re.sub(r"(<[A-Z]+\d>)", pinyin_func, text)
        # print('prepare_for_CN_EN',text)
        return text

    def process_num_puns(self, text):
        """
        将数字中间的.保留，其余的.转换成。
        :param text: (str)
        :return: (str)
        """

        def func_uppercase_point(match):
            words = match.group(1)
            words = ' '.join(list(words.replace('.', '')))
            return words

        punc = text[-1]  # 保留最右边的.
        # 处理大写字母间的. 'U.S.' => 'U S'
        text = re.sub(r"((?:[A-Z]\.){2,})", func_uppercase_point, text)
        if not text.endswith(punc):
            text += punc

        def func_num_point(match):
            pun = match.group(1)
            left_str = text[:match.span()[0]]
            right_str = text[match.span()[1]:]
            if len(left_str) > 0 and len(right_str) > 0:
                if left_str[-1].isdigit() and right_str[0].isdigit():
                    return '.'
                elif left_str[-1].isalpha() and right_str[0].isalpha():  # 如果.两边都是字母，很可能是邮箱网站之类的点。
                    return '.'
                else:
                    return '。'
            else:
                return pun

        # 处理数字间的.
        text = re.sub(r"(\.)", func_num_point, text)

        return text

    def call(self, text):
        """
        该部分主要是标点处理与分句
        :param text: (str) 用户输入任意文本
        :param language_id: (str) 语言类型标记 in ["CN", "EN", "CN_EN"]
        :return: (list) 若无有效字符，返回空列表
        """
        # headers = {'content-type': 'application/json'}
        # REQ_TIMEOUT = 2000
        # 语言类型检查
        language_id = self.language_id.upper()
        if language_id not in ["CN", "EN", "CN_EN"]:
            language_id = "CN"
        app_logger.debug("语言类型 %s" % language_id)

        # zimu_dict = {'b':'bi4','c':'sei1','d':'di4','e':'iii4','f':'aaai2fu5','g':'ji4','h':'aaai2qu5','i':'aaai4','j':'jie4','k':'kei1','l':'aaai2eeer2','m':'aaai2mu5','n':'eeen1','o':'ooo1','p':'pi4','q':'ke5iiiu1','r':'aaa1','s':'aaai4siy5','t':'ti4','u':'iiiu1','v':'uuui1','w':'da2bu5liu1','x':'aaai2ke5siy5','y':'uuuai1','z':'zei1',}
        # 字符/标点正则
        text = self.char_norm.call(text, language_id)
        app_logger.debug("字符/标点正则 [输出]： %s" % text)

        if text == "":  # 无效字符串
            app_logger.error("无效字符串")
            return [], []

        # 数字中的点.处理，将不是数字中间的.处理成中文标点。

        text = self.process_num_puns(text)
        app_logger.debug("数字中的点.处理 [输出] %s" % text)
        text = text.replace(':',',')
        # 分句
        sentences = self.split_sentence(text)
        app_logger.debug("分句 [输出]： %s" % sentences)
        # print('sentences',sentences)
        sentences_list = []
        for sentence in sentences:
            # end_punc = sentence[-1]  # TODO 记录末端标点，未来用于情感TTS

            # 语言类型预处理(约束文本正则的输入)
            if language_id == "CN":
                sentence = self.prepare_for_CN(sentence[:-1])
            elif language_id == "EN":
                sentence = self.prepare_for_EN(sentence[:-1])
            elif language_id == 'CN_EN':
                sentence = self.prepare_for_CN_EN(sentence[:-1])
            # print(sentence)
            app_logger.debug("语言类型预处理(约束文本正则的输入) [输出]： %s" % sentence)
            text = self.text_norm.call(sentence, pure_number_language_type=language_id)  # 句末标点不输入，方便最后一位有效字符的处理
            print(text)

            space_patten = re.compile(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])')
            text = space_patten.sub(r'\1\2', text.replace('、', '').strip())
            #print(text)
            # # Hey Jane, 周末 要不要一起吃早茶，叫上Jennie。
            # x = space_patten.sub(r'\1\2', x)
            # print(x)
            # Hey Jane, 周末要不要一起吃早茶，叫上Jennie。

            # sentences_list.append(re.sub('\W','',text.replace('、', '').replace(' ', '')))
            sentences_list.append(text)
        # print(sentences_list)
        return sentences_list


if __name__ == '__main__':
    tn = TTSFrontEnd('CN_EN')
    text = '我一生创作了众多重要作品电话17601549896，以下是几部代表作的简要介绍1第五交响曲命运交响曲创作于1804-1808年，象征着命运的力量与斗争精神。2第九交响曲合唱交响曲创作于1822-1824年，以“欢乐颂”著称，是首个将合唱引入交响曲的作品。3.月光奏鸣曲创作于1801年，原名升c小调第十四钢琴奏鸣曲，以其浪漫和深情的旋律著称。4.英雄交响曲创作于1803-1804年，原本献给拿破仑，后来改为献给“纪念一位伟人的追思”。5.费德里奥这是我唯一的歌剧，讲述了一位妻子为营救被不公囚禁的丈夫而化装成男子的故事。6致爱丽丝创作于1810年，是一首小型钢琴作品，旋律优美，广为流传。这些作品展示了我在交响曲、钢琴奏鸣曲和歌剧等领域的创新和成就。如果你对其中某一部作品有特别兴趣，请告诉我，我可以进一步详细介绍。'
    tn.call(text)
