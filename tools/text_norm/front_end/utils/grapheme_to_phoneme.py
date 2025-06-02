# -*- coding: utf-8 -*-
# Create Time: 2020/9/23 下午4:09
# Author: Allen
import re
import os
import io
from service.modules.config.config_helper import global_config
from service.modules.preprocess.front_end.utils.g2p_en import G2p
from service.modules.log.log_helper import app_logger
from service.modules.preprocess.front_end.utils.CN_EN_pinyin2phone import pinyin2phone_cnen


class GraphemeToPhonemeEN(object):
    def __init__(self):
        self.g2pen = G2p()

    def single_word_to_phone(self, word):
        """
        单个英文字母映射成音素
        :param word:
        :return:
        """
        phones = "".join(self.g2pen(word))
        phones = phones.replace('0', '6').replace('1', '7').replace('2', '8')
        return phones

    def single_pingyin_to_phone(self, pinyin):
        """
        单个拼音映射成音素
        :param pinyin:
        :return:
        """
        phone = pinyin2phone_cnen.get(pinyin, '')
        return phone

    def call(self, cds):
        if cds.language_flag[0] == 1:  # cn
            text = '-'
        elif cds.language_flag[0] == 0:  # en
            text = '-'
        else:
            text = ''

        # print("***", cds.grapheme_list, cds.language_flag, cds.prosody_list)

        for grapheme, language, prosody in zip(cds.grapheme_list, cds.language_flag, cds.prosody_list):
            phone = self.single_word_to_phone(grapheme)
            if language == 1:
                text += phone + prosody
            elif language == 0:
                text += phone + prosody
            elif language == ',':
                text += '#3'
            elif language == '.':
                text += '#4'
            else:
                pass

        def func(match):
            num1 = match.group(1)
            num2 = match.group(2)

            return '#%s' % str(num1) if num1 >= num2 else '#%s' % str(num2)

        text = re.sub(r"#(\d) ?#(\d)", func, text)  # 韵律去重
        app_logger.debug("韵律替换前的结果: %s" % text)
        text = text.replace('#0', '').replace('#1', '').replace('#2', '').replace('#3', ',').replace('#4', '.')
        text = re.sub(r"[%#,.]+$", '', text)  # 消除结尾韵律

        return text + '.'


class GraphemeToPhonemeCNEN(object):
    def __init__(self):
        self.g2pen = G2p()

    def single_word_to_phone(self, word):
        """
        单个英文字母映射成音素
        :param word:
        :return:
        """
        phones = "".join(self.g2pen(word))
        phones = phones.replace('0', '6').replace('1', '7').replace('2', '8')
        return phones

    def single_pingyin_to_phone(self, pinyin):
        """
        单个拼音映射成音素
        :param pinyin:
        :return:
        """
        phone = pinyin2phone_cnen.get(pinyin, '')
        return phone

    def call(self, cds):
        """
        :param grapheme_list: (list) 包含拼音和英文单词的列表
        :return: (list) 音素列表
        """
        grapheme_list = cds.grapheme_list
        language_list = cds.language_flag
        prosody_list = cds.prosody_list

        phone_list = []
        assert len(grapheme_list) == len(language_list)
        for index, g in enumerate(grapheme_list):
            if language_list[index] == 0:  # en
                if g == 'A':
                    phone_list.append('eeei1')
                else:
                    phone_list.append(self.single_word_to_phone(g))
            elif language_list[index] == 1:  # cn
                phone_list.append(self.single_pingyin_to_phone(g))
            else:
                phone_list.append(g)

        if language_list[0] == 1:  # cn
            text = '-'
        elif language_list[0] == 0:  # en

            text = '-'
        else:
            text = ''

        for index, i in enumerate(zip(phone_list, prosody_list)):
            if language_list[index] == 1:
                text += ''.join(i)
            elif language_list[index] == 0:
                text += '/%s/' % '/'.join(i)
            elif language_list[index] == '，':
                text += '#3'
            elif language_list[index] == ',':
                text += '#3，'
            elif language_list[index] == '、':
                text += '#2'
            else:
                pass

        def func(match):
            num1 = match.group(1)
            num2 = match.group(2)

            return '#%s' % str(num1) if num1 >= num2 else '#%s' % str(num2)

        text = re.sub(r"#(\d)/?#(\d)", func, text)  # 韵律去重
        app_logger.debug("韵律替换前的结果: %s" % text)
        text = text.replace('#0', '').replace('#1', '@').replace('#2', '^').replace('#3', '，')
        text = re.sub(r"[@^&]+$", '', text)  # 消除结尾韵律
        text = re.sub(r"/+", '/', text)
        # print("text+++", text + '。')
        return text + '。'


