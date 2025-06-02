# -*- coding: utf-8 -*-
# Create Time: 2020/9/30 上午11:27
# Author: Allen

import os
import re

from service.modules.log.log_helper import app_logger

from service.modules.preprocess.front_end.normalize.char_normalize import CharNormalize
from service.modules.preprocess.front_end.normalize.text_normalize import TextNormalize
from service.modules.preprocess.front_end.prosody_predict.ProsodyPredict import ProsodyPredicting
from service.modules.preprocess.front_end.utils.custom_data_structure_list import CustomDataStructureList
from service.modules.preprocess.front_end.utils.grapheme_to_phoneme import GraphemeToPhonemeCNEN


class FrontEnd(object):
    def __init__(self, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = app_logger

        self.char_norm = CharNormalize()

        self.text_norm = TextNormalize()

        pwd = os.path.dirname(os.path.abspath(__file__))
        englist_pb_path = os.path.join(pwd, "prosody_predict/model/EnglishProsody.pb")
        chinese_pb_path = os.path.join(pwd, "prosody_predict/model/ChineseProsody.pb")
        config_path = os.path.join(pwd, "prosody_predict/config")

        self.prosody_predict = ProsodyPredicting(english_pb_path=englist_pb_path,
                                                 chinese_pb_path=chinese_pb_path,
                                                 config_path=config_path)

        self.cdsl = CustomDataStructureList()
        self.g2p = GraphemeToPhonemeCNEN()

    @staticmethod
    def split_sentence(text):
        """
        中英文分句
        :param text: (str)
        :return: (list)
        """
        # 分句逻辑中不使用.，分句的.在之前已经被替换成。
        sentences = [s.strip() for s in re.split(r"(.*?[。？！?!])", text) if s != '' and s is not None]

        return sentences

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
    def prepare_for_EN(text):
        """
        语言类型为EN时：删除所有中文字符

        :param text: (str)
        :return: (str) 包含：英文小写单词+[英文大写字母]+[数字]+[自定义标识符]
        """
        # 删除所有中文标识符
        text = re.sub(r"[\u4e00-\u9fa5]", '', text)

        text = re.sub(r"<.*?>", "", text)  # 不支持<>自定义标识符
        # text = re.sub(r"\(.*?\)", "", text)
        text = re.sub(r"{.*?}", "", text)  # 不支持{}自定标识符

        # 中文停顿标点替换为英文标点
        mapping = {'，': ', ', '、': ', '}
        for k, v in mapping.items():
            text = text.replace(k, v)

        # 处理空格
        text = text.strip()  # 处理前后空格
        text = re.sub(r" +", ' ', text)  # 处理中间多余空格

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
                else:
                    return '。'
            else:
                return pun

        # 处理数字间的.
        text = re.sub(r"(\.)", func_num_point, text)

        return text

    def call(self, text, language_id):
        """
        该部分主要是标点处理与分句
        :param text: (str) 用户输入任意文本
        :param language_id: (str) 语言类型标记 in ["CN", "EN", "CN_EN"]
        :return: (list) 若无有效字符，返回空列表
        """

        # 语言类型检查
        if language_id not in ["CN", "EN", "CN_EN"]:
            language_id = "CN"
        app_logger.debug("语言类型 %s" % language_id)

        # 字符/标点正则
        text = self.char_norm.call(text, language_id)
        app_logger.debug("字符/标点正则 [输出]： %s" % text)

        if text == "":  # 无效字符串
            app_logger.error("无效字符串")
            return []

        # 数字中的点.处理，将不是数字中间的额.处理成中文标点。
        text = self.process_num_puns(text)
        app_logger.debug("数字中的点.处理 [输出] %s" % text)

        # 分句
        sentences = self.split_sentence(text)
        app_logger.debug("分句 [输出]： %s" % sentences)

        phoneme_list = []

        for sentence in sentences:
            end_punc = sentence[-1]  # TODO 记录末端标点，未来用于情感TTS

            # 语言类型预处理(约束文本正则的输入)
            if language_id == "CN":
                sentence = self.prepare_for_CN(sentence[:-1])
            elif language_id == "EN":
                sentence = self.prepare_for_EN(sentence[:-1])
            elif language_id == 'CN_EN':
                sentence = self.prepare_for_CN_EN(sentence[:-1])
            app_logger.debug("语言类型预处理(约束文本正则的输入) [输出]： %s" % sentence)

            # 文本正则(功能独立，输入没有要求，lang只影响纯数字转写)
            text = self.text_norm.call(sentence, pure_number_language_type=language_id)  # 句末标点不输入，方便最后一位有效字符的处理
            phoneme_list.append(text)
            app_logger.debug("音素转换/韵律拼接 [输出] phoneme_list: {}".format(phoneme_list))

        return phoneme_list


if __name__ == '__main__':
    tn = FrontEnd()
    # print(tn.call("据英国《每日<ri1>邮报》10月6日报道hello！", 'CN_EN'))
    # print(tn.call("TTS font end 123456, test text。TTS font end 12,300 test text？TTS font end ,123456 test text！", 'EN'))
    # print(tn.call("TTS font end，test text。TTS font end，test text？TTS font end，test text！", 'EN'))
    # print(tn.call("TTS font end 123456. test text。TTS font end 12.300 test text？TTS font end .123456 test text！", 'EN'))
    # print(tn.call('"U.S. Decennial Census " U.S.', 'EN'))
    # print(tn.call("TTS font end ($123.001) test text<&100>.", 'EN'))
    # print(tn.call("Yan made the remarks during a panel discussion on 'Investment in Canada' organized during the Canada China Business Council's 42nd Annual General Meeting Business Forum held in Beijing.", 'EN'))
    # print(tn.call("Visitors at the booth of Huawei during the China International Fair for Trade in Services in Beijing in September. [ZHAN MIN/FOR CHINA DAILY]", 'EN'))
    # print(tn.call("Huawei is among the top 20 largest corporate investors in Canada and employs over 1,200 people there", 'EN'))
    # print(tn.call("HUAWEI Canada and employs over 1,200 people there", 'EN'))
    # print(tn.call("Huawei Canada and employs over 1,200 people THERE", 'EN'))
    # print(tn.call("Yan made the remarks during a panel discussion on 'Investment in Canada' organized during the Canada China Business Council's 42nd Annual General Meeting Business Forum held in Beijing", 'EN'))
    # print(tn.call("So far, China has 21 pilot free trade zones, located from south to north and from the country's coasts to its inland regions.", 'EN'))

    # print(tn.call("TTS测试￥12.5文本end！", 'CN_EN'))
    # print(tn.call("，，！，TTS前端文本测试文本hello。", 'CN_EN'))
    # print(tn.call("TTS前端，，！，文本测试文本hello。", 'CN_EN'))
    # print(tn.call("TTS前端文本测试文本hello，，！，", 'CN_EN'))
    # print(tn.call("，，！，TTS前端文hello，，！，本测试文本，，！，", 'CN_EN'))
    #
    # print(tn.call("TTS前端123,001文本测试文本hello.", 'CN_EN'))
    # print(tn.call("TTS前端123,文本测试文本hello.", 'CN_EN'))
    # print(tn.call("TTS前端,001文本测试文本hello.", 'CN_EN'))
    #
    # print(tn.call("TTS前端123.001文本测试文本hello.", 'CN_EN'))
    # print(tn.call("TTS前端123.文本测试文本hello.", 'CN_EN'))
    # print(tn.call("TTS前端.001文本测试文本hello.", 'CN_EN'))
    #
    # print(tn.call("<&200>TTS{前<qian2>端}($123.001)文<#1>本(@123.001)测试(#123.001)文本hello<&100>.", 'CN_EN'))
    # print(tn.call("2019年", 'CN_EN'))
    # print(tn.call("2019年 hello", 'CN_EN'))
    # print(tn.call("2019年,hello", 'CN_EN'))
    # print(tn.call("2019年，hello", 'CN_EN'))
    #
    # print(tn.call("2019-12-12hello2019年", 'CN_EN'))
    # print(tn.call("120Hz 你", 'CN_EN'))
    # print(tn.call("120Hz hello", 'CN_EN'))
    # print(tn.call("T1TNS测试文本，hello 2020, happy new year<&100>", 'CN_EN'))
    # print(tn.call("T1TNS测试文本<ben2>，hello 2020<#2>, happy new year", 'CN_EN'))
    # print(tn.call("据德国官方统计", 'CN_EN'))
    # print(tn.call("2019年20：30:10的比分", 'CN_EN'))
    # print(tn.call("2019年today20:30的比分", 'CN_EN'))

    # print(tn.call("120Hz 你。", 'CN_EN'))
    # print(tn.call("保留了hello,3.5km耳机孔。", 'CN_EN'))
    # print(tn.call("保留了hello 3.5m, hello耳机孔。", 'CN_EN'))
    # print(tn.call("保留了hello 3.5km， hello耳机孔。", 'CN_EN'))
    # print(tn.call("保留了3.5m， hello耳机孔。", 'CN_EN'))
    # print(tn.call("保留了3.5km, hello耳机孔。", 'CN_EN'))

    # print(tn.call("你哈， 23:01， 达到 25:1", 'CN'))
    # print(tn.call("你哈， 23:01:12， 达到 23:01:71", 'CN'))
    # print(tn.call("你哈， 23/01/12， 达到 23/01", 'CN'))
    # print(tn.call("你哈， ￥23.5， 达到 23.01‰", 'CN'))
    # print(tn.call("你哈， 23.5￥， 达到 23.01‰", 'CN'))
    # print(tn.call("2012年， 23.5%， 达到 23.01‰", 'CN'))
    # print(tn.call("202年， 23.5%， 达到 23.01‰", 'CN'))
    # print(tn.call("你哈， 23.5~13.7", 'CN'))
    #
    # print(tn.call("12°C， -12°C， 0.0°C， 0°C， 1.1°C， -1.1°C", 'CN'))
    # print(tn.call("12°C， -12°C， 0.0°C， 0°C， 1.1°C， -1.1°C °C", 'CN'))
    # print(tn.call("12°C， -12°C， 0.0°C， 0°C， 1.1°C， -1.1°C C", 'CN'))
    # print(tn.call("12°C， -12°C， 0.0°C， 0°C， 1.1°C， °-1.1°C", 'CN'))

    # print(tn.call("23.5%，23%，0.01‰，0.0%, -0%", 'CN'))
    # print(tn.call("TTS前端123,文本测试文本.", 'CN'))
    # print(tn.call("-23.5%，-23%，-0.01，-0.0， -0", 'CN'))
    # print(tn.call("-23.5，-23，-0.01，-0.0， -0-", 'CN'))
    # print(tn.call("2012-12-14，2222-14-41", 'CN'))
    # print(tn.call("2012/12/14，-14/41", 'CN'))
    # print(tn.call("12:12:14，13:12:14，12:12:-14，12:-12:14，-12:12:14", 'CN'))
    # print(tn.call("12:12.0:14，13:-12.0:14", 'CN'))
    # print(tn.call("12:12，25:12，12:-14，-12:12，-12:14.0", 'CN'))
    # print(tn.call("外加集成了153亿晶体管的5nm{单单单}。", 'CN_EN'))
    # print(tn.call("阿<a1>波罗", 'CN_EN'))
    # print(tn.call("阿<e1>胶", 'CN_EN'))
    # print(tn.call("哦<o4>好的", 'CN_EN'))
    # print(tn.call("你平时爱用iphone12手机，安卓手机，还是ipad平板呢？", 'CN_EN'))
    # print(tn.call("这是新款华为mate20 pro手机", 'CN_EN'))
    # print(tn.call("球鞋Air Jordan 1 Mid Fearless", 'CN_EN'))
    # print(tn.call("administrator@guiji.ai", 'CN_EN'))
    # print(tn.call("0", 'EN'))
    print(tn.call("<&2000>历史上有名的阿<a1>房女是真实存在的吗？<&2000>，{单玲玲}", 'CN'))
