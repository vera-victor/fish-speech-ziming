# -*- coding: utf-8 -*-
# Create Time: 2020/10/22 下午2:52
# Author: Allen

"""数字和标点组合正则"""
import os
import re
import json
from tools.text_norm.log.log_helper import app_logger
from tools.text_norm.front_end.normalize.number_normalize import NumberNormalize
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"config")

class NumberPunctionNormalizeCN(object):
    """
    数字和标点的组合正则
    """

    def __init__(self):
        unit_file = os.path.join(config_path, 'units.json')
        app_logger.debug("加载自定义 单位 [%s]" % unit_file)
        self.unit_dict = self.load_json2dict(unit_file)
        self.num_norm = NumberNormalize()

    @staticmethod
    def load_json2dict(json_path):
        with open(json_path, "r") as rf:
            data = json.load(rf)
        return data

    def read_cn_int_num(self, text):
        """
        读中文整数数字，读零
        :param text: (str)
        :return: (str)
        """
        if "." in text:
            return self.num_norm.call(text, 'cn', 'ordinal')
        elif 0 <= int(text) <= 9:
            return self.num_norm.call(text, 'cn', 'bitwise')
        else:
            text = str(int(text))
            return self.num_norm.call(text, 'cn', 'ordinal')

    def read_cn_float_num(self, text):
        """
        读中文浮点数数字
        :param text: (str)
        :return: (str)
        """

        if int(float(text)) == 0:
            num = self.num_norm.call(str(0), 'cn', 'ordinal')

            return "零下%s摄氏度" % num
        else:
            if '.' in text:
                num = self.num_norm.call(str(float(text)), 'cn', 'ordinal')
            else:
                num = self.num_norm.call(str(int(text)), 'cn', 'ordinal')

            return num

    def code_punc(self, text):
        """
        手机号，电话号处理
        :param text:
        :return:
        """

        # 标准手机号
        def normal_phone_func1(match):
            num = self.num_norm.call(match.group(2), 'cn', 'phone')
            return num

        text = re.sub(r"(\+86 ?)?(1[0-9]{10})", normal_phone_func1, text)

        def primary_phone_func(match):
            num = match.group(3).replace("-", "").replace("—", "").replace("+", "").replace("/", "").replace(" ", "")
            num = self.num_norm.call(num, 'cn', 'phone')
            return match.group(1) + match.group(2) + num

        text = re.sub(r"(电话|手机|代码|代号|编号|邮编|拨打|房间号|联系方式|密码|号码|账号)([^\d +\-—/]{0,3})([\d +\-—/]+)", primary_phone_func, text)

        #
        def code_func1(match):
            num = self.num_norm.call(match.group(2), 'cn', 'bitwise')
            return match.group(1)+num + match.group(3)

        text = re.sub(r"(^|[^\d\-])([0-9]+)(赛季)", code_func1, text)

        # 阵型
        def code_func2(match):
            num = self.num_norm.call(match.group(1), 'cn', 'phone')
            return num + match.group(2)

        text = re.sub(r"(\d+)(阵型|折)", code_func2, text)
        # text = re.sub(r"([0-9]+)(阵型|网站)", code_func2, text)

        # 特殊电话
        def code_func2(match):
            num = self.num_norm.call(match.group(2), 'cn', 'phone')
            return match.group(1) + num + match.group(3)

        text = re.sub(r"(^|\D)(110|119|120|911|114116|114|10086|12306|12315)([^\d个万元所批]|$)", code_func2, text)
        # 量词判断：个、单位、元、万、所、

        return text

    def license_plate_punc(self, text):
        """
        车牌处理
        :param text:
        :return:
        """

        def plate_func(match):
            sub_first = match.group(1)
            sub_str = match.group(2)

            if len(sub_str.replace(" ", "")) == 6:
                sub_str = re.sub("[0-9]+", lambda m: self.num_norm.call(m.group(), 'cn', 'phone'), sub_str)

            return sub_first + sub_str

        text = re.sub(r"([京津沪渝蒙新藏宁桂港澳黑吉辽晋冀青鲁豫苏皖浙闽赣湘鄂粤琼甘陕黔贵滇云川])([ 0-9A-Za-z]+)", plate_func, text)

        return text

    def colon_punc(self, text):
        """
        :(冒号)搭配数字处理
        约定：
            在时间范围以内（两个或三个冒号，整数，时分秒数值范围）的按时间读，在时间范围以外的按比分读
        :param text: (str)
        :return: (str)
        """

        def double_func(match):
            num1 = match.group(1)
            num2 = match.group(2)
            num3 = match.group(3)
            num4 = match.group(4)

            if 0 <= int(num1) <= 24 and 0 <= int(num2) < 60 and 0 <= int(num3) <= 24 and 0 <= int(num4) < 60:
                num1 = self.num_norm.call(num1, 'cn', 'ordinal')
                num2 = self.read_cn_int_num(num2)
                num3 = self.num_norm.call(num3, 'cn', 'ordinal')
                num4 = self.read_cn_int_num(num4)
                if int(match.group(2)) == 0 and int(match.group(4)) == 0:
                    return "%s点到%s点" % (num1, num3)
                elif int(match.group(2)) == 0:
                    return "%s点到%s点%s分" % (num1, num3, num4)
                elif int(match.group(4)) == 0:
                    return "%s点%s分到%s点" % (num1, num2, num3)

                return "%s点%s分到%s点%s分" % (num1, num2, num3, num4)

        text = re.sub(r"(\d{1,2}):(\d{1,2})-(\d{1,2}):(\d{1,2})", double_func, text)


        def func(match):
            match_str = "%s%s" % (match.group(1), match.group(2))
            match_list = match_str.split(':')
            if score_flage:
                num_list = [self.num_norm.call(num, 'cn', 'ordinal') for num in match_list]

                return "比".join(num_list)
            else:
                if match_str.count(':') == 2:
                    if re.findall(r"(?:[0-9]+):(?:[0-9]{2}):(?:[0-9]{2})", match_str):  # 时分秒
                        if 0 <= int(match_list[0]) <= 24 and 0 <= int(match_list[1]) <= 60 and 0 <= float(
                                match_list[2]) <= 60:
                            num1 = self.num_norm.call(match_list[0], 'cn', 'ordinal')
                            num2 = self.read_cn_int_num(match_list[1])
                            num3 = self.read_cn_int_num(match_list[2])
                            if float(match_list[2]) == 0:
                                if int(match_list[1]) == 0:
                                    return "%s点" % num1
                                else:
                                    return "%s点%s分" % (num1, num2)

                            return "%s点%s分%s秒" % (num1, num2, num3)

                elif match_str.count(":") == 1:
                    if re.findall(r"(?:[0-9]+):(?:[0-9]{2})", match_str):  # 时分
                        if 0 <= float(match_list[0]) <= 24 and 0 <= float(match_list[1]) <= 60:
                            num1 = self.num_norm.call(match_list[0], 'cn', 'ordinal')
                            num2 = self.read_cn_int_num(match_list[1])
                            if float(match_list[1]) == 0:
                                return "%s点" % num1

                            return "%s点%s分" % (num1, num2)
                # 比分
                num_list = [self.num_norm.call(num, 'cn', 'ordinal') for num in match_list]

                return "比".join(num_list)

        score_flage = False
        if re.findall(r"比分|分数|战胜|领先|击败|险胜|不敌|轻取|女排|男排|篮球|主场|客场|决赛|比赛|冠军|输|赢", text):  # TODO添加更多的关键词
            score_flage = True

        text = re.sub(r"(-[0-9]+\.[0-9]+|-[0-9]+|[0-9]+\.[0-9]+|[0-9]+)((?:[:](-[0-9]+\.[0-9]+|-[0-9]+|[0-9]+\.[0-9]+|[0-9]+))+)", func, text)

        # 将剩余的冒号替换成逗号
        text = text.replace(':', "，")

        return text

    def plus_punc(self, text):
        """
        +(加号)处理
        :param text: (str)
        :return: (str)
        """
        text = text.replace('+', '加')

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
            num1 = match.group(1)
            num2 = match.group(2)
            num3 = match.group(3)
            if len(num1) == 4 and 1 <= int(num2) <= 12 and 1 <= int(num3) <= 31:  # 判断为 年月日
                num1 = self.num_norm.call(str(int(num1)), 'cn', 'bitwise')
                num2 = self.num_norm.call(str(int(num2)), 'cn', 'ordinal')
                num3 = self.num_norm.call(str(int(num3)), 'cn', 'ordinal')

                return '%s年%s月%s日' % (num1, num2, num3)
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

    def percent_sign_punc(self, text):
        """
        %(百分号)处理 或 ‰(千分号)处理
        :param text: (str)
        :return: (str)
        """

        # 处理 12%-13%或12%~13%
        def two_num_func(match):
            num1 = match.group(1)
            num2 = match.group(2)

            return "百分之%s至百分之%s" % (self.read_cn_float_num(num1), self.read_cn_float_num(num2))

        text = re.sub(r"([0-9]+\.[0-9]+|[0-9]+)%?[-~—]([0-9]+\.[0-9]+|[0-9]+)%", two_num_func, text)

        # 负数
        def hundred_negative_func(match):
            num = match.group(1)
            if '.' in num:
                num = self.num_norm.call(str(float(num)), 'cn', 'ordinal')
            else:
                num = self.num_norm.call(str(int(num)), 'cn', 'ordinal')

            return "负百分之%s" % num

        text = re.sub(r"-([0-9]+\.[0-9]+|[0-9]+)%", hundred_negative_func, text)

        def thousand_negative_func(match):
            num = match.group(1)
            if '.' in num:
                num = self.num_norm.call(str(float(num)), 'cn', 'ordinal')
            else:
                num = self.num_norm.call(str(int(num)), 'cn', 'ordinal')

            return "负千分之%s" % num

        text = re.sub(r"-([0-9]+\.[0-9]+|[0-9]+)‰", thousand_negative_func, text)

        # 正数
        def hundred_positive_func(match):
            num = match.group(1)
            if '.' in num:
                num = self.num_norm.call(str(float(num)), 'cn', 'ordinal')
            else:
                num = self.num_norm.call(str(int(num)), 'cn', 'ordinal')

            return "百分之%s" % num

        text = re.sub(r"([0-9]+\.[0-9]+|[0-9]+)%", hundred_positive_func, text)

        def thousand_positive_func(match):
            num = match.group(1)
            if '.' in num:
                num = self.num_norm.call(str(float(num)), 'cn', 'ordinal')
            else:
                num = self.num_norm.call(str(int(num)), 'cn', 'ordinal')
            return "千分之%s" % num

        text = re.sub(r"([0-9]+\.[0-9]+|[0-9]+)‰", thousand_positive_func, text)

        # 删除剩余的百分号
        text = text.replace('%', '').replace('‰', '')

        return text

    def date_punc(self, text):

        def date_func1(match):
            num1 = self.num_norm.call(match.group(2), 'cn', 'bitwise')
            num2 = self.num_norm.call(match.group(3), 'cn', 'ordinal')
            num3 = self.num_norm.call(match.group(4), 'cn', 'ordinal')
            return "%s年%s月%s日" % (num1, num2, num3)

        text = re.sub(r"((\d{2,4}) *年(\d{1,2}) ?月(\d{1,2}) *日)", date_func1, text)

        def date_func2(match):
            num2 = self.num_norm.call(match.group(2), 'cn', 'ordinal')
            num3 = self.num_norm.call(match.group(3), 'cn', 'ordinal')
            return "%s月%s日" % (num2, num3)

        text = re.sub(r"((\d{1,2}) *月(\d{1,2}) *日)", date_func2, text)

        def time_func1(match):
            num2 = self.num_norm.call(match.group(2), 'cn', 'ordinal')
            num3 = self.num_norm.call(match.group(3), 'cn', 'bitwise')
            return "%s秒%s" % (num2, num3)

        text = re.sub(r"((\d{1,2}) *秒 *(\d{1,2}))", time_func1, text)

        return text

    def unit_punc(self, text):
        """
        单位符号
        :param text:
        :return:
        """
        def func_unit_quantifier(match):
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

        # print("text0", text)
        text = re.sub(r"近(\d+) *年", spec_year_func1, text)
        # print("text0_", text)
        def spec_year_func2(match):
            y = self.num_norm.call(match.group(1), 'cn', 'ordinal')
            return "%s年%s" % (y, match.group(2))

        text = re.sub(r"(\d+) *年((以?来)|(之?以?前)|(之?以?后))", spec_year_func2, text)
        def year_func1(match):
            y1 = self.num_norm.call(match.group(1), 'cn', 'bitwise')
            y2 = self.num_norm.call(match.group(2), 'cn', 'bitwise')
            return "%s至%s年" % (y1, y2)

        text = re.sub(r"(\d{4})[-—](\d{4}) *年", year_func1, text)
        def year_func3(match):
            y = self.num_norm.call(match.group(1), 'cn', 'bitwise')
            return "%s年" % y
        # print("text2", text)
        text = re.sub(r"([1-3]\d{3}|(([0-2][1-9])|([1-2]\d))) *年", year_func3, text)
        # print("text2_", text)
        def year_func2(match):
            y = self.num_norm.call(match.group(1), 'cn', 'bitwise')
            return "%s后" % y

        text = re.sub(r"(\d0|5) *后", year_func2, text)
        return text

    def renminbi_punc(self, text):
        """
        ￥(人民币)付出
        :param text: (str)
        :return: (str)
        """

        def func(match):
            num = match.group(1)
            if '.' in num:
                num = self.num_norm.call(str(float(num)), 'cn', 'ordinal')
            else:
                num = self.num_norm.call(str(int(num)), 'cn', 'ordinal')
            return "%s元" % num

        text = re.sub(r"￥([0-9]+\.[0-9]+|[0-9]+)", func, text)

        # 处理剩余的人民币符号
        text = text.replace("￥", '')

        return text

    def centigrade_punc(self, text):
        """
        °C(摄氏度)付出
        :param text: (str)
        :return: (str)
        """

        # 3-4°C或3~4°C
        def two_num_func(match):
            num1 = match.group(1)
            num2 = match.group(2)

            return "%s至%s摄氏度" % (self.read_cn_float_num(num1), self.read_cn_float_num(num2))

        text = re.sub(r"([0-9]+\.[0-9]+|[0-9]+)[-~]([0-9]+\.[0-9]+|[0-9]+)(°C|℃)", two_num_func, text)

        # 负数
        def negative_func(match):
            num = match.group(1)

            if int(float(num)) == 0:
                num = self.num_norm.call(str(0), 'cn', 'ordinal')

                return "零下%s摄氏度" % num
            else:
                if '.' in num:
                    num = self.num_norm.call(str(float(num)), 'cn', 'ordinal')
                else:
                    num = self.num_norm.call(str(int(num)), 'cn', 'ordinal')

                return "零下%s摄氏度" % num

        text = re.sub(r"-([0-9]+\.[0-9]+|[0-9]+)(°C|℃)", negative_func, text)

        # 正数
        def positive_func(match):
            num = match.group(1)

            if int(float(num)) == 0:
                num = self.num_norm.call(str(0), 'cn', 'ordinal')
                return "%s摄氏度" % num
            else:
                if '.' in num:
                    num = self.num_norm.call(str(float(num)), 'cn', 'ordinal')
                else:
                    num = self.num_norm.call(str(int(num)), 'cn', 'ordinal')
                return "%s摄氏度" % num

        text = re.sub(r"([0-9]+\.[0-9]+|[0-9]+)(°C|℃)", positive_func, text)

        # 处理剩余的摄氏度符号
        text = text.replace("°C", '').replace("°", '').replace("℃", "")

        return text

    def wavy_punc(self, text):
        """
        ~(波浪号)处理
        :param text: (str)
        :return: (str)
        """

        def wavy_func(match):
            num1 = match.group(1)
            num2 = match.group(2)
            num1 = self.num_norm.call(num1, 'cn', 'ordinal')
            num2 = self.num_norm.call(num2, 'cn', 'ordinal')
            return "%s至%s" % (num1, num2)

        text = re.sub(r"([0-9]+\.?[0-9]+?)~([0-9]+\.?[0-9]+?)", wavy_func, text)

        return text

    def hyphen_punc(self, text):
        """
        -(中间短横线)处理
        约定：
            1.2012-01-20转年月日
            2.10-20转为 十至二十
        :param text: (str)
        :return: (str)
        """

        def phone_func1(match):
            num1 = self.num_norm.call(match.group(1), 'cn', 'phone')
            num2 = self.num_norm.call(match.group(2), 'cn', 'phone')
            return num1 + num2

        text = re.sub(r"(\d{3})[-—](\d{8})", phone_func1, text)

        def phone_func2(match):
            num1 = self.num_norm.call(match.group(1), 'cn', 'phone')
            num2 = self.num_norm.call(match.group(2), 'cn', 'phone')
            return num1 + num2

        text = re.sub(r"(\d{4})[-—](\d{7})", phone_func2, text)

        def three_hyphen_func(match):
            num1 = match.group(1)
            num2 = match.group(2)
            num3 = match.group(3)
            if len(num1) == 4 and 1 <= int(num2) <= 12 and 1 <= int(num3) <= 31:  # 判断为年月日
                num1 = self.num_norm.call(str(int(num1)), 'cn', 'bitwise')
                num2 = self.num_norm.call(str(int(num2)), 'cn', 'ordinal')
                num3 = self.num_norm.call(str(int(num3)), 'cn', 'ordinal')
                return "%s年%s月%s日" % (num1, num2, num3)
            else:  # 判断为比分
                num1 = self.num_norm.call(str(int(num1)), 'cn', 'ordinal')
                num2 = self.num_norm.call(str(int(num2)), 'cn', 'ordinal')
                num3 = self.num_norm.call(str(int(num3)), 'cn', 'ordinal')
                return "%s至%s至%s" % (num1, num2, num3)

        text = re.sub(r"([0-9]+)-([0-9]+)-([0-9]+)", three_hyphen_func, text)

        def two_hyphen_func1(match):
            num1 = match.group(1)
            num2 = match.group(2)
            num1 = self.num_norm.call(num1, 'cn', 'ordinal')
            num2 = self.num_norm.call(num2, 'cn', 'ordinal')
            return "%s至%s" % (num1, num2)

        text = re.sub(r"(\d+\.\d+)[-—](\d+\.\d+)", two_hyphen_func1, text)

        def two_hyphen_func2(match):
            num1 = match.group(1)
            num2 = match.group(2)
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

        text = re.sub(r"(\d+)[-—](\d+)", two_hyphen_func2, text)

        # TODO 不处理剩余中间短横线，因为可能是负数符号，在self.default_translate中处理剩余中间短横线

        return text

    def default_translate(self, text):
        """
        默认数字转换
        :param text: (str)
        :return: (str)
        """

        def code_func(match):
            num = self.num_norm.call(match.group(2), 'cn', 'bitwise')
            return match.group(1) + num

        text = re.sub(r"(^|[^\d\-\.])(0[0-9]+)", code_func, text)

        def func(match):
            num = match.group(1)
            if match.group(1).startswith("."):
                num = "0" + num
            if match.group(1).startswith("-."):
                num = "-0" + num
            num = self.num_norm.call(num, 'cn', 'ordinal')
            return num

        text = re.sub(r"(-[0-9]*\.[0-9]+|-[0-9]+|[0-9]*\.[0-9]+|[0-9]+)", func, text)

        # 处理剩余中间短横线
        text = text.strip('-').replace("-", "")
        # text = text.strip('-').replace("-", "至")

        return text

    def call(self, text):
        # 处理英文逗号
        text = re.sub(r"(?<=\d),(?=\d)", '', text)  # 删除数字间的英文逗号
        app_logger.debug("处理数字间的英文逗号 [输出]: %s" % text)

        # 编号处理
        text = self.code_punc(text)
        app_logger.debug("处理编号 [输出]: %s" % text)

        # 车牌处理
        text = self.license_plate_punc(text)
        app_logger.debug("处理车牌 [输出]: %s" % text)

        # 处理百分号、千分号
        text = self.percent_sign_punc(text)
        app_logger.debug("处理百分号、千分号 [输出]: %s" % text)

        # 波浪号处理
        text = self.wavy_punc(text)
        app_logger.debug("处理波浪号 [输出]: %s" % text)

        # 处理冒号
        text = self.colon_punc(text)
        app_logger.debug("处理冒号 [输出]: %s" % text)

        # 处理斜杠
        text = self.slash_punc(text)
        app_logger.debug("处理斜杠 [输出]: %s" % text)

        text = self.date_punc(text)
        app_logger.debug("处理日期 [输出]: %s" % text)

        text = self.unit_punc(text)
        app_logger.debug("处理单位符号 [输出]: %s" % text)
        # print("处理单位符号 [输出]: %s" % text)
        # 处理数字搭配年
        text = self.year_punc(text)
        app_logger.debug("处理数字搭配年 [输出]: %s" % text)
        # print("处理数字搭配年 [输出]: %s" % text)
        # 处理人民币号
        text = self.renminbi_punc(text)
        app_logger.debug("处理人民币号 [输出]: %s" % text)

        # 处理摄氏度符
        text = self.centigrade_punc(text)
        app_logger.debug("处理摄氏度符 [输出]: %s" % text)

        # 处理中间短横线
        text = self.hyphen_punc(text)
        app_logger.debug("处理中间短横线 [输出]: %s" % text)

        # 默认数字转换
        text = self.default_translate(text)
        app_logger.debug("默认数字转换 [输出]: %s" % text)

        # 处理波浪号
        # text = self.wavy_punc(text)
        app_logger.debug("处理波浪号 [输出]: %s" % text)

        # 处理加号
        text = self.plus_punc(text)
        app_logger.debug("处理加号 [输出]: %s" % text)

        return text


