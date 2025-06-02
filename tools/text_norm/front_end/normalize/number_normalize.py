# -*- coding: utf-8 -*-
# Create Time: 2020/9/30 下午2:23
# Author: Allen
import itertools
import re

dec2_pattern = re.compile(r"([0-9]+)[\.|:]([0-9]+\.[0-9]+)$", re.VERBOSE)


class ChineseDigitalProcessing(object):
    def __init__(self):
        """
        负责处理中文数字处理
        """
        pass

    def generalpronunciation(self, num, big=False, simp=True, o=False, twoalt=True):
        """
        Converts numbers to Chinese representations.
        `big`   : use financial characters.
        `simp`  : use simplified characters instead of traditional characters.
        `o`     : use 〇 for zero.
        `twoalt`: use 两/兩 for two when appropriate.
        Note that `o` and `twoalt` is ignored when `big` is used,
        and `twoalt` is ignored when `o` is used for formal representations.
        """
        # check num first
        nd = str(num)
        if abs(float(nd)) >= 1e50:
            raise ValueError('number out of range')
        elif 'e' in nd:
            raise ValueError('scientific notation is not supported')
        c_symbol = '正负点' if simp else '正負點'
        if o:  # formal
            twoalt = False
        if big:
            c_basic = '零壹贰叁肆伍陆柒捌玖' if simp else '零壹貳參肆伍陸柒捌玖'
            c_unit1 = '拾佰仟'
            c_twoalt = '贰' if simp else '貳'
        else:
            c_basic = '〇一二三四五六七八九' if o else '零一二三四五六七八九'
            c_unit1 = '十百千'
            if twoalt:
                c_twoalt = '两' if simp else '兩'
            else:
                c_twoalt = '二'
        c_unit2 = '万亿兆京垓秭穰沟涧正载' if simp else '萬億兆京垓秭穰溝澗正載'
        revuniq = lambda l: ''.join(k for k, g in itertools.groupby(reversed(l)))
        nd = str(num)
        result = []
        if nd[0] == '+':
            result.append(c_symbol[0])
        elif nd[0] == '-':
            result.append(c_symbol[1])
        if '.' in nd:
            integer, remainder = nd.lstrip('+-').split('.')
            zero_count = 0
            for i in range(len(remainder)):
                char = remainder[-(i + 1)]
                if char != "0":
                    break
                zero_count = i + 1
            if zero_count > 0:
                remainder = remainder[0:-zero_count]
        else:
            integer, remainder = nd.lstrip('+-'), None
        if int(integer):
            splitted = [integer[max(i - 4, 0):i]
                        for i in range(len(integer), 0, -4)]
            intresult = []
            for nu, unit in enumerate(splitted):
                # special cases
                if int(unit) == 0:  # 0000
                    intresult.append(c_basic[0])
                    continue
                elif nu > 0 and int(unit) == 2:  # 0002
                    intresult.append(c_twoalt + c_unit2[nu - 1])
                    continue
                ulist = []
                unit = unit.zfill(4)
                for nc, ch in enumerate(reversed(unit)):
                    if ch == '0':
                        if ulist:  # ???0
                            ulist.append(c_basic[0])
                    elif nc == 0:
                        ulist.append(c_basic[int(ch)])
                    elif nc == 1 and ch == '1' and unit[1] == '0':
                        # special case for tens
                        # edit the 'elif' if you don't like
                        # 十四, 三千零十四, 三千三百一十四
                        ulist.append(c_unit1[0])
                    elif nc > 1 and ch == '2':
                        ulist.append(c_twoalt + c_unit1[nc - 1])
                    else:
                        ulist.append(c_basic[int(ch)] + c_unit1[nc - 1])
                ustr = revuniq(ulist)
                if nu == 0:
                    intresult.append(ustr)
                else:
                    intresult.append(ustr + c_unit2[nu - 1])
            result.append(revuniq(intresult).strip(c_basic[0]))
        else:
            result.append(c_basic[0])
        if remainder:
            result.append(c_symbol[2])
            result.append(''.join(c_basic[int(ch)] for ch in remainder))
        result = ''.join(result)
        # if result.endswith("零十"):
        result = result.replace("零十", "零一十")
        return result

    def bitwisepronunciation(self, num):
        """
        :param num: (str) 需要转换的数字
        :return: (str) 中文数字按位读法
        """
        num = re.sub(r"\D^a-z^A_Z^\.", '', num)  # 删除非数字字符
        mapping = {'0': '零', '1': '一', '2': '二', '3': '三', '4': '四',
                   '5': '五', '6': '六', '7': '七', '8': '八', '9': '九', 'a':" A ", "b":" B ",
                   'c': " C ", "d": " D ",'e':" E ", "f":" F ",'g': " G ", "h": " H ",'i':" I ", "j":" J ",
                   "k":" K ", "l":" L ", 'm': " M ", "n": " N ", 'o': " O ", "p": " P ","q": " Q ",
                   "r": " R ", "s": " S ", 't': " T ", "u": " U ", 'v': " V ", "w": " W ", "x": " X ","y": " Y ", "z": " Z ",'.':"点"}
        mapping_ord = {ord(k.lower()): v for k, v in mapping.items()}
        num = num.translate(mapping_ord)
        return num

    def phoneprounciation(self, num):
        """

        :param num: (str) 需要转换的数字
        :return: (str) 中文电话号码读法
        """
        num = re.sub(r"\D", '', num)  # 删除非数字字符
        mapping = {'0': '零', '1': '幺', '2': '二', '3': '三', '4': '四',
                   '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'}
        mapping_ord = {ord(k): v for k, v in mapping.items()}
        num = num.translate(mapping_ord)
        return num

    def scoreprounciation(self, num):
        """

        :param num: 需要转换的数字
        :return:  比分读法
        """
        if "/" not in num:
            raise Exception("请输入分数形式")
        else:
            numerator, denominator = num.split("/")
            read_numerator = self.generalpronunciation(numerator)
            read_denominator = self.generalpronunciation(denominator)
            value = read_numerator + "比" + read_denominator
            return value

    def fractionprounciation(self, num):
        """

        :param num: 需要转换的数字
        :return:  分数读法
        """
        if "/" not in num:
            raise Exception("请输入分数形式")
        else:
            numerator, denominator = num.split("/")
            read_numerator = self.generalpronunciation(numerator)
            read_denominator = self.generalpronunciation(denominator)
            value = read_denominator + "分之" + read_numerator
            return value


