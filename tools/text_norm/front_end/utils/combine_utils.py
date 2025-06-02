import re


def combine_grapheme_prosody(cds):
    grapheme_list = cds.grapheme_list
    language_list = cds.language_flag
    prosody_list = cds.prosody_list
    assert len(grapheme_list) == len(language_list)
    txt = ' '
    for phone, prosody, flag in zip(grapheme_list, prosody_list, language_list):
        if prosody == "#0":
            prosody = ""
        if flag == 1:
            txt += " " + phone + " " + prosody
        elif flag == 0:
            txt += " " + phone + " " + prosody
        elif flag == '，':
            txt += ' #3'
        elif flag == ',':
            txt += ' #3'
        elif flag == '、':
            txt += ' #2'
        else:
            pass
    # txt = txt.replace('#0', '').replace('#1', '@').replace('#2', '^').replace('#3', '，')
    # txt = re.sub(r"[@^&]+$", '', txt)
    # txt = txt.replace('#0', '').replace('@', ' #1').replace('^', ' #2').replace('，', ' #3')
    # txt = re.sub(r" +", ' ', txt)
    # txt = txt.replace('#1 #2', '#2').replace('#2 #2', '#2')
    txt = re.sub(r" +", ' ', txt)

    def func(match):
        num1 = match.group(1)
        num2 = match.group(2)

        return '#%s' % str(num1) if num1 >= num2 else '#%s' % str(num2)

    txt = re.sub(r"#(\d) ?#(\d)", func, txt)  # 韵律去重

    return txt.strip() + " #3"

# if __name__ == '__main__':
#     phone_list = ['guo4', 'qu4', 'liang3', 'nian2', 'quan2', 'qiu2', 'si4', 'nve4', 'de5', 'xin1', 'guan1', 'bing4', 'du2']
#     language_list = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#     prosody_list = ['#0', '#1', '#0', '#2', '#0', '#1', '#0', '#0', '#2', '#0', '#1', '#0', '#0']
#     text = ' '
#     for phone, prosody, flag in zip(phone_list, prosody_list, language_list):
#         if prosody == "#0":
#             prosody = ""
#         if flag == 1:
#             text += " " + phone + " " + prosody
#         elif flag == 0:
#             text += phone + prosody
#         elif flag == '，':
#             text += '#3'
#         elif flag == ',':
#             text += '#3'
#         elif flag == '、':
#             text += '#2'
#         else:
#             pass
#     print("***************", text)
#     text = text.replace('#0', '').replace('#1', '@').replace('#2', '^').replace('#3', '，')
#     text = re.sub(r"[@^&]+$", '', text)
#     text = text.replace('#0', '').replace('@', ' #1').replace('^', ' #2').replace('，', ' #3')
#     text = re.sub(r" +", ' ', text)
#     print("***************", text)