if __name__ == '__main__':
    text = "你哈， 23:01， 达到 25:1"
    npn = NumberPunctionNormalizeCN()
    # print(npn.call("你哈， 23:01， 达到 25:1"))
    # print(npn.call("你哈， 23:01:12， 达到 23:01:71"))
    #
    # print(npn.call("你哈， 23/01/12， 达到 23/01"))
    #
    # print(npn.call("你哈， ￥23.5， 达到 23.01‰"))
    #
    # print(npn.call("2012年， 23.5%， 达到 23.01‰"))
    # print(npn.call("202年， 23.5%， 达到 23.01‰"))
    #
    # print(npn.call("你哈， 23.5~13.7"))
    # print(npn.call("你哈， 23.5 ~13.7"))
    # print(npn.call("你哈， 23.5~ 13.7"))
    # print(npn.call("你哈， 23.5 ~ 13.7"))
    #
    # print(npn.call("12°C， -12°C， 0.0°C， 0°C， 1.1°C， -1.1°C"))
    # print(npn.call("12°C， -12°C， 0.0°C， 0°C， 1.1°C， -1.1°C °C"))
    # print(npn.call("12°C， -12°C， 0.0°C， 0°C， 1.1°C， -1.1°C C"))
    # print(npn.call("23.5%，23%，0.01‰，0.0%"))
    # print(npn.call("-23.5%，-23%，-0.01，-0.0， -0"))
    print(npn.call("12:12:14，13:12:14，12:12:-14，12:-12:14，-12:12:14"))
