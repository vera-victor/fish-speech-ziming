#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：gjtts_server
@File ：insertcontext.py
@Author ： z_q_mao
@Date ：21-10-13 上午10:12
"""

import random

a = ['-uuui2#0hu4#1gong1#0ping2#1he2#0li3#0de5', 'guo2#0ji4#1zhix4#0li3#1ti3#0xi4#0']


def RepSingleWords(pices):
    if "#1" in pices:
        piceses = pices.split("#1")
        index = random.choice(range(len(piceses)))
        replist = piceses[index]
        replist = replist.split("#0")
        if len(replist) >= 2:
            replist = replist[0] + "#5" + "#0".join(replist)
        else:
            replist = "#0".join(replist)
        piceses[index] = replist
        pices = "#1".join(piceses)
    return pices


def DuplicateFistWords(sentence_list):
    rand_words = random.random()
    if rand_words < 0.2:
        index = random.choice(range(len(sentence_list)))
        if index is not None:
            target_pices = sentence_list[index]
            sentence_list[index] = RepSingleWords(target_pices)
    return sentence_list


if __name__ == '__main__':
    print(DuplicateFistWords(sentence_list=a))
    # print(RepSingleWords(pices='gong1#0ping2#1he2#0li3#0de5'))