class GraphemeToPhonemeCN(object):
    def __init__(self):

        self.uppercase_letter_map = {"A": "eeei1",
                                     "B": "bi4",
                                     "C": "sei4",
                                     "D": "di4",
                                     "E": "iii4",
                                     "F": "ai2f",
                                     "G": "ji4",
                                     "H": "ei2ch",
                                     "I": "aaai4",
                                     "J": "jei4",
                                     "K": "kei4",
                                     "L": "ai2l",
                                     "M": "ai2m",
                                     'N': "eeen1",
                                     "O": "ooou1",
                                     "P": "pi4",
                                     "Q": "kiu4",
                                     "R": "aaa4",
                                     "S": "aaai2s",
                                     "T": "ti4",
                                     "U": "iiiu1",
                                     "V": "uuui1",
                                     "W": "da2bliu1",
                                     "X": "ai2ks",
                                     "Y": "uuuai4",
                                     "Z": "zei4"}

    def single_pingyin_to_phone(self, pinyin):
        """
        单个拼音映射成音素
        :param pinyin:
        :return:
        """
        phone = pinyin2phone_cnen.get(pinyin, '')
        return phone

    def call(self, cds):
        """
        :param grapheme_list: (list) 包含拼音和英文单词的列表
        :return: (list) 音素列表
        """
        grapheme_list = cds.grapheme_list
        language_list = cds.language_flag
        prosody_list = cds.prosody_list

        phone_list = []
        assert len(grapheme_list) == len(language_list)
        for index, g in enumerate(grapheme_list):
            if language_list[index] == 0:  # en uppercase
                phone_list.append(self.uppercase_letter_map.get(g))
            elif language_list[index] == 1:  # cn
                phone_list.append(self.single_pingyin_to_phone(g))
            else:
                phone_list.append(g)

        text = '-'

        for index, i in enumerate(zip(phone_list, prosody_list)):
            if language_list[index] == 1:
                text += ''.join(i)
            elif language_list[index] == 0:
                text += ''.join(i)
            elif language_list[index] == '，':
                text += '#3'
            elif language_list[index] == ',':
                text += '#3，'
            elif language_list[index] == '、':
                text += '#2'
            else:
                pass

        def func(match):
            num1 = match.group(1)
            num2 = match.group(2)

            return '#%s' % str(num1) if num1 >= num2 else '#%s' % str(num2)

        text = re.sub(r"#(\d)#(\d)", func, text)  # 韵律去重
        app_logger.debug("韵律替换前的结果: %s" % text)
        text = text.replace('#0', '').replace('#1', '@').replace('#2', '^').replace('#3', '，')
        text = re.sub(r"[@^&]+$", '', text)  # 消除结尾韵律
        #
        return text + '。'


class GraphemeToPhonemeHK(object):
    def __init__(self):
        self.cantonese_dict = {}
        work_dir = global_config.get_value(section="APP", option="WORKING_DIR", default="./model")
        dictionary_file = os.path.join(work_dir, "lib/zhy_jyut_cantonese.tsv")
        with io.open(dictionary_file, mode='r', encoding='utf-8') as f:
            for line in f:
                line = line.strip().split('\t')
                chs, jyp = line
                self.cantonese_dict[chs] = jyp

        self.uppercase_letter_map = {"A": "eeei1",
                                     "B": "bi4",
                                     "C": "sei4",
                                     "D": "di4",
                                     "E": "iii4",
                                     "F": "ai2f",
                                     "G": "ji4",
                                     "H": "ei2ch",
                                     "I": "aaai4",
                                     "J": "jei4",
                                     "K": "kei4",
                                     "L": "ai2l",
                                     "M": "ai2m",
                                     'N': "eeen1",
                                     "O": "ooou1",
                                     "P": "pi4",
                                     "Q": "kiu4",
                                     "R": "aaa4",
                                     "S": "aaai2s",
                                     "T": "ti4",
                                     "U": "iiiu1",
                                     "V": "uuui1",
                                     "W": "da2bliu1",
                                     "X": "ai2ks",
                                     "Y": "uuuai4",
                                     "Z": "zei4"}

    def single_hanzi_to_phone(self, hanzi):
        """
        单个汉字映射成音素
        :param hanzi:
        :return:
        """
        phone = self.cantonese_dict.get(hanzi)
        # get first word of multiple phoneme
        if phone and '/' in phone:
            phone = phone.split('/')[0]

        return phone

    def call(self, cds):
        """
        :param text_list: (list) 包含拼音和英文单词的列表
        :return: (list) 音素列表
        """
        text_list = cds.text_list
        language_list = cds.language_flag
        prosody_list = cds.prosody_list

        phone_list = []
        assert len(text_list) == len(language_list)
        for index, g in enumerate(text_list):
            if language_list[index] == 0:  # en uppercase
                phone_list.append(self.uppercase_letter_map.get(g))
            elif language_list[index] == 1:  # cn
                phone_list.append(self.single_hanzi_to_phone(g))
            else:
                phone_list.append(g)
        if None in phone_list:
            app_logger.error("音素转换有None值: {}".format(phone_list))
        app_logger.debug("转音素结果： {}".format(phone_list))

        text = '-'

        for index, i in enumerate(zip(phone_list, prosody_list)):
            if language_list[index] == 1:
                text += ''.join(i)
            elif language_list[index] == 0:
                text += ''.join(i)
            elif language_list[index] == '，':
                text += '#3'
            elif language_list[index] == ',':
                text += '#3，'
            elif language_list[index] == '、':
                text += '#2'
            else:
                pass

        def func(match):
            num1 = match.group(1)
            num2 = match.group(2)

            return '#%s' % str(num1) if num1 >= num2 else '#%s' % str(num2)

        text = re.sub(r"#(\d)#(\d)", func, text)  # 韵律去重
        app_logger.debug("韵律替换前的结果: %s" % text)
        text = text.replace('#0', '').replace('#1', '@').replace('#2', '^').replace('#3', '，')
        text = re.sub(r"[@^&]+$", '', text)  # 消除结尾韵律

        return text + '*。'


if __name__ == '__main__':
    g2p = GraphemeToPhonemeCNEN()
    res = g2p.single_pingyin_to_phone('gui1')
    print(res)
    res = g2p.single_pingyin_to_phone('ji1')
    print(res)