class EnglishDigitalProcessing(object):

    def __init__(self):

        scale = [
            '', 'thousand', 'million', 'billion', 'trillion', 'quadrillion',
            'quintillion', 'sextillion', 'octillion', 'nonillion', 'decillion',
            'undecillion', 'duodecillion', 'tredecillion', 'quattuordecillion',
            'quindecillion', 'sexdecillion', 'septendecillion', 'octodecillion',
            'noverndecillion', 'vigintillion'
        ]

        cardinals = [
            '', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
            'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
            'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen',
        ]

        tensCardinals = [
            '', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy',
            'eighty', 'ninety',
        ]

        ordinals = [
            '', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth',
            'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth',
            'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth',
            'eighteenth', 'nineteenth'
        ]

        tensOrdinals = [
            '', '', 'twentieth', 'thirtieth', 'fortieth', 'fiftieth', 'sixtieth',
            'seventieth', 'eightieth', 'ninetieth',
        ]
        self._scale = scale
        self._cardinals = cardinals
        self._tensCardinals = tensCardinals
        self._ordinals = ordinals
        self._tensOrdinals = tensOrdinals

    def generalpronunciation(self, num):
        """
        :param num: 需要转换的数字
        :return:  英文数字一般读法
        """
        # clean up
        fraction = num.strip()
        if "." in fraction:
            parts = fraction.split(".")
            self._integer = parts[0]
            self._fraction = parts[1]
        else:
            self._integer = fraction
            self._fraction = None
        integer = self.number_to_cardinal(self._integer)
        if self._fraction is not None:
            fraction = self.bitwisepronunciation(self._fraction)
            if integer == "zero":
                integer = "zero point %s" % fraction
            else:
                integer = "%s point %s" % (integer, fraction)
        return integer.strip()

    def number_to_list(self, number):
        return re.findall(r'.{3}', number.zfill(len(number) // 3 * 3 + 3))

    def number_to_english(self, number):
        """

        :param num: 需要转换的数字
        :return:  转化为一般基数词读法
        """
        hundreds = int(number) // 100
        tens = int(number) % 100
        pre = self._cardinals[hundreds] + ' hundred' if hundreds else ''

        if tens < 20:
            post = self._cardinals[tens]
        else:
            post = self._tensCardinals[tens // 10]

            if not tens % 10 == 0:
                post = post + '-' + self._cardinals[tens % 10]

        if pre and post:
            return (pre + ' ' + post).strip()

        return (pre + post).strip()

    def number_to_cardinal(self, number):
        """

        :param num: 需要转换的数字
        :return:  将数字转化为基数词
        """
        if not number:
            return number
        if int(number) == 0:
            return "zero"
        number_list = self.number_to_list(number)[::-1]
        cardinal_list = []
        for i, number in enumerate(number_list):
            english_number = self.number_to_english(number)

            if english_number:
                cardinal_list.append(english_number + ' ' + self._scale[i])

        post = cardinal_list[0]
        pre = ' '.join(cardinal_list[1:][::-1])

        if pre and post:
            return (pre + ' ' + post).strip()

        return (pre + post).strip()

    def cardinal_to_ordinal(self, cardinal):
        """

        :param num: 需要转换的数字
        :return:  将基数词转化为序数词
        """
        words = cardinal.split()
        post = words[-1]

        if '-' in post:
            parts = post.split('-')
            pre = parts[0]
            post = parts[1]

        if post in self._cardinals:
            post = self._ordinals[self._cardinals.index(post)]
        elif post in self._tensCardinals:
            post = self._tensOrdinals[self._tensCardinals.index(post)]
        else:
            post = post + 'th'

        if 'pre' in vars():
            post = pre + '-' + post

        words[-1] = post

        if len(words) > 1:
            if '-' not in post:
                post = words.pop()
                pre = words.pop()
                last = pre + '-' + post
                words.append(last)

        return ' '.join(words).strip()

    def number_to_ordinal(self, number):
        """

        :param num: 需要转换的数字
        :return:  将数字转化为序数词
        """
        return self.cardinal_to_ordinal(self.number_to_cardinal(number)).strip()

    def bitwisepronunciation(self, num):
        """

        :param num: 需要转换的数字
        :return:  按位读法的结果 123 读one two three
        """
        num = re.sub(r"\D", '', num)  # 删除非数字

        txt = num
        num_han = {0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight',
                   9: 'nine'}
        value = ''.join(x for x in num if x in "0123456789")
        value = ' '.join(num_han.get(int(x)) if x in value else x for x in txt)
        return value

    def phoneprounciation(self, num):
        """

        :param num: 需要转换的数字
        :return:  根据电话号码读法转换 0 读字母O
        """
        num = re.sub(r"\D", '', num)  # 删除非数字
        txt = num
        num_han = {0: 'O', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight',
                   9: 'nine'}
        value = ''.join(x for x in num if x in "0123456789.")
        value = ' '.join(num_han.get(int(x)) if x in value else x for x in txt)
        return value

    def scoreprounciation(self, num):
        """

        :param num: 需要转换的数字
        :return:  根据比分读法转换
        """
        if "/" not in num:
            raise Exception("请输入分数形式")
        else:
            numerator, denominator = num.split("/")
            if numerator == "0":
                read_numerator = "nil"
            else:
                read_numerator = self.generalpronunciation(numerator)
            if denominator == '0':
                read_denominator = "nil"
            else:
                read_denominator = self.generalpronunciation(denominator)
            value = read_numerator + " to " + read_denominator
            return value

    def fractionprounciation(self, num):
        """

        :param num: 需要转换的数字
        :return:  根据分数读法转换
        """
        if "/" not in num:
            raise Exception("请输入分数形式")
        else:
            # num = num.replace("/","-")
            numerator, denominator = num.split("/")
            read_numerator = self.number_to_cardinal(numerator)
            read_denominator = self.cardinal_to_ordinal(self.number_to_cardinal(denominator))
            return ' '.join([read_numerator, read_denominator])

    def expand_NDIG(self, w):
        """Expand digit sequences to a series of words."""
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        num_words = ['zero', 'one', 'two', 'three', 'four', 'five',
                     'six', 'seven', 'eight', 'nine']
        str2 = ''
        for n in w:
            if n.isdigit():
                str2 += num_words[numbers.index(n)]
                str2 += " "
            elif n == '.':
                str2 += 'dot'
                str2 += ' '
            else:
                str2 += ''
        return str2[:-1]

    def expand_NUM(self, n):
        """
        Return n as an cardinal in words.
        :param n: (str) 英文数字
        :return: (str)
        """

        if len(n) > 0:
            if n[-1] == 's':
                if len(n) > 1 and n[-2:] == "'s":
                    str = ''
                    str += self.expand_NUM(n[:-2])
                    str += "'s"
                else:
                    str = ''
                    if self.expand_NUM(n[:-1])[-1] == 'y':
                        str += self.expand_NUM(n[:-1])[:-1]
                        str += 'ies'
                    else:
                        str += self.expand_NUM(n[:-1])
                        str += 's'
                return str

        if dec2_pattern.match(n):
            str2 = ''
            str2 += (self.expand_NUM(dec2_pattern.match(n).group(1)) + " "
                     + self.expand_NUM(dec2_pattern.match(n).group(2)))
            return str2

        if n.startswith('.'):
            return "point " + self.expand_NDIG(n[1:])

        ones_C = [
            "zero", "one", "two", "three", "four", "five", "six", "seven",
            "eight", "nine", "ten", "eleven", "twelve", "thirteen",
            "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
            "nineteen"
        ]

        tens_C = [
            "zero", "ten", "twenty", "thirty", "forty", "fifty", "sixty",
            "seventy", "eighty", "ninety"
        ]

        large = [
            "", "thousand", "million", "billion", "trillion", "quadrillion",
            "quintillion", "sextillion", "septillion", "octillion",
            "nonillion", "decillion", "undecillion", "duodecillion",
            "tredecillion", "quattuordecillion", "sexdecillion",
            "septendecillion", "octodecillion", "novemdecillion",
            "vigintillion"
        ]

        def subThousand(n):
            """Convert a cardinal to words for numbers less than a thousand."""
            if n <= 19:
                return ones_C[n]
            elif n <= 99:
                q, r = divmod(n, 10)
                return tens_C[q] + (" " + subThousand(r) if r else "")
            else:
                q, r = divmod(n, 100)
                return (ones_C[q]
                        + " hundred"
                        + (" and " + subThousand(r) if r else ""))

        def splitByThousands(n):
            "Return reversed digits of n in groups of 3."""
            res = []
            while n:
                n, r = divmod(n, 1000)
                res.append(r)
            return res

        def thousandUp(n):
            """Return cardinal greater than a thousand in words."""
            list1 = []
            for i, z in enumerate(splitByThousands(n)):
                if i and z:
                    list1.insert(0, subThousand(z) + " " + large[i])
                elif z:
                    list1.insert(0, subThousand(z))
            return ", ".join(list1)

        def decimal(n):
            """Returns pronounced words with n as rhs of a decimal"""
            if n == '00':
                out = ''
            else:
                out = ' point'
                for lt in n:
                    out += ' {}'.format(ones_C[int(lt)])
            return out

        n_clean = ''
        for i in range(len(n)):
            if not i:
                if n[i].isdigit() or n[i] == '-':
                    n_clean += n[i]
                elif n[i] == '+':
                    return "plus " + self.expand_NUM(n[1:])
            else:
                if n[i].isdigit() or n[i] == '.':
                    n_clean += n[i]
        if '.' in n_clean:
            dot = n_clean.find('.')
            whole, part = n_clean[:dot], n_clean[dot + 1:]
            return self.expand_NUM(whole) + decimal(part)
        num = int(n_clean)
        if num == 0:
            if '-' in n_clean:
                return 'minus zero'
            else:
                return "zero"
        else:
            w = ("minus " if num < 0 else "") + thousandUp(abs(num))
            if len(n) < 4:
                return w
            else:
                if n[-3] == '0' and n[-2:] != '00':
                    ind = w.rfind(",")
                    return w[:ind] + " and" + w[ind + 1:]
                else:
                    return w


class NumberNormalize(object):

    def __init__(self):
        """

        :param num:  要转换的数字
        :param language: 中英文语言类型
        :param style:  转换风格
        """
        self.chinese_process = ChineseDigitalProcessing()
        self.english_process = EnglishDigitalProcessing()

    def call(self, num, language, style):
        """
        :param num: (str)
        :param language: (str) en|cn
        :param style: (str) digits|ordinal|score|fraction|phone
            language=en:
                bitwise：前面的数字是数码读法，如：123[=digits] -> 一二三
                ordinal：前面的数字是数值读法，如：123[=ordinal] -> 一百二十三
                phone：前面的数字是电话号码读法，如：123[=phone] -> 幺二三
                score：前面的数字是分数读法，如：4/5[=score] -> 四比五
                fraction：前面的数字是小数读法，如：4/5[=fraction] -> 五分之四
            laguage=cn:
                TODO
        :return (str)
        """
        self.num = num
        self.language = language
        self.style = style

        self.result = None
        if self.language == "en":
            if self.style == "ordinal":
                self.result = self.english_process.expand_NUM(self.num)
            elif self.style == "bitwise":
                self.result = self.english_process.bitwisepronunciation(self.num)
            elif self.style == "phone":
                self.result = self.english_process.phoneprounciation(self.num)
            elif self.style == "score":
                self.result = self.english_process.scoreprounciation(self.num)
            elif self.style == "fraction":
                self.result = self.english_process.fractionprounciation(self.num)
        else:
            if self.style == "ordinal":
                self.result = self.chinese_process.generalpronunciation(self.num)
            elif self.style == "bitwise":
                self.result = self.chinese_process.bitwisepronunciation(self.num)
            elif self.style == "phone":
                self.result = self.chinese_process.phoneprounciation(self.num)
            elif self.style == "score":
                self.result = self.chinese_process.scoreprounciation(self.num)
            elif self.style == "fraction":
                self.result = self.chinese_process.fractionprounciation(self.num)
        return self.result


if __name__ == '__main__':
    num = NumberNormalize()
    res = num.call("-0.987654", 'en', 'ordinal')
    print(res)
    print(res == "一千两百五十八亿零三千三百二十一")
