"""
英文单词转复数形式

1.直接加s。
2.以s,sh,ch,x结尾的单词要加es。
3.以辅音字母加上y结尾的单词,去掉y加上ies.
4.以o结尾的名词，变复数时，大多数都是直接加s,
    除了hero,negro,potato,tamato这四个加es.
5.以f或fe结尾的名词变复数时,可以是加s，如：belief-beliefs，roof-roofs;
    也有去f,fe加ves，如half-halves,knife-knives,leaf-leaves,wolf-wolves,wife-wives,thief-thieves.

"""
import re


# 每条匹配规则都有自己的函数，它们返回对re.search() 函数调用结果。

# 实现对sxz结尾单词的匹配和复数输出函数
def match_sxz(noun):
    return re.search('[sxz]$', noun)


def apply_sxz(noun):
    return re.sub('$', 'es', noun)


# 实现对*h结尾单词的匹配和复数输出函数
def match_h(noun):
    return re.search('[^aeioudgkprt]h$', noun)


def apply_h(noun):
    return re.sub('$', 'es', noun)


# 实现对*y结尾单词的匹配和复数输出函数
def match_y(noun):
    return re.search('[^aeiou]y$', noun)


def apply_y(noun):
    return re.sub('y$', 'ies', noun)


# 实现对上面三种情况之外的单词输出复数
def match_default(noun):
    return True


def apply_default(noun):
    return noun + 's'


# 一个函数对的序列，而不是一个函数（plural()）实现多个条
rules = ((match_sxz, apply_sxz),
         (match_h, apply_h),
         (match_y, apply_y),
         (match_default, apply_default)
         )


def plural(noun):
    for matches_rule, apply_rule in rules:
        if matches_rule(noun):
            return apply_rule(noun)


def parse_complex(text):
    """
    单词复数形式
    :param text:
    :return:
    """
    text = text.replace(" '", "'")

    def func(match):
        word = match.group(2)
        return match.group(1) + plural(word)
    # print('#############',text)
    # text = re.sub(r"(^| )([a-zA-Z]+)'s", func, text)
    # print('@@@@@@@@@@@@',text)
    # text = re.sub(r"(^| )([a-zA-Z]+)’s", func,
    return text


# 实现函数调用,求单次复数形式
if __name__ == '__main__':
    print(parse_complex("school's"))
    print(parse_complex(
        "she was named one of twenty ten 's one hundred most influential people in the world by time magazine"))
    exit()
    print(plural('zoo'))
    print(plural("kitty"))
    print(plural('coach'))
    print(plural('it'))
    print(plural('she'))
    print(plural('half'))
    print(plural('knife'))
    print(plural('leaf'))
    print(plural('wolf'))
    print(plural('wife'))
    print(plural('thief'))

'''结果如下：
zoos
kitties
coaches
'''
