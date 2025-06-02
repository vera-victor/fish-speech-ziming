# -*- coding: utf-8 -*-
# Create Time: 2020/9/21 上午9:43
# Author: Allen
import re


class CustomDataStructure(object):
    """自定义数据结构，用于韵律预测模块、拼音校正、韵律校正"""

    def __init__(self, logger=None):
        self.logger = logger
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

    def init(self, text, lang):
        """
        :param text: (str) 正则化后的文本
        """
        self.lang = lang
        self.text_list = []  #
        self.grapheme_list = []  # 中文存放拼音，英文存放单词
        self.prosody_list = []  # 韵律标记
        self.phoneme_list = []  # 音素标记
        self.before_silence = 0
        self.after_silence = 0
        self.language_flag = []  # cn 1 en 0 其他

        self.text = self.mark_chars_full_to_half(text.strip())  # 全角转半角

        self.parser_silence()

        if lang in ['CN', 'CN_EN']:  # 中文支持自定义拼音、韵律、姓名多音字
            self.parser_name()
            self.parser_grapheme_and_prosody()

        elif lang in ["EN"]:  # 英文支持自定义韵律
            self.parser_prosody()

        return self

    def parser_silence(self):
        # 解析前停顿标识符
        before_silence = re.findall(r"^<&[0-9]+>", self.text)
        if before_silence:
            self.before_silence = max(int(before_silence[0][2:-1]), 0)
            self.text = self.text[len(before_silence[0]):]

        # 解析后停顿标识符
        after_silence = re.findall(r"<&[0-9]+>$", self.text)
        if after_silence:
            self.after_silence = max(int(after_silence[0][2:-1]), 0)
            self.text = self.text[:-len(after_silence[0])]

        # 删除中间停顿标识符
        self.text = re.sub("<&[0-9]+>", '', self.text)

    def parser_name(self):
        mapping = {'仇': '仇<qiu2>', '朴': '朴<piao2>', '单': '单<shan4>', '解': '解<xie4>', '区': '区<ou1>', '查': '查<zha1>',
                   '繁': '繁<po2>', '瞿': '瞿<qu2>', '员': '员<yun4>', '能': '能<nai4>', '阚': '阚<kan4>', '都': '都<du1>',
                   '乜': '乜<nie4>', '缪': '缪<miao4>', '句': '句<gou1>', '阿': '阿<e1>', '任': '任<ren2>', '要': '要<yao1>',
                   '华': '华<hua4>', '过': '过<guo1>', '曲': '曲<qu1>', '訾': '訾<zi1>', '哈': '哈<ha3>', '钻': '钻<zuan1>',
                   '谌': '谌<chen2>', '令狐': '令<ling2>狐<hu2>', '尉迟': '尉<yu4>迟<chi2>', '澹台': '澹<tan2>台<tai2>',
                   '皇甫': '皇<huang2>甫<fu3>', '长孙': '长<zhang3>孙<sun1>', '宰父': '宰<zai3>父<fu3>', '亓官': '亓<qi2>官<guan1>',
                   '毌丘': '毌<guan4>丘<qiu1>'}

        def func(match):
            name = match.group(1)
            clean_name = name[1:-1]
            for k, v in mapping.items():
                if k in clean_name:
                    clean_name = re.sub(r"^(%s)([\u4e00-\u9fa5<>a-z1-5]+)" % k, r"%s\2" % v, clean_name)  # 替换姓名多音字
                    clean_name = re.sub(r"([\u4e00-\u9fa5])", r"\1<#0>", clean_name)  # 姓名多音字添加<#0>
                    clean_name = re.sub(r"(<#[0123]>)(<[a-z]+[1-5]>)", r"\2\1", clean_name)  # 交换韵律与拼音标记
                    break  # 匹配一次就跳出，减少匹配次数
            return clean_name

        self.text = re.sub(r"(\{[\u4e00-\u9fa5<>a-z1-5]+\})", func, self.text)

    def parser_grapheme_and_prosody(self):
        """
        解析文本中的韵律与拼音标识符
        :return: None
        """
        text_list = [x for x in re.split(r"([\u4e00-\u9fa5]| |<.*?>|[A-Za-z\']+)", self.text) if x != '' and x != ' ']
        for i in text_list:
            if self.is_chinese(i):
                self.text_list.append(i)
                self.grapheme_list.append('')
                self.prosody_list.append('')
                self.language_flag.append(1)  # cn 1
            elif self.is_engish(i):
                self.text_list.append(i)
                self.grapheme_list.append('')
                if i.isupper():
                    self.prosody_list.append('#0')  # 设置大写字母韵律为#0
                else:
                    self.prosody_list.append('')
                self.language_flag.append(0)  # en 0
            elif i.startswith('<#'):
                stop_grade = int(i[2:-1])
                if stop_grade > 3:
                    stop_grade = 3
                self.prosody_list[-1] = '#%d' % stop_grade
                continue
            elif i.startswith("<"):
                self.grapheme_list[-1] = i[1:-1]
                continue
            else:
                self.text_list.append(i)
                self.grapheme_list.append('')
                self.prosody_list.append('#0')
                self.language_flag.append(i)  # 其他

        assert len(self.text_list) == len(self.grapheme_list) == len(self.prosody_list) == len(self.language_flag)

    def parser_prosody(self):
        """
        解析文本中的韵律标识符
        :return: None
        """
        text_list = [x for x in re.split(r"( |,|\.|!|\?|<.*?>)", self.text) if x != '' and x != ' ']
        for word in text_list:
            if word.isalpha() or word.replace("'", "").isalpha():
                self.text_list.append(word.lower())
                self.grapheme_list.append('')
                self.prosody_list.append('')
                self.language_flag.append(0)  # en 0
            elif word.startswith('<#'):
                stop_grade = int(word[2:-1])
                if stop_grade > 3:
                    stop_grade = 3
                self.prosody_list[-1] = '#%d' % stop_grade
                continue
            else:
                self.text_list.append(word)
                self.grapheme_list.append('')
                self.prosody_list.append('')
                self.language_flag.append(word)  # 其他

        assert len(self.text_list) == len(self.grapheme_list) == len(self.prosody_list) == len(self.language_flag)

    def is_chinese(self, char):
        """判断字符是否为中文字符"""
        if '\u4e00' <= char <= '\u9fa5':
            return True
        else:
            return False

    def is_engish(self, word):
        """判断字符串是否为英文字符"""
        if re.findall(r"^[A-Za-z\']+$", word):
            return True
        else:
            return False

    def show(self):
        print("self.text: ", self.text)
        print("self.text_list: ", self.text_list)
        print("len(self.text_list): ", len(self.text_list))
        print("self.grapheme_list: ", self.grapheme_list)
        print("len(self.grapheme_list): ", len(self.grapheme_list))
        print("self.prosody_list: ", self.prosody_list)
        print("len(self.prosody_list): ", len(self.prosody_list))

        print("self.before_silence: ", self.before_silence)
        print("self.after_silence: ", self.after_silence)
        print("self.language_flag: ", self.language_flag)
        print("self.phone_list: ", self.phoneme_list)

    def info(self):
        info = ["self.text: {}".format(self.text),
                "self.text_list: {}".format(self.text_list),
                "len(self.text_list): {}".format(len(self.text_list)),
                "self.grapheme_list: {}".format(self.grapheme_list),
                "len(self.grapheme_list): {}".format(len(self.grapheme_list)),
                "self.prosody_list: {}".format(self.prosody_list),
                "len(self.prosody_list): {}".format(len(self.prosody_list)),
                "self.before_silence: {}".format(self.before_silence),
                "self.after_silence: {}".format(self.after_silence),
                "self.language_flag: {}".format(self.language_flag),
                "self.phone_list: {}".format(self.phoneme_list)]

        return "\n".join(info)

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

    def update_grapheme(self, grapheme_list):
        """
        根据位置更新拼音列表
        :param grapheme_list: (list)
        :return:
        """
        assert len(grapheme_list) == len(self.grapheme_list)
        for index, grapheme in enumerate(grapheme_list):
            if self.grapheme_list[index] != '':
                continue
            else:
                self.grapheme_list[index] = grapheme

    def update_prosody(self, prosody_list):
        """
        根据位置更新韵律列表
        :param prosody_list: (list)
        :return:
        """
        assert len(prosody_list) == len(self.prosody_list)
        for index, prosody in enumerate(prosody_list):
            if self.prosody_list[index] != '':
                continue
            else:
                self.prosody_list[index] = str(prosody) if str(prosody).startswith('#') else "#" + str(prosody)
        self.prosody_list[-1] = '#0'  # 强制文本最后韵律为#0


if __name__ == '__main__':
    text = 'A B C 《＃３》 D E F G H 《＃２》 I J K L M N'
    # text = "犹如经历追求时对方一时兴起的tease"

    cds = CustomDataStructure(text)
    cds.init(text, 'EN')
    cds.show()
    print(cds.text_list)
    # 纯中文 cn 纯英文 en 中英混合 cn&en
