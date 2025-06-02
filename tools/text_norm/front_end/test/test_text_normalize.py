# -*- coding: utf-8 -*-
# Create Time: 2020/10/12 上午10:42
# Author: Allen

import unittest
from service.modules.preprocess.front_end.normalize.text_normalize import TextNormalize


class TestTextNormalize(unittest.TestCase):
    def setUp(self) -> None:
        self.tn = TextNormalize()

    def test_text_normalize_CN(self):
        lang = "CN"  # 无英文小写字母

        # 无特殊字符
        self.assertEqual(self.tn.call("TTS测试文本", lang), "T T S 测试文本")

        # 数字搭配特殊符号
        self.assertEqual(self.tn.call("TTS测试￥12.5文本", lang), "T T S 测试十二点五元文本")
        self.assertEqual(self.tn.call("TTS测试12.5%文本", lang), "T T S 测试百分之十二点五文本")

        # 默认数字
        self.assertEqual(self.tn.call("TTS测试123文本", lang), "T T S 测试一百二十三文本")
        self.assertEqual(self.tn.call("TTS测试123.123文本", lang), "T T S 测试一百二十三点一二三文本")
        self.assertEqual(self.tn.call("TTS测试0.123文本", lang), "T T S 测试零点一二三文本")
        self.assertEqual(self.tn.call("TTS测试00.123文本", lang), "T T S 测试零点一二三文本")
        self.assertEqual(self.tn.call("TTS测试00.00文本", lang), "T T S 测试零点零零文本")

        # 自定义标识符
        ## 自定义数字标识符
        self.assertEqual(self.tn.call("TTS测试(@123.123)文本", lang), "T T S 测试一百二十三点一二三文本")
        self.assertEqual(self.tn.call("TTS测试($123.123)文本", lang), "T T S 测试一二三一二三文本")
        self.assertEqual(self.tn.call("TTS测试(#123.123)文本", lang), "T T S 测试幺二三幺二三文本")
        ## 自定义人名标识符
        self.assertEqual(self.tn.call("TTS测试文本，来自{单单单}", lang), "T T S 测试文本 ， 来自单《ｓｈａｎ４》《＃０》单《＃０》单《＃０》")
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2>单单}", lang), "T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃０》单《＃０》单《＃０》")
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2>单<wang2>单<wang2>}", lang),
                         "T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃０》单《ｗａｎｇ２》《＃０》单《ｗａｎｇ２》《＃０》")
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2><#1>单<wang2><#2>单<wang2><#3>}", lang),
                         "T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《ｗａｎｇ２》《＃２》单《ｗａｎｇ２》《＃３》")
        ## 自定义拼音标识符
        self.assertEqual(self.tn.call("TTS测<wang2>试文本<wang2>，来<wang2>自单单单<wang2>", lang),
                         "T T S 测《ｗａｎｇ２》试文本《ｗａｎｇ２》 ， 来《ｗａｎｇ２》自单单单《ｗａｎｇ２》")
        ## 自定义韵律标识符
        self.assertEqual(self.tn.call("TTS测<#0>试文本<#1>，来<#2>自单单单<#3>", lang), "T T S 测《＃０》试文本《＃１》 ， 来《＃２》自单单单《＃３》")
        ## 自定义停顿时长标识符
        self.assertEqual(self.tn.call("<&100>TTS测试文本<&200>，来自单单单<&300>", lang), "《＆１００》 T T S 测试文本《＆２００》 ， 来自单单单《＆３００》")
        self.assertEqual(self.tn.call("<&100>TTS测试文本，<&200>，来自单单单<&300>", lang), "《＆１００》 T T S 测试文本 ， 来自单单单《＆３００》")
        self.assertEqual(self.tn.call("<&100>TTS测试<&200>文本，<&200>，来自单单单<&300>", lang),
                         "《＆１００》 T T S 测试文本 ， 来自单单单《＆３００》")

        # 随机测试
        self.assertEqual(self.tn.call("<&100>TTS测<1>试文<A>本<&200>，来自单单单<&300>", lang),
                         "《＆１００》 T T S 测 、 一 、 试文 、 A 、 本《＆２００》 ， 来自单单单《＆３００》")
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2><#1>单(@100)单}", lang),
                         "T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》一《＃０》百《＃０》单《＃０》")
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<#1><wang2>单(#100)单}", lang),
                         "T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》幺《＃０》零《＃０》零《＃０》单《＃０》")
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2><#1>单<&100>单}", lang),
                         "T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》单《＃０》")

    def test_text_normalize_CN_EN(self):
        lang = "CN_EN"
        # 无特殊字符
        self.assertEqual(self.tn.call("TTS测试文本", lang), "T T S 测试文本")

        # 默认数字
        self.assertEqual(self.tn.call("TTS测试123文本", lang), "T T S 测试一百二十三文本")
        self.assertEqual(self.tn.call("TTS测试123.123文本", lang), "T T S 测试一百二十三点一二三文本")
        self.assertEqual(self.tn.call("TTS测试0.123文本", lang), "T T S 测试零点一二三文本")
        self.assertEqual(self.tn.call("TTS测试00.123文本", lang), "T T S 测试零点一二三文本")
        self.assertEqual(self.tn.call("TTS测试00.00文本", lang), "T T S 测试零点零零文本")

        # 数字+标点
        self.assertEqual(self.tn.call("TTS测试123. 123文本", lang), "T T S 测试一百二十三 . 一百二十三文本")

        # 自定义标识符
        # # 自定义数字标识符
        self.assertEqual(self.tn.call("TTS测试(@123.123)文本", lang), "T T S 测试一百二十三点一二三文本")
        self.assertEqual(self.tn.call("TTS测试($123.123)文本", lang), "T T S 测试一二三一二三文本")
        self.assertEqual(self.tn.call("TTS测试(#123.123)文本", lang), "T T S 测试幺二三幺二三文本")
        # # 自定义人名标识符
        self.assertEqual(self.tn.call("TTS测试文本，来自{单单单}", lang), "T T S 测试文本 ， 来自单《ｓｈａｎ４》《＃０》单《＃０》单《＃０》")
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2>单单}", lang), "T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃０》单《＃０》单《＃０》")
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2>单<wang2>单<wang2>}", lang),
                         "T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃０》单《ｗａｎｇ２》《＃０》单《ｗａｎｇ２》《＃０》")
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2><#1>单<wang2><#2>单<wang2><#3>}", lang),
                         "T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《ｗａｎｇ２》《＃２》单《ｗａｎｇ２》《＃３》")
        # # 自定义拼音标识符
        self.assertEqual(self.tn.call("TTS测<wang2>试文本<wang2>，来<wang2>自单单单<wang2>", lang),
                         "T T S 测《ｗａｎｇ２》试文本《ｗａｎｇ２》 ， 来《ｗａｎｇ２》自单单单《ｗａｎｇ２》")
        # # 自定义韵律标识符
        self.assertEqual(self.tn.call("TTS测<#0>试文本<#1>，来<#2>自单单单<#3>", lang), "T T S 测《＃０》试文本《＃１》 ， 来《＃２》自单单单《＃３》")
        ## 自定义停顿时长标识符
        self.assertEqual(self.tn.call("<&100>TTS测试文本<&200>，来自单单单<&300>", lang), "《＆１００》 T T S 测试文本《＆２００》 ， 来自单单单《＆３００》")
        self.assertEqual(self.tn.call("<&100>TTS测<&200>试文本，来自单单单<&300>", lang), "《＆１００》 T T S 测试文本 ， 来自单单单《＆３００》")
        self.assertEqual(self.tn.call("<&100>TTS测试文本，<&200>，来自单单单<&300>", lang), "《＆１００》 T T S 测试文本 ， 来自单单单《＆３００》")
        self.assertEqual(self.tn.call("<&100>TTS测试<&200>文本，<&200>，来自单单单<&300>", lang),
                         "《＆１００》 T T S 测试文本 ， 来自单单单《＆３００》")

        # 随机测试
        # # CN
        self.assertEqual(self.tn.call("<&100>TTS测<1>试文<A>本<&200>，来自单单单<&300>", lang),
                         "《＆１００》 T T S 测 、 一 、 试文 、 A 、 本《＆２００》 ， 来自单单单《＆３００》")
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2><#1>单(@100)单}", lang),
                         "T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》一《＃０》百《＃０》单《＃０》")
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<#1><wang2>单(#100)单}", lang),
                         "T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》幺《＃０》零《＃０》零《＃０》单《＃０》")
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2><#1>单<&100>单}", lang),
                         "T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》单《＃０》")
        self.assertEqual(self.tn.call("T1TNS测试文本测试30~40文本，来自{单<wang2><#1>单(@100)单}", lang),
                         "T 一 T N S 测试文本测试三十至四十文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》一《＃０》百《＃０》单《＃０》")
        self.assertEqual(self.tn.call("T1TNS测试文本测试30.1~40.1文本，来自{单<wang2><#1>单(@100)单}", lang),
                         "T 一 T N S 测试文本测试三十点一至四十点一文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》一《＃０》百《＃０》单《＃０》")
        self.assertEqual(self.tn.call("小保方晴子读博时所属的研究科科长则上缴了自己三个月工资津贴的20%", lang), "小保方晴子读博时所属的研究科科长则上缴了自己三个月工资津贴的百分之二十")

        # # CN_EN
        self.assertEqual(self.tn.call("T1TNS测试文本，hello 2020, happy new year<&100>", lang),
                         "T one T N S 测试文本 ， hello two thousand and twenty , happy new year《＆１００》")
        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>，hello 2020, happy new year", lang),
                         "T one T N S 测试文本《ｂｅｎ２》 ， hello two thousand and twenty , happy new year")
        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>，hello 2020<#2>, happy new year", lang),
                         "T one T N S 测试文本《ｂｅｎ２》 ， hello two thousand and twenty 《＃２》 , happy new year")
        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>，hello 2020<#2>, happy<ni2> new year", lang),
                         "T one T N S 测试文本《ｂｅｎ２》 ， hello two thousand and twenty 《＃２》 , happy new year")

        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>，hello 2020<#2>, happy ($314) new year", lang),
                         "T one T N S 测试文本《ｂｅｎ２》 ， hello two thousand and twenty 《＃２》 , happy three one four new year")
        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>，($314) hello 2020<#2>, happy new year", lang),
                         "T one T N S 测试文本《ｂｅｎ２》 ， 三一四 hello two thousand and twenty 《＃２》 , happy new year")
        self.assertEqual(self.tn.call("($314) T1TNS测试文本<ben2>，hello 2020<#2>, happy ($314) new year", lang),
                         "three one four T one T N S 测试文本《ｂｅｎ２》 ， hello two thousand and twenty 《＃２》 , happy three one four new year")
        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>，hello 2020<#2>, happy ($314) new year ($314)", lang),
                         "T one T N S 测试文本《ｂｅｎ２》 ， hello two thousand and twenty 《＃２》 , happy three one four new year three one four")
        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>， a hello 2020<#2>, happy ($314) new year ($314)", lang),
                         "T one T N S 测试文本《ｂｅｎ２》 ， a hello two thousand and twenty 《＃２》 , happy three one four new year three one four")
        self.assertEqual(self.tn.call("ABC<&100>TTS测试<&200>文本<&200>，来自单abc 20~30 efg 单单<&300>DE<&100>", lang),
                         "A B C T T S 测试文本《＆２００》 ， 来自单abc twenty to thirty efg 单单 D E 《＆１００》")
        self.assertEqual(self.tn.call("ABC<&100>TTS测试<&200>文本<&200>，来自单20~30.单单<&300>DE<&100>", lang),
                         "A B C T T S 测试文本《＆２００》 ， 来自单二十至三十 . 单单 D E 《＆１００》")
        self.assertEqual(self.tn.call("ABC<&100>TTS测试<&200>文本<&200>，来自单abc 20~30单单<&300>DE<&100>", lang),
                         "A B C T T S 测试文本《＆２００》 ， 来自单abc 二十至三十单单 D E 《＆１００》")
        self.assertEqual(self.tn.call("ABC<&100>TTS测试<&200>文本<&200>，来自单20~30 efg 单单<&300>DE<&100>", lang),
                         "A B C T T S 测试文本《＆２００》 ， 来自单二十至三十 efg 单单 D E 《＆１００》")

    def test_text_normalzie_EN(self):
        lang = "EN"
        self.assertEqual(self.tn.call(
            "Huawei is among the top 20 largest corporate investors in Canada and employs over 1,200 people there",
            lang),
            "huawei is among the top twenty largest corporate investors in canada and employs over one thousand , two hundred people there")
        self.assertEqual(self.tn.call(
            "Huawei is among the top ($20) largest corporate investors in Canada and employs over 1,200 people there",
            lang),
            "huawei is among the top two zero largest corporate investors in canada and employs over one thousand , two hundred people there")
        self.assertEqual(self.tn.call(
            "Huawei is among the top (@20) largest corporate investors in Canada and employs over 1,200 people there",
            lang),
            "huawei is among the top twenty largest corporate investors in canada and employs over one thousand , two hundred people there")
        self.assertEqual(self.tn.call(
            "Huawei is among the top (#20) largest corporate investors in Canada and employs over 1,200 people there",
            lang),
            "huawei is among the top two O largest corporate investors in canada and employs over one thousand , two hundred people there")

        self.assertEqual(self.tn.call("HUAWEI Canada and employs over 1,200 people there", lang),
                         "H U A W E I canada and employs over one thousand , two hundred people there")
        self.assertEqual(self.tn.call("Huawei CANADA and employs over 1,200 people there", lang),
                         "huawei C A N A D A and employs over one thousand , two hundred people there")
        self.assertEqual(self.tn.call("Huawei Canada and employs over 1,200 people THERE", lang),
                         "huawei canada and employs over one thousand , two hundred people T H E R E")

        self.assertEqual(self.tn.call(
            "Yan made the remarks during a panel discussion on 'Investment in Canada' organized during the Canada China Business Council's 42nd Annual General Meeting Business Forum held in Beijing",
            lang),
            "yan made the remarks during a panel discussion on investment in canada organized during the canada china business council's forty second annual general meeting business forum held in beijing")


if __name__ == '__main__':
    unittest.main()
