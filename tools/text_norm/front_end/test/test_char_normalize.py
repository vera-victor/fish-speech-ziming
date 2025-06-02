# -*- coding: utf-8 -*-
# Create Time: 2020/10/12 上午10:42
# Author: Allen

import unittest
from service.modules.preprocess.front_end.normalize.char_normalize import CharNormalize


class TestCharNormalize(unittest.TestCase):
    def setUp(self) -> None:
        self.cn = CharNormalize()

    def test_char_normalize_CN(self):
        lang = "CN"
        self.assertEqual(self.cn.call(
            "０１２３４５６７８９①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇⒈⒉⒊⒋⒌⒍⒎⒏⒐⒑⒒⒓⒔⒕⒖⒗⒘⒙⒚⒛ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹ❶❷❸❹❺❻❼❽❾❿㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩",
            lang),
            "0123456789123456789101112131415161718192012345678910111213141516171819201234567891011121314151617181920123456789101112123456789101234567891012345678910。")
        self.assertEqual(self.cn.call("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ", lang),
                         "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz。")

        # 空字符串
        self.assertEqual(self.cn.call("", lang), "")  # 空字符串

        # 标点冗余
        self.assertEqual(self.cn.call("，，！，TTS前端文本测试文本。", lang), "TTS前端文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端，，！，文本测试文本。", lang), "TTS前端！文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端文本测试文本，，！，", lang), "TTS前端文本测试文本！")
        self.assertEqual(self.cn.call("，，！，TTS前端文，，！，本测试文本，，！，", lang), "TTS前端文！本测试文本！")

        # 标点语言匹配
        self.assertEqual(self.cn.call("TTS前端,文本测试文本.", lang), "TTS前端,文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端,文本测试文本?", lang), "TTS前端,文本测试文本？")
        self.assertEqual(self.cn.call("TTS前端,文本测试文本!", lang), "TTS前端,文本测试文本！")

        # 标点语言匹配——,(英文逗号)特殊处理
        self.assertEqual(self.cn.call("TTS前端123,001文本测试文本.", lang), "TTS前端123,001文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端123,文本测试文本.", lang), "TTS前端123,文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端,001文本测试文本.", lang), "TTS前端,001文本测试文本。")

        # 标点语言匹配——.(英文句号)特殊处理
        self.assertEqual(self.cn.call("TTS前端123.001文本测试文本.", lang), "TTS前端123.001文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端123.文本测试文本.", lang), "TTS前端123.文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端.001文本测试文本.", lang), "TTS前端.001文本测试文本。")

        # 自定义标识符
        self.assertEqual(self.cn.call("<&200>TTS{前<qian2>端}($123.001)文<#1>本(@123.001)测试(#123.001)文本<&100>.", lang),
                         "<&200>TTS{前<qian2>端}($123.001)文<#1>本(@123.001)测试(#123.001)文本<&100>。")

    def test_char_normalize_CN_EN(self):
        lang = "CN_EN"
        self.assertEqual(self.cn.call(
            "０１２３４５６７８９①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇⒈⒉⒊⒋⒌⒍⒎⒏⒐⒑⒒⒓⒔⒕⒖⒗⒘⒙⒚⒛ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹ❶❷❸❹❺❻❼❽❾❿㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩",
            lang),
            "0123456789123456789101112131415161718192012345678910111213141516171819201234567891011121314151617181920123456789101112123456789101234567891012345678910。")
        self.assertEqual(self.cn.call("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ", lang),
                         "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz。")
        # 空字符串
        self.assertEqual(self.cn.call("", lang), "")  # 空字符串

        # 标点冗余
        self.assertEqual(self.cn.call("，，！，TTS前端文本测试文本。", lang), "TTS前端文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端，，！，文本测试文本。", lang), "TTS前端！文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端文本测试文本，，！，", lang), "TTS前端文本测试文本！")
        self.assertEqual(self.cn.call("，，！，TTS前端文，，！，本测试文本，，！，", lang), "TTS前端文！本测试文本！")

        # 标点语言匹配
        self.assertEqual(self.cn.call("TTS前端,文本测试文本.", lang), "TTS前端,文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端,文本测试文本?", lang), "TTS前端,文本测试文本？")
        self.assertEqual(self.cn.call("TTS前端,文本测试文本!", lang), "TTS前端,文本测试文本！")

        # 标点语言匹配——,(英文逗号)特殊处理
        self.assertEqual(self.cn.call("TTS前端123,001文本测试文本.", lang), "TTS前端123,001文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端123,文本测试文本.", lang), "TTS前端123,文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端,001文本测试文本.", lang), "TTS前端,001文本测试文本。")

        self.assertEqual(self.cn.call("T,TS,前端123,001文本测试,test,case,文本.", lang), "T,TS,前端123,001文本测试,test,case,文本。")
        self.assertEqual(self.cn.call("T,TS,前端123,001文本测试,test, case,文本.", lang), "T,TS,前端123,001文本测试,test, case,文本。")
        self.assertEqual(self.cn.call("T,TS,前端123,001文本测试,test ,case,文本.", lang), "T,TS,前端123,001文本测试,test, case,文本。")

        # 标点语言匹配——.(英文句号)特殊处理
        self.assertEqual(self.cn.call("TTS前端123.001文本测试文本.", lang), "TTS前端123.001文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端123.文本测试文本.", lang), "TTS前端123.文本测试文本。")
        self.assertEqual(self.cn.call("TTS前端.001文本测试文本.", lang), "TTS前端.001文本测试文本。")

        # 自定义标识符
        self.assertEqual(self.cn.call("<&200>TTS{前<qian2>端}($123.001)文<#1>本(@123.001)测试(#123.001)文本<&100>.", lang),
                         "<&200>TTS{前<qian2>端}($123.001)文<#1>本(@123.001)测试(#123.001)文本<&100>。")

    def test_char_normalize_EN(self):
        lang = "EN"
        self.assertEqual(self.cn.call(
            "０１２３４５６７８９①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇⒈⒉⒊⒋⒌⒍⒎⒏⒐⒑⒒⒓⒔⒕⒖⒗⒘⒙⒚⒛ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹ❶❷❸❹❺❻❼❽❾❿㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩",
            lang),
            "0123456789123456789101112131415161718192012345678910111213141516171819201234567891011121314151617181920123456789101112123456789101234567891012345678910.")
        self.assertEqual(self.cn.call("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ", lang),
                         "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.")
        # 空字符串
        self.assertEqual(self.cn.call("", lang), "")  # 空字符串

        # 标点冗余
        self.assertEqual(self.cn.call(",,!,TTS font end,,!,test text,,!,", lang), "TTS font end, test text.")

        # 标点语言匹配
        self.assertEqual(self.cn.call("TTS font end，test text。TTS font end，test text？TTS font end，test text！", lang),
                         "TTS font end，test text。TTS font end，test text? TTS font end，test text!")

        # 标点语言匹配——,(英文逗号)特殊处理
        self.assertEqual(
            self.cn.call("TTS font end 123456, test text。TTS font end 12,300 est text？TTS font end ,123456 test text！",
                         lang),
            "TTS font end 123456, test text。TTS font end 12,300 est text? TTS font end, 123456 test text!")

        # 标点语言匹配——.(英文句号)特殊处理
        self.assertEqual(
            self.cn.call("TTS font end 123456. test text。TTS font end 12.300 est text？TTS font end .123456 test text！",
                         lang),
            "TTS font end 123456. test text。TTS font end 12.300 est text? TTS font end. 123456 test text!")

        self.assertEqual(self.cn.call('"U.S. Decennial Census " U.S.', lang), "U.S. Decennial Census U.S.")

        self.assertEqual(self.cn.call("TTS font end ($123.001) test text<&100>.", lang),
                         "TTS font end ($123.001) test text<&100>.")

        # 随机测试
        self.assertEqual(self.cn.call(
            "Yan made the remarks during a panel discussion on 'Investment in Canada' organized during the Canada China Business Council's 42nd Annual General Meeting Business Forum held in Beijing.",
            lang),
            "Yan made the remarks during a panel discussion on 'Investment in Canada' organized during the Canada China Business Council's 42nd Annual General Meeting Business Forum held in Beijing.")
        self.assertEqual(self.cn.call(
            "Visitors at the booth of Huawei during the China International Fair for Trade in Services in Beijing in September. [ZHAN MIN/FOR CHINA DAILY]",
            lang),
            "Visitors at the booth of Huawei during the China International Fair for Trade in Services in Beijing in September. ZHAN MIN/FOR CHINA DAILY.")


if __name__ == '__main__':
    unittest.main()
