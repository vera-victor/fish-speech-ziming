# -*- coding: utf-8 -*-
# Create Time: 2020/10/14 下午1:36
# Author: Allen

import unittest
from service.modules.preprocess.front_end.normalize.number_normalize import NumberNormalize


class TestNumberNormalize(unittest.TestCase):
    def setUp(self) -> None:
        self.num_norm = NumberNormalize()

    def test_cn_num(self):
        lang = 'cn'
        self.assertEqual(self.num_norm.call("1", lang, 'ordinal'), "一")
        self.assertEqual(self.num_norm.call("15", lang, 'ordinal'), "十五")
        self.assertEqual(self.num_norm.call("20", lang, 'ordinal'), "二十")
        self.assertEqual(self.num_norm.call("23", lang, 'ordinal'), "二十三")
        self.assertEqual(self.num_norm.call("100", lang, 'ordinal'), "一百")
        self.assertEqual(self.num_norm.call("101", lang, 'ordinal'), "一百零一")
        self.assertEqual(self.num_norm.call("110", lang, 'ordinal'), "一百一十")
        self.assertEqual(self.num_norm.call("111", lang, 'ordinal'), "一百一十一")
        self.assertEqual(self.num_norm.call("1000", lang, 'ordinal'), "一千")
        self.assertEqual(self.num_norm.call("10321", lang, 'ordinal'), "一万零三百二十一")
        self.assertEqual(self.num_norm.call("1031", lang, 'ordinal'), "一千零三十一")
        self.assertEqual(self.num_norm.call("10021", lang, 'ordinal'), "一万零二十一")
        self.assertEqual(self.num_norm.call("10321", lang, 'ordinal'), "一万零三百二十一")
        self.assertEqual(self.num_norm.call("11321", lang, 'ordinal'), "一万一千三百二十一")
        self.assertEqual(self.num_norm.call("30150000", lang, 'ordinal'), "三千零一十五万")
        self.assertEqual(self.num_norm.call("35680101", lang, 'ordinal'), "三千五百六十八万零一百零一")
        self.assertEqual(self.num_norm.call("5030750622", lang, 'ordinal'), "五十亿三千零七十五万零六百二十二")
        self.assertEqual(self.num_norm.call("1330150312", lang, 'ordinal'), "十三亿三千零一十五万零三百一十二")
        self.assertEqual(self.num_norm.call("125800000000", lang, 'ordinal'), "一千两百五十八亿")
        self.assertEqual(self.num_norm.call("30150312", lang, 'ordinal'), "三千零一十五万零三百一十二")
        self.assertEqual(self.num_norm.call("1258000000000000", lang, 'ordinal'), "一千两百五十八兆")
        self.assertEqual(self.num_norm.call("3321", lang, 'ordinal'), "三千三百二十一")
        self.assertEqual(self.num_norm.call("331", lang, 'ordinal'), "三百三十一")
        self.assertEqual(self.num_norm.call("21", lang, 'ordinal'), "二十一")
        self.assertEqual(self.num_norm.call("321", lang, 'ordinal'), "三百二十一")
        self.assertEqual(self.num_norm.call("125800003321", lang, 'ordinal'), "一千两百五十八亿零三千三百二十一")
        self.assertEqual(self.num_norm.call("200", lang, 'ordinal'), "两百")
        self.assertEqual(self.num_norm.call("2222", lang, 'ordinal'), "两千两百二十二")
        self.assertEqual(self.num_norm.call("222000222", lang, 'ordinal'), "两亿两千两百万零两百二十二")
        self.assertEqual(self.num_norm.call("307830150312", lang, 'ordinal'), "三千零七十八亿三千零一十五万零三百一十二")

        self.assertEqual(self.num_norm.call("18.91", lang, 'ordinal'), "十八点九一")
        self.assertEqual(self.num_norm.call("0.123", lang, 'ordinal'), "零点一二三")
        self.assertEqual(self.num_norm.call("0", lang, 'ordinal'), "零")
        self.assertEqual(self.num_norm.call("1099.66", lang, 'ordinal'), "一千零九十九点六六")

    def test_en_num(self):
        lang = 'en'
        self.assertEqual(self.num_norm.call("0", lang, 'ordinal'), "zero")
        self.assertEqual(self.num_norm.call("1", lang, 'ordinal'), "one")
        self.assertEqual(self.num_norm.call("2", lang, 'ordinal'), "two")
        self.assertEqual(self.num_norm.call("3", lang, 'ordinal'), "three")
        self.assertEqual(self.num_norm.call("4", lang, 'ordinal'), "four")
        self.assertEqual(self.num_norm.call("5", lang, 'ordinal'), "five")
        self.assertEqual(self.num_norm.call("6", lang, 'ordinal'), "six")
        self.assertEqual(self.num_norm.call("7", lang, 'ordinal'), "seven")
        self.assertEqual(self.num_norm.call("8", lang, 'ordinal'), "eight")
        self.assertEqual(self.num_norm.call("9", lang, 'ordinal'), "nine")
        self.assertEqual(self.num_norm.call("10", lang, 'ordinal'), "ten")
        self.assertEqual(self.num_norm.call("11", lang, 'ordinal'), "eleven")
        self.assertEqual(self.num_norm.call("12", lang, 'ordinal'), "twelve")
        self.assertEqual(self.num_norm.call("13", lang, 'ordinal'), "thirteen")
        self.assertEqual(self.num_norm.call("14", lang, 'ordinal'), "fourteen")
        self.assertEqual(self.num_norm.call("15", lang, 'ordinal'), "fifteen")
        self.assertEqual(self.num_norm.call("16", lang, 'ordinal'), "sixteen")
        self.assertEqual(self.num_norm.call("17", lang, 'ordinal'), "seventeen")
        self.assertEqual(self.num_norm.call("18", lang, 'ordinal'), "eighteen")
        self.assertEqual(self.num_norm.call("19", lang, 'ordinal'), "nineteen")
        self.assertEqual(self.num_norm.call("20", lang, 'ordinal'), "twenty")
        self.assertEqual(self.num_norm.call("21", lang, 'ordinal'), "twenty one")

        self.assertEqual(self.num_norm.call("29", lang, 'ordinal'), "twenty nine")
        self.assertEqual(self.num_norm.call("99", lang, 'ordinal'), "ninety nine")
        self.assertEqual(self.num_norm.call("100", lang, 'ordinal'), "one hundred")
        self.assertEqual(self.num_norm.call("101", lang, 'ordinal'), "one hundred and one")
        self.assertEqual(self.num_norm.call("110", lang, 'ordinal'), "one hundred and ten")
        self.assertEqual(self.num_norm.call("111", lang, 'ordinal'), "one hundred and eleven")
        self.assertEqual(self.num_norm.call("900", lang, 'ordinal'), "nine hundred")
        self.assertEqual(self.num_norm.call("999", lang, 'ordinal'), "nine hundred and ninety nine")
        self.assertEqual(self.num_norm.call("1000", lang, 'ordinal'), "one thousand")
        self.assertEqual(self.num_norm.call("1001", lang, 'ordinal'), "one thousand and one")
        self.assertEqual(self.num_norm.call("1010", lang, 'ordinal'), "one thousand and ten")
        self.assertEqual(self.num_norm.call("1100", lang, 'ordinal'), "one thousand, one hundred")
        self.assertEqual(self.num_norm.call("2000", lang, 'ordinal'), "two thousand")
        self.assertEqual(self.num_norm.call("10000", lang, 'ordinal'), "ten thousand")
        self.assertEqual(self.num_norm.call("100000", lang, 'ordinal'), "one hundred thousand")
        self.assertEqual(self.num_norm.call("100001", lang, 'ordinal'), "one hundred thousand and one")
        self.assertEqual(self.num_norm.call("100010", lang, 'ordinal'), "one hundred thousand and ten")
        self.assertEqual(self.num_norm.call("100100", lang, 'ordinal'), "one hundred thousand, one hundred")
        self.assertEqual(self.num_norm.call("101000", lang, 'ordinal'), "one hundred and one thousand")
        self.assertEqual(self.num_norm.call("1010000", lang, 'ordinal'), "one million, ten thousand")
        self.assertEqual(self.num_norm.call("1010001", lang, 'ordinal'), "one million, ten thousand and one")
        self.assertEqual(self.num_norm.call("123456", lang, 'ordinal'),
                         "one hundred and twenty three thousand, four hundred and fifty six")
        self.assertEqual(self.num_norm.call("0123456", lang, 'ordinal'),
                         "one hundred and twenty three thousand, four hundred and fifty six")
        self.assertEqual(self.num_norm.call("1234567", lang, 'ordinal'),
                         "one million, two hundred and thirty four thousand, five hundred and sixty seven")
        self.assertEqual(self.num_norm.call("12345678", lang, 'ordinal'),
                         "twelve million, three hundred and forty five thousand, six hundred and seventy eight")
        self.assertEqual(self.num_norm.call("1234567890", lang, 'ordinal'),
                         "one billion, two hundred and thirty four million, five hundred and sixty seven thousand, eight hundred and ninety")
        self.assertEqual(self.num_norm.call("123456789012345", lang, 'ordinal'),
                         "one hundred and twenty three trillion, four hundred and fifty six billion, seven hundred and eighty nine million, twelve thousand, three hundred and forty five")
        self.assertEqual(self.num_norm.call("12345678901234567890", lang, 'ordinal'),
                         "twelve quintillion, three hundred and forty five quadrillion, six hundred and seventy eight trillion, nine hundred and one billion, two hundred and thirty four million, five hundred and sixty seven thousand, eight hundred and ninety")

        self.assertEqual(self.num_norm.call("0.987654", lang, 'ordinal'), "zero point nine eight seven six five four")
        self.assertEqual(self.num_norm.call(".987654", lang, 'ordinal'), "point nine eight seven six five four")
        self.assertEqual(self.num_norm.call("9.87654", lang, 'ordinal'), "nine point eight seven six five four")
        self.assertEqual(self.num_norm.call("98.7654", lang, 'ordinal'), "ninety eight point seven six five four")
        self.assertEqual(self.num_norm.call("987.654", lang, 'ordinal'),
                         "nine hundred and eighty seven point six five four")
        self.assertEqual(self.num_norm.call("9876.54", lang, 'ordinal'),
                         "nine thousand, eight hundred and seventy six point five four")
        self.assertEqual(self.num_norm.call("98765.4", lang, 'ordinal'),
                         "ninety eight thousand, seven hundred and sixty five point four")
        self.assertEqual(self.num_norm.call("98765.", lang, 'ordinal'),
                         "ninety eight thousand, seven hundred and sixty five point")

        self.assertEqual(self.num_norm.call("0123456789", lang, 'bitwise'),
                         'zero one two three four five six seven eight nine')

        self.assertEqual(self.num_norm.call("0123456789", lang, 'phone'),
                         'O one two three four five six seven eight nine')


if __name__ == '__main__':
    unittest.main()
