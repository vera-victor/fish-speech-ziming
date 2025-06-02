# -*- coding: utf-8 -*-
# Create Time: 2020/10/15 上午10:33
# Author: Allen

import unittest

from service.modules.preprocess.front_end.tts_front_end_debug import FrontEnd


class TestFrontEnd(unittest.TestCase):
    def setUp(self) -> None:
        self.tn = FrontEnd()

    def test_cn_input(self):
        """中文字符+[英文大写字母]+[数字]+[自定义标识符]"""
        lang = 'CN'
        self.assertEqual(self.tn.call("", lang), [])

        self.assertEqual(self.tn.call("据英国《每日<ri1>邮报》10月6日报道！", lang), ['据英国 、 每日《ｒｉ１》邮报 、 十月六日报道'])
        self.assertEqual(self.tn.call("(完) (编译 张明钧", lang), ['完 、 编译张明钧'])

        self.assertEqual(self.tn.call("，，！，TTS前端文本测试文本。", lang), ['T T S 前端文本测试文本'])
        self.assertEqual(self.tn.call("TTS前端，，！，文本测试文本。", lang), ['T T S 前端', '文本测试文本'])
        self.assertEqual(self.tn.call("TTS前端文本测试文本，，！，", lang), ['T T S 前端文本测试文本'])
        self.assertEqual(self.tn.call("，，！，TTS前端文，，！，本测试文本，，！，", lang), ['T T S 前端文', '本测试文本'])

        self.assertEqual(self.tn.call("TTS前端123,001文本测试文本.", lang), ['T T S 前端十二万三千零一文本测试文本'])
        self.assertEqual(self.tn.call("TTS前端123,文本测试文本.", lang), ['T T S 前端一百二十三 ， 文本测试文本'])
        self.assertEqual(self.tn.call("TTS前端,001文本测试文本.", lang), ['T T S 前端 ， 一文本测试文本'])

        self.assertEqual(self.tn.call("TTS前端123.001文本测试文本.", lang), ['T T S 前端一百二十三点零零一文本测试文本'])
        self.assertEqual(self.tn.call("TTS前端 123.001 文本测试文本.", lang), ['T T S 前端一百二十三点零零一文本测试文本'])
        self.assertEqual(self.tn.call("TTS前端 123.001文本测试文本.", lang), ['T T S 前端一百二十三点零零一文本测试文本'])
        self.assertEqual(self.tn.call("TTS前端123.001 文本测试文本.", lang), ['T T S 前端一百二十三点零零一文本测试文本'])
        self.assertEqual(self.tn.call("TTS前端123.文本测试文本.", lang), ['T T S 前端一百二十三', '文本测试文本'])
        self.assertEqual(self.tn.call("TTS前端.001文本测试文本.", lang), ['T T S 前端', '一文本测试文本'])

        self.assertEqual(self.tn.call("<&200>TTS{前<qian2>端}($123.001)文<#1>本(@123.001)测试(#123.001)文本<&100>.", lang),
                         ['《＆２００》 T T S 前《ｑｉａｎ２》《＃０》端《＃０》一二三零零一文《＃１》本一百二十三点零零一测试幺二三零零幺文本《＆１００》'])

        self.assertEqual(self.tn.call("TTS测试文本！", lang), ['T T S 测试文本'])
        self.assertEqual(self.tn.call("TTS测试￥12.5文本。", lang), ['T T S 测试十二点五元文本'])
        self.assertEqual(self.tn.call("TTS测试12.5%文本", lang), ['T T S 测试百分之十二点五文本'])
        self.assertEqual(self.tn.call("TTS测试 12.5%文本", lang), ['T T S 测试百分之十二点五文本'])

        self.assertEqual(self.tn.call("TTS测试(@123.123)文本！", lang), ['T T S 测试一百二十三点一二三文本'])
        self.assertEqual(self.tn.call("TTS测试($123.123)文本！", lang), ['T T S 测试一二三一二三文本'])
        self.assertEqual(self.tn.call("TTS测试(#123.123)文本！", lang), ['T T S 测试幺二三幺二三文本'])
        self.assertEqual(self.tn.call("TTS测试文本！", lang), ['T T S 测试文本'])
        self.assertEqual(self.tn.call("20年前！", lang), ['二十年前'])
        self.assertEqual(self.tn.call("2012年前！", lang), ['二零一二年前'])

        ## 自定义人名标识符
        self.assertEqual(self.tn.call("TTS测试文本，来自{单单单}", lang), ["T T S 测试文本 ， 来自单《ｓｈａｎ４》《＃０》单《＃０》单《＃０》"])
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2>单单}", lang), ["T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃０》单《＃０》单《＃０》"])
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2>单<wang2>单<wang2>}", lang),
                         ["T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃０》单《ｗａｎｇ２》《＃０》单《ｗａｎｇ２》《＃０》"])
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2><#1>单<wang2><#2>单<wang2><#3>}", lang),
                         ["T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《ｗａｎｇ２》《＃２》单《ｗａｎｇ２》《＃３》"])
        ## 自定义拼音标识符
        self.assertEqual(self.tn.call("TTS测<wang2>试文本<wang2>，来<wang2>自单单单<wang2>", lang),
                         ["T T S 测《ｗａｎｇ２》试文本《ｗａｎｇ２》 ， 来《ｗａｎｇ２》自单单单《ｗａｎｇ２》"])
        ## 自定义韵律标识符
        self.assertEqual(self.tn.call("TTS测<#0>试文本<#1>，来<#2>自单单单<#3>", lang), ["T T S 测《＃０》试文本《＃１》 ， 来《＃２》自单单单《＃３》"])
        ## 自定义停顿时长标识符
        self.assertEqual(self.tn.call("<&100>TTS测试文本<&200>，来自单单单<&300>", lang),
                         ["《＆１００》 T T S 测试文本《＆２００》 ， 来自单单单《＆３００》"])
        self.assertEqual(self.tn.call("<&100>TTS测试文本，<&200>，来自单单单<&300>", lang), ["《＆１００》 T T S 测试文本 ， 来自单单单《＆３００》"])
        self.assertEqual(self.tn.call("<&100>TTS测试<&200>文本，<&200>，来自单单单<&300>", lang),
                         ["《＆１００》 T T S 测试文本 ， 来自单单单《＆３００》"])

        # 随机测试
        self.assertEqual(self.tn.call("<&100>TTS测<1>试文<A>本<&200>，来自单单单<&300>", lang),
                         ["《＆１００》 T T S 测 、 一 、 试文 、 A 、 本《＆２００》 ， 来自单单单《＆３００》"])
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2><#1>单(@100)单}", lang),
                         ["T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》一《＃０》百《＃０》单《＃０》"])
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<#1><wang2>单(#100)单}", lang),
                         ["T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》幺《＃０》零《＃０》零《＃０》单《＃０》"])
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2><#1>单<&100>单}", lang),
                         ["T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》单《＃０》"])

        self.assertEqual(self.tn.call("你哈， 23:01， 达到 25:1", lang), ['你哈 ， 二十三时零一分 ， 达到二十五比一'])
        self.assertEqual(self.tn.call("你哈， 23:01:12， 达到 23:01:71", lang), ['你哈 ， 二十三时零一分十二秒 ， 达到二十三比一比七十一'])
        self.assertEqual(self.tn.call("你哈， 23/01/12， 达到 23/01", lang), ['你哈 ， 二十三 ， 一 ， 十二 ， 达到一分之二十三'])
        self.assertEqual(self.tn.call("你哈， 2023/01/12， 达到 23/01", lang), ['你哈 ， 二零二三年一月十二日 ， 达到一分之二十三'])
        self.assertEqual(self.tn.call("你哈， ￥23.5， 达到 23.01‰", lang), ['你哈 ， 二十三点五元 ， 达到千分之二十三点零一'])
        self.assertEqual(self.tn.call("你哈， 23.5￥， 达到 23.01‰", lang), ['你哈 ， 二十三点五 ， 达到千分之二十三点零一'])
        self.assertEqual(self.tn.call("2012年， 23.5%， 达到 23.01‰", lang), ['二零一二年 ， 百分之二十三点五 ， 达到千分之二十三点零一'])
        self.assertEqual(self.tn.call("202年， 23.5%， 达到 23.01‰", lang), ['两百零二年 ， 百分之二十三点五 ， 达到千分之二十三点零一'])
        self.assertEqual(self.tn.call("202年， -23.5%， 达到 -23.01‰", lang), ['两百零二年 ， 负百分之二十三点五 ， 达到负千分之二十三点零一'])
        self.assertEqual(self.tn.call("12°C， -12°C， 0.0°C， 0°C， 1.1°C， -1.1°C", lang),
                         ['十二摄氏度 ， 零下十二摄氏度 ， 零摄氏度 ， 零摄氏度 ， 一点一摄氏度 ， 零下一点一摄氏度'])
        self.assertEqual(self.tn.call("12°C， -12°C， 0.0°C， 0°C， 1.1°C， -1.1°C °C", lang),
                         ['十二摄氏度 ， 零下十二摄氏度 ， 零摄氏度 ， 零摄氏度 ， 一点一摄氏度 ， 零下一点一摄氏度'])
        self.assertEqual(self.tn.call("12°C， -12°C， 0.0°C， 0°C， 1.1°C， -1.1°C C", lang),
                         ['十二摄氏度 ， 零下十二摄氏度 ， 零摄氏度 ， 零摄氏度 ， 一点一摄氏度 ， 零下一点一摄氏度 C'])
        self.assertEqual(self.tn.call("12°C， -12°C， 0.0°C， 0°C， 1.1°C， °-1.1°C", lang),
                         ['十二摄氏度 ， 零下十二摄氏度 ， 零摄氏度 ， 零摄氏度 ， 一点一摄氏度 ， 零下一点一摄氏度'])
        self.assertEqual(self.tn.call("0°C， -0°C", lang), ['零摄氏度 ， 零下零摄氏度'])
        self.assertEqual(self.tn.call("23.5%，23%，0.01‰，0.0%, -0%", lang),
                         ['百分之二十三点五 ， 百分之二十三 ， 千分之零点零一 ， 百分之零点零 ， 负百分之零'])
        self.assertEqual(self.tn.call("-23.5%，-23%，-0.01，-0.0， -0", lang), ['负百分之二十三点五 ， 负百分之二十三 ， 负零点零一 ， 负零点零 ， 负零'])

        self.assertEqual(self.tn.call("-23.5，-23，-0.01，-0.0， -0-", lang), ['负二十三点五 ， 负二十三 ， 负零点零一 ， 负零点零 ， 负零'])
        self.assertEqual(self.tn.call("2012-12-14，2222-14-41", lang), ['二零一二年十二月十四日 ， 两千两百二十二至十四至四十一'])
        self.assertEqual(self.tn.call("2012/12/14，-14/41", lang), ['二零一二年十二月十四日 ， 负四十一分之十四'])
        self.assertEqual(self.tn.call("12:12:14，13:12:14，12:12:-14，12:-12:14，-12:12:14", lang),
                         ['十二时十二分十四秒 ， 十三时十二分十四秒 ， 十二比十二比负十四 ， 十二比负十二比十四 ， 负十二比十二比十四'])
        self.assertEqual(self.tn.call("12:12.0:14，13:-12.0:14", lang), ['十二比十二点零比十四 ， 十三比负十二点零比十四'])
        self.assertEqual(self.tn.call("12:12，25:12，12:-14，-12:12，-12:14.0", lang),
                         ['十二时十二分 ， 二十五比十二 ， 十二比负十四 ， 负十二比十二 ， 负十二比十四点零'])
        self.assertEqual(self.tn.call("2019年", lang), ["二零一九年"])
        self.assertEqual(self.tn.call("2019年20:30的比分", lang), ['二零一九年二十比三十的比分'])
        self.assertEqual(self.tn.call("哦<o4>好的", lang), ['哦《ｏ４》好的'])
        self.assertEqual(self.tn.call("阿<e1>胶", lang), ['阿《ｅ１》胶'])
        self.assertEqual(self.tn.call("阿<a1>波罗", lang), ['阿《ａ１》波罗'])
        self.assertEqual(self.tn.call("中华人民共和国的英文缩写：PRC，全称the People's Republic of China。中华人民共和国，通称“中国”。", lang),
                         ['中华人民共和国的英文缩写 ， P R C ， 全称 T H E P E O P L E S R E P U B L I C O F C H I N A',
                          '中华人民共和国 ， 通称 、 中国'])
        self.assertEqual(self.tn.call("<&2000>历史上有名的阿<a1>房女是真实存在的吗？<&2000>，{单玲玲}", lang),
                         ['《＆２０００》历史上有名的阿《ａ１》房女是真实存在的吗', '单《ｓｈａｎ４》《＃０》玲《＃０》玲《＃０》'])

    def test_cn_en_input(self):
        """中文字符+英文小写单词+[英文大写字母]+[数字]+[自定义标识符]"""
        lang = 'CN_EN'
        self.assertEqual(self.tn.call("", lang), [])

        self.assertEqual(self.tn.call("据英国《每日<ri1>邮报》10月6日报道hello！", lang), ['据英国 、 每日《ｒｉ１》邮报 、 十月六日报道hello'])
        self.assertEqual(self.tn.call("，，！，TTS前端文本测试文本hello。", lang), ['T T S 前端文本测试文本hello'])
        self.assertEqual(self.tn.call("TTS前端，，！，文本测试文本hello。", lang), ['T T S 前端', '文本测试文本hello'])
        self.assertEqual(self.tn.call("TTS前端文本测试文本hello，，！，", lang), ['T T S 前端文本测试文本hello'])
        self.assertEqual(self.tn.call("，，！，TTS前端文hello，，！，本测试文本，，！，", lang), ['T T S 前端文hello', '本测试文本'])

        self.assertEqual(self.tn.call("TTS前端123,001文本测试文本hello.", lang), ['T T S 前端十二万三千零一文本测试文本hello'])
        self.assertEqual(self.tn.call("TTS前端123,文本测试文本hello.", lang), ['T T S 前端一百二十三 ， 文本测试文本hello'])
        self.assertEqual(self.tn.call("TTS前端,001文本测试文本hello.", lang), ['T T S 前端 ， 一文本测试文本hello'])

        self.assertEqual(self.tn.call("TTS前端123.001文本测试文本hello.", lang), ['T T S 前端一百二十三点零零一文本测试文本hello'])
        self.assertEqual(self.tn.call("TTS前端123.文本测试文本hello.", lang), ['T T S 前端一百二十三', '文本测试文本hello'])
        self.assertEqual(self.tn.call("TTS前端.001文本测试文本hello.", lang), ['T T S 前端', '一文本测试文本hello'])  # 默认转实数

        self.assertEqual(self.tn.call("<&200>TTS{前<qian2>端}($123.001)文<#1>本(@123.001)测试(#123.001)文本hello<&100>.", lang),
                         ['《＆２００》 T T S 前《ｑｉａｎ２》《＃０》端《＃０》一二三零零一文《＃１》本一百二十三点零零一测试幺二三零零幺文本hello《＆１００》'])

        # 自定义标识符
        # # 自定义数字标识符
        self.assertEqual(self.tn.call("TTS测试(@123.123)文本", lang), ["T T S 测试一百二十三点一二三文本"])
        self.assertEqual(self.tn.call("TTS测试($123.123)文本", lang), ["T T S 测试一二三一二三文本"])
        self.assertEqual(self.tn.call("TTS测试(#123.123)文本", lang), ["T T S 测试幺二三幺二三文本"])
        # # 自定义人名标识符
        self.assertEqual(self.tn.call("TTS测试文本，来自{单单单}", lang), ["T T S 测试文本 ， 来自单《ｓｈａｎ４》《＃０》单《＃０》单《＃０》"])
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2>单单}", lang), ["T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃０》单《＃０》单《＃０》"])
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2>单<wang2>单<wang2>}", lang),
                         ["T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃０》单《ｗａｎｇ２》《＃０》单《ｗａｎｇ２》《＃０》"])
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2><#1>单<wang2><#2>单<wang2><#3>}", lang),
                         ["T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《ｗａｎｇ２》《＃２》单《ｗａｎｇ２》《＃３》"])
        # # 自定义拼音标识符
        self.assertEqual(self.tn.call("TTS测<wang2>试文本<wang2>，来<wang2>自单单单<wang2>", lang),
                         ["T T S 测《ｗａｎｇ２》试文本《ｗａｎｇ２》 ， 来《ｗａｎｇ２》自单单单《ｗａｎｇ２》"])
        # # 自定义韵律标识符
        self.assertEqual(self.tn.call("TTS测<#0>试文本<#1>，来<#2>自单单单<#3>", lang), ["T T S 测《＃０》试文本《＃１》 ， 来《＃２》自单单单《＃３》"])
        ## 自定义停顿时长标识符
        self.assertEqual(self.tn.call("<&100>TTS测试文本<&200>，来自单单单<&300>", lang),
                         ["《＆１００》 T T S 测试文本《＆２００》 ， 来自单单单《＆３００》"])
        self.assertEqual(self.tn.call("<&100>TTS测试<&200>文本，来自单单单<&300>", lang), ["《＆１００》 T T S 测试文本 ， 来自单单单《＆３００》"])
        self.assertEqual(self.tn.call("<&100>TTS测试文本，<&200>，来自单单单<&300>", lang), ["《＆１００》 T T S 测试文本 ， 来自单单单《＆３００》"])
        self.assertEqual(self.tn.call("<&100>TTS测试文本<&200>，<&200>来自单单单<&300>", lang),
                         ["《＆１００》 T T S 测试文本《＆２００》 ， 《＆２００》来自单单单《＆３００》"])
        self.assertEqual(self.tn.call("<&100>TTS测试<&200>文本，<&200>，来自单单单<&300>", lang),
                         ["《＆１００》 T T S 测试文本 ， 来自单单单《＆３００》"])

        # 随机测试
        # # CN
        self.assertEqual(self.tn.call("<&100>TTS测<1>试文<A>本<&200>，来自单单单<&300>", lang),
                         ["《＆１００》 T T S 测 、 一 、 试文 、 A 、 本《＆２００》 ， 来自单单单《＆３００》"])
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2><#1>单(@100)单}", lang),
                         ["T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》一《＃０》百《＃０》单《＃０》"])
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<#1><wang2>单(#100)单}", lang),
                         ["T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》幺《＃０》零《＃０》零《＃０》单《＃０》"])
        self.assertEqual(self.tn.call("TTS测试文本，来自{单<wang2><#1>单<&100>单}", lang),
                         ["T T S 测试文本 ， 来自单《ｗａｎｇ２》《＃１》单《＃０》单《＃０》"])

        # # CN_EN
        self.assertEqual(self.tn.call("T1TNS测试文本，hello 2020, happy new year<&100>", lang),
                         ["T one T N S 测试文本 ， hello two thousand and twenty , happy new year《＆１００》"])
        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>，hello 2020, happy new year", lang),
                         ["T one T N S 测试文本《ｂｅｎ２》 ， hello two thousand and twenty , happy new year"])
        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>，hello 2020<#2>, happy new year", lang),
                         ["T one T N S 测试文本《ｂｅｎ２》 ， hello two thousand and twenty 《＃２》 , happy new year"])
        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>，hello 2020<#2>, happy<ni2> new year", lang),
                         ["T one T N S 测试文本《ｂｅｎ２》 ， hello two thousand and twenty 《＃２》 , happy new year"])

        self.assertEqual(self.tn.call("保留了hello 3.5m hello耳机孔", lang), ["保留了hello three point five meters hello耳机孔"])
        self.assertEqual(self.tn.call("保留了hello 3.5km hello耳机孔", lang),
                         ["保留了hello three point five kilometers hello耳机孔"])
        self.assertEqual(self.tn.call("保留了hello 3.5m耳机孔", lang), ['保留了hello 三点五米耳机孔'])
        self.assertEqual(self.tn.call("保留了hello 3.5km耳机孔", lang), ['保留了hello 三点五千米耳机孔'])
        self.assertEqual(self.tn.call("保留了3.5m hello耳机孔", lang), ['保留了三点五米 hello耳机孔'])
        self.assertEqual(self.tn.call("保留了3.5km hello耳机孔", lang), ['保留了三点五千米 hello耳机孔'])
        self.assertEqual(self.tn.call("保留了hello，3.5m耳机孔。", lang), ['保留了hello ， 三点五米耳机孔'])
        self.assertEqual(self.tn.call("保留了hello,3.5km耳机孔。", lang), ['保留了hello ， 三点五千米耳机孔'])
        self.assertEqual(self.tn.call("保留了hello 3.5m, hello耳机孔。", lang),
                         ['保留了hello three point five meters , hello耳机孔'])
        self.assertEqual(self.tn.call("保留了hello 3.5km， hello耳机孔。", lang),
                         ['保留了hello three point five kilometers ， hello耳机孔'])
        self.assertEqual(self.tn.call("保留了3.5m， hello耳机孔。", lang), ['保留了三点五米 ， hello耳机孔'])
        self.assertEqual(self.tn.call("保留了3.5km, hello耳机孔。", lang), ['保留了三点五千米 ， hello耳机孔'])

        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>，hello 2020<#2>, happy ($314) new year", lang), [
            "T one T N S 测试文本《ｂｅｎ２》 ， hello two thousand and twenty 《＃２》 , happy three one four new year"])
        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>，($314) hello 2020<#2>, happy new year", lang),
                         ["T one T N S 测试文本《ｂｅｎ２》 ， 三一四 hello two thousand and twenty 《＃２》 , happy new year"])
        self.assertEqual(self.tn.call("($314) T1TNS测试文本<ben2>，hello 2020<#2>, happy ($314) new year", lang), [
            "three one four T one T N S 测试文本《ｂｅｎ２》 ， hello two thousand and twenty 《＃２》 , happy three one four new year"])
        self.assertEqual(self.tn.call("T1TNS测试文本<ben2>，hello 2020<#2>, happy ($314) new year ($314)", lang), [
            "T one T N S 测试文本《ｂｅｎ２》 ， hello two thousand and twenty 《＃２》 , happy three one four new year three one four"])

        self.assertEqual(self.tn.call("2019年 hello", lang), ["二零一九年 hello"])
        self.assertEqual(self.tn.call("2019-12-12hello2019年", lang),
                         ["the twelfth of december twenty nineteen hello二零一九年"])
        self.assertEqual(self.tn.call("120Hz 你", lang), ['一百二十赫兹你'])
        self.assertEqual(self.tn.call("120Hz hello", lang), ['one hundred and twenty h z hello'])
        self.assertEqual(self.tn.call("T1TNS测试文本120HzFN", lang), ['T one T N S 测试文本一百二十hzfn'])

        self.assertEqual(self.tn.call("2019年today20:30的比分", lang), ['二零一九年today二十比三十的比分'])
        self.assertEqual(self.tn.call("2019年today20：30的比分", lang), ['二零一九年today二十比三十的比分'])
        self.assertEqual(self.tn.call("2019年", lang), ["二零一九年"])
        self.assertEqual(self.tn.call("2019年20:30的比分", lang), ['二零一九年二十比三十的比分'])
        self.assertEqual(self.tn.call("2019年20：30的比分", lang), ['二零一九年二十比三十的比分'])

        self.assertEqual(self.tn.call("外加集成了153亿晶体管的5nm“性能怪兽”5G SoC让其坐稳了2020年安卓机皇的位置", lang),
                         ['外加集成了一百五十三亿晶体管的五纳米 、 性能怪兽 、 五 G S O C 让其坐稳了二零二零年安卓机皇的位置'])
        self.assertEqual(self.tn.call("20:30 hello 你好", lang), ['twenty to thirty hello 你好'])
        self.assertEqual(self.tn.call("你平时爱用iphone12手机，安卓手机，还是ipad平板呢？", lang),
                         ['你平时爱用 i phone 十二手机 ， 安卓手机 ， 还是 i pad 平板呢'])
        self.assertEqual(self.tn.call("这是新款华为mate20 pro手机", lang), ['这是新款华为mate twenty pro手机'])
        self.assertEqual(self.tn.call("球鞋Air Jordan 1 Mid Fearless", lang), ['球鞋air jordan one mid fearless'])

    def test_num_input(self):
        """数字"""
        lang = 'CN'
        self.assertEqual(self.tn.call("1", lang), ["一"])
        self.assertEqual(self.tn.call("15", lang), ["十五"])
        self.assertEqual(self.tn.call("20", lang), ["二十"])
        self.assertEqual(self.tn.call("23", lang), ["二十三"])
        self.assertEqual(self.tn.call("100", lang), ["一百"])
        self.assertEqual(self.tn.call("101", lang), ["一百零一"])
        self.assertEqual(self.tn.call("110", lang), ["一百一十"])
        self.assertEqual(self.tn.call("111", lang), ["一百一十一"])
        self.assertEqual(self.tn.call("1000", lang), ["一千"])
        self.assertEqual(self.tn.call("10321", lang), ["一万零三百二十一"])
        self.assertEqual(self.tn.call("1031", lang), ["一千零三十一"])
        self.assertEqual(self.tn.call("10021", lang), ["一万零二十一"])
        self.assertEqual(self.tn.call("10321", lang), ["一万零三百二十一"])
        self.assertEqual(self.tn.call("11321", lang), ["一万一千三百二十一"])
        self.assertEqual(self.tn.call("30150000", lang), ["三千零一十五万"])
        self.assertEqual(self.tn.call("35680101", lang), ["三千五百六十八万零一百零一"])
        self.assertEqual(self.tn.call("5030750622", lang), ["五十亿三千零七十五万零六百二十二"])
        self.assertEqual(self.tn.call("1330150312", lang), ["十三亿三千零一十五万零三百一十二"])
        self.assertEqual(self.tn.call("125800000000", lang), ["一千两百五十八亿"])
        self.assertEqual(self.tn.call("30150312", lang), ["三千零一十五万零三百一十二"])
        self.assertEqual(self.tn.call("1258000000000000", lang), ["一千两百五十八兆"])
        self.assertEqual(self.tn.call("3321", lang), ["三千三百二十一"])
        self.assertEqual(self.tn.call("331", lang), ["三百三十一"])
        self.assertEqual(self.tn.call("21", lang), ["二十一"])
        self.assertEqual(self.tn.call("321", lang), ["三百二十一"])
        self.assertEqual(self.tn.call("125800003321", lang), ["一千两百五十八亿零三千三百二十一"])
        self.assertEqual(self.tn.call("200", lang), ["两百"])
        self.assertEqual(self.tn.call("2222", lang), ["两千两百二十二"])
        self.assertEqual(self.tn.call("222000222", lang), ["两亿两千两百万零两百二十二"])
        self.assertEqual(self.tn.call("307830150312", lang), ["三千零七十八亿三千零一十五万零三百一十二"])

        self.assertEqual(self.tn.call("18.91", lang), ["十八点九一"])
        self.assertEqual(self.tn.call("0.123", lang), ["零点一二三"])
        self.assertEqual(self.tn.call("0", lang), ["零"])
        self.assertEqual(self.tn.call("1099.66", lang), ["一千零九十九点六六"])

        lang = 'EN'
        self.assertEqual(self.tn.call("0", lang), ["zero"])
        self.assertEqual(self.tn.call("1", lang), ["one"])
        self.assertEqual(self.tn.call("2", lang), ["two"])
        self.assertEqual(self.tn.call("3", lang), ["three"])
        self.assertEqual(self.tn.call("4", lang), ["four"])
        self.assertEqual(self.tn.call("5", lang), ["five"])
        self.assertEqual(self.tn.call("6", lang), ["six"])
        self.assertEqual(self.tn.call("7", lang), ["seven"])
        self.assertEqual(self.tn.call("8", lang), ["eight"])
        self.assertEqual(self.tn.call("9", lang), ["nine"])
        self.assertEqual(self.tn.call("10", lang), ["ten"])
        self.assertEqual(self.tn.call("11", lang), ["eleven"])
        self.assertEqual(self.tn.call("12", lang), ["twelve"])
        self.assertEqual(self.tn.call("13", lang), ["thirteen"])
        self.assertEqual(self.tn.call("14", lang), ["fourteen"])
        self.assertEqual(self.tn.call("15", lang), ["fifteen"])
        self.assertEqual(self.tn.call("16", lang), ["sixteen"])
        self.assertEqual(self.tn.call("17", lang), ["seventeen"])
        self.assertEqual(self.tn.call("18", lang), ["eighteen"])
        self.assertEqual(self.tn.call("19", lang), ["nineteen"])
        self.assertEqual(self.tn.call("20", lang), ["twenty"])
        self.assertEqual(self.tn.call("21", lang), ["twenty one"])

        self.assertEqual(self.tn.call("29", lang), ["twenty nine"])
        self.assertEqual(self.tn.call("99", lang), ["ninety nine"])
        self.assertEqual(self.tn.call("100", lang), ["one hundred"])
        self.assertEqual(self.tn.call("101", lang), ["one hundred and one"])
        self.assertEqual(self.tn.call("110", lang), ["one hundred and ten"])
        self.assertEqual(self.tn.call("111", lang), ["one hundred and eleven"])
        self.assertEqual(self.tn.call("900", lang), ["nine hundred"])
        self.assertEqual(self.tn.call("999", lang), ["nine hundred and ninety nine"])
        self.assertEqual(self.tn.call("1000", lang), ["one thousand"])
        self.assertEqual(self.tn.call("1001", lang), ["one thousand and one"])
        self.assertEqual(self.tn.call("1010", lang), ["one thousand and ten"])
        self.assertEqual(self.tn.call("1100", lang), ["one thousand , one hundred"])
        self.assertEqual(self.tn.call("-1100", lang), ["minus one thousand , one hundred"])
        self.assertEqual(self.tn.call("2000", lang), ["two thousand"])
        self.assertEqual(self.tn.call("10000", lang), ["ten thousand"])
        self.assertEqual(self.tn.call("100000", lang), ["one hundred thousand"])
        self.assertEqual(self.tn.call("100001", lang), ["one hundred thousand and one"])
        self.assertEqual(self.tn.call("100010", lang), ["one hundred thousand and ten"])
        self.assertEqual(self.tn.call("100100", lang), ["one hundred thousand , one hundred"])
        self.assertEqual(self.tn.call("101000", lang), ["one hundred and one thousand"])
        self.assertEqual(self.tn.call("1010000", lang), ["one million , ten thousand"])
        self.assertEqual(self.tn.call("1010001", lang), ["one million , ten thousand and one"])
        self.assertEqual(self.tn.call("123456", lang),
                         ["one hundred and twenty three thousand , four hundred and fifty six"])
        self.assertEqual(self.tn.call("0123456", lang),
                         ["one hundred and twenty three thousand , four hundred and fifty six"])
        self.assertEqual(self.tn.call("1234567", lang),
                         ["one million , two hundred and thirty four thousand , five hundred and sixty seven"])
        self.assertEqual(self.tn.call("12345678", lang),
                         ["twelve million , three hundred and forty five thousand , six hundred and seventy eight"])
        self.assertEqual(self.tn.call("1234567890", lang), [
            "one billion , two hundred and thirty four million , five hundred and sixty seven thousand , eight hundred and ninety"])
        self.assertEqual(self.tn.call("123456789012345", lang), [
            "one hundred and twenty three trillion , four hundred and fifty six billion , seven hundred and eighty nine million , twelve thousand , three hundred and forty five"])
        self.assertEqual(self.tn.call("12345678901234567890", lang), [
            "twelve quintillion , three hundred and forty five quadrillion , six hundred and seventy eight trillion , nine hundred and one billion , two hundred and thirty four million , five hundred and sixty seven thousand , eight hundred and ninety"])

        self.assertEqual(self.tn.call("0.987654", lang), ["zero point nine eight seven six five four"])
        self.assertEqual(self.tn.call("-0.987654", lang), ["minus zero point nine eight seven six five four"])
        self.assertEqual(self.tn.call("9.87654", lang), ["nine point eight seven six five four"])
        self.assertEqual(self.tn.call("98.7654", lang), ["ninety eight point seven six five four"])
        self.assertEqual(self.tn.call("987.654", lang), ["nine hundred and eighty seven point six five four"])
        self.assertEqual(self.tn.call("9876.54", lang),
                         ["nine thousand , eight hundred and seventy six point five four"])
        self.assertEqual(self.tn.call("-98765.4", lang),
                         ["minus ninety eight thousand , seven hundred and sixty five point four"])

    def test_en_input(self):
        """英文小写单词+[英文大写字母]+[数字]+[自定义标识符]"""
        lang = "EN"

        # 空字符串
        self.assertEqual(self.tn.call("", lang), [])  # 空字符串

        # 标点冗余
        self.assertEqual(self.tn.call(",,!,TTS font end,,!,test text,,!,", lang), ["T T S font end , test text"])

        # 标点语言匹配
        self.assertEqual(self.tn.call("TTS font end，test text。TTS font end，test text？TTS font end，test text！", lang),
                         ['T T S font end , test text', 'T T S font end , test text', 'T T S font end , test text'])

        # 标点语言匹配——,(英文逗号)特殊处理
        self.assertEqual(
            self.tn.call("TTS font end 123456, test text。TTS font end 12,300 test text？TTS font end ,123456 test text！",
                         lang),
            ['T T S font end one hundred and twenty three thousand , four hundred and fifty six , test text',
             'T T S font end twelve thousand , three hundred test text',
             'T T S font end , one hundred and twenty three thousand , four hundred and fifty six test text'])

        # 标点语言匹配——.(英文句号)特殊处理
        self.assertEqual(
            self.tn.call("TTS font end 123456. test text。TTS font end 12.300 test text？TTS font end .123456 test text！",
                         lang),
            ['T T S font end one hundred and twenty three thousand , four hundred and fifty six', 'test text',
             'T T S font end twelve point three zero zero test text', 'T T S font end',
             'one hundred and twenty three thousand , four hundred and fifty six test text'])

        self.assertEqual(self.tn.call('"U.S. Decennial Census " U.S.', lang), ['U S decennial census U S'])

        self.assertEqual(self.tn.call("TTS font end ($123.001) test text<&100>.", lang),
                         ['T T S font end one two three zero zero one test text'])  # TODO 不支持英文前后停顿时长标记

        # 随机测试
        self.assertEqual(self.tn.call(
            "Yan made the remarks during a panel discussion on 'Investment in Canada' organized during the Canada China Business Council's 42nd Annual General Meeting Business Forum held in Beijing.",
            lang), [
                             "yan made the remarks during a panel discussion on investment in canada organized during the canada china business council's forty second annual general meeting business forum held in beijing"])
        self.assertEqual(self.tn.call(
            "Visitors at the booth of Huawei during the China International Fair for Trade in Services in Beijing in September. [ZHAN MIN/FOR CHINA DAILY]",
            lang), [
                             'visitors at the booth of huawei during the china international fair for trade in services in beijing in september',
                             'Z H A N M I N ， F O R C H I N A D A I L Y'])

        self.assertEqual(self.tn.call(
            "Huawei is among the top 20 largest corporate investors in Canada and employs over 1,200 people there",
            lang), [
                             'huawei is among the top twenty largest corporate investors in canada and employs over one thousand , two hundred people there'])
        self.assertEqual(self.tn.call(
            "Huawei is among the top ($20) largest corporate investors in Canada and employs over 1,200 people there",
            lang), [
                             "huawei is among the top two zero largest corporate investors in canada and employs over one thousand , two hundred people there"])
        self.assertEqual(self.tn.call(
            "Huawei is among the top (@20) largest corporate investors in Canada and employs over 1,200 people there",
            lang), [
                             "huawei is among the top twenty largest corporate investors in canada and employs over one thousand , two hundred people there"])
        self.assertEqual(self.tn.call(
            "Huawei is among the top (#20) largest corporate investors in Canada and employs over 1,200 people there",
            lang), [
                             "huawei is among the top two O largest corporate investors in canada and employs over one thousand , two hundred people there"])

        self.assertEqual(self.tn.call("HUAWEI Canada and employs over 1,200 people there", lang),
                         ["H U A W E I canada and employs over one thousand , two hundred people there"])
        self.assertEqual(self.tn.call("Huawei CANADA and employs over 1,200 people there", lang),
                         ['huawei C A N A D A and employs over one thousand , two hundred people there'])
        self.assertEqual(self.tn.call("Huawei Canada and employs over 1,200 people THERE", lang),
                         ['huawei canada and employs over one thousand , two hundred people T H E R E'])

        self.assertEqual(self.tn.call(
            "Yan made the remarks during a panel discussion on 'Investment in Canada' organized during the Canada China Business Council's 42nd Annual General Meeting Business Forum held in Beijing",
            lang), [
                             "yan made the remarks during a panel discussion on investment in canada organized during the canada china business council's forty second annual general meeting business forum held in beijing"])
        self.assertEqual(self.tn.call(
            "So far, China has 21 pilot free trade zones, located from south to north and from the country's coasts to its inland regions.",
            lang), [
                             "so far , china has twenty one pilot free trade zones , located from south to north and from the country's coasts to its inland regions"])

        self.assertEqual(self.tn.call("TTS font end, 3.5m test text!", lang),
                         ['T T S font end , three point five metres test text'])
        self.assertEqual(self.tn.call("TTS font end, 3.5km test text!", lang),
                         ['T T S font end , three point five kilometres test text'])
        self.assertEqual(self.tn.call("Love begins with a smile,grows with a kiss and ends with a tear.", lang),
                         ['love begins with a smile , grows with a kiss and ends with a tear'])
        self.assertEqual(self.tn.call("administrator@guiji.ai", lang), ['administrator at guiji', 'ai'])
        self.assertEqual(self.tn.call("I was a teacher of Xihua University.", lang),
                         ['I was a teacher of xihua university'])


if __name__ == '__main__':
    unittest.main()
