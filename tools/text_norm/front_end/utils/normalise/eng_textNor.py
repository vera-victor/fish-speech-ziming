import re, sys

from tqdm import tqdm

sys.path.append("..")

from service.modules.preprocess.front_end.utils.normalise.normalize_english import normalize_


def demo1():
    # text = input("Enter an english sentence to be normalized:    ")
    text = "English 1234 qaba"
    text_1 = normalize_(text)
    # print()
    print("------NORMALIZED TEXT:------")
    # print()
    print(text_1)


def iter_sent():
    items = []
    sent_id = None
    # filename = "D:\Data\TTS\英文正则化\谷歌数据集\en_train.csv"
    filename = desk("en_tn_corpus/test.csv")
    print(filename)
    for line in fiter(filename, dropout_first=True, is_tqdm=True):
        item = line.replace('"', "").split(",")
        if sent_id is not None and item[0] != sent_id and len(items) > 0:
            yield sent_id, items
            items = []
        if len(item[1:]) == 4:
            items.append(item[1:])
            sent_id = item[0]


def demo2():
    # 测试句子级别，准确率:87.08%
    all_count = 0
    ok_count = 0
    for i, (sent_id, items) in enumerate(iter_sent()):
        ids, tags, befores, afters = zip(*items)
        raw_text = " ".join(befores)
        real_text = " ".join(afters)
        pred_text, pred_tags = normalize_(raw_text)
        pred_text = re.sub("[^\da-zA-Z\u4e00-\u9fa5]+", " ", pred_text).strip().lower()
        real_text = re.sub("[^\da-zA-Z\u4e00-\u9fa5]+", " ", real_text).strip().lower()
        pred_text = re.sub(" +", " ", pred_text)
        real_text = re.sub(" +", " ", real_text)
        all_count += 1
        if pred_text == real_text:
            ok_count += 1
        if i % 200 == 0 and i > 10:
            print("准确率:{:>6.2%}({}/{})".format(ok_count / all_count, ok_count, all_count))
    print("Final 准确率:{:>6.2%}({}/{})".format(ok_count / all_count, ok_count, all_count))


def demo3():
    """
    测试单词级别
        准确率:98.66%(72847/73839)
            FRACTION:  100.00%(6/6)
            PLAIN:      99.08%(68377/69014)
            DATE:       95.96%(1973/2056)
            LETTERS:    96.84%(1041/1075)
            CARDINAL:   90.29%(1265/1401)
            DECIMAL:    91.53%(108/118)
            DIGIT:      83.33%(10/12)
            TIME:       81.82%(9/11)
            VERBATIM:   63.16%(36/57)
            ELECTRONIC: 35.14%(13/37)
            MONEY:      30.00%(6/20)
            TELEPHONE:  10.71%(3/28)
            PUNCT:       0.00%(0/1)
            MEASURE:     0.00%(0/3)
    """
    all_count = 0
    ok_count = 0
    data_dict = dict()
    for i, (sent_id, items) in enumerate(iter_sent()):
        # ids, tags, befores, afters = zip(*items)
        for id, tag, before, after in items:
            pred_before, classes = normalize_(before)
            pred_before = re.sub("[^\da-zA-Z\u4e00-\u9fa5]+", " ", pred_before).strip().lower()
            after = re.sub("[^\da-zA-Z\u4e00-\u9fa5]+", " ", after).strip().lower()
            pred_before = re.sub(" +", " ", pred_before)
            after = re.sub(" +", " ", after)
            if not pred_before or not after:
                continue
            tag = classes[0][0] if len(classes) > 0 and len(classes[0]) > 0 else None
            data_dict.setdefault(tag, [0, 0])
            data_dict[tag][0] += 1
            all_count += 1
            if pred_before == after:
                data_dict[tag][1] += 1
                ok_count += 1
            if all_count % 500 == 0 and all_count > 10:
                print("准确率:{:>6.2%}({}/{})".format(ok_count / all_count, ok_count, all_count))
                for lab, (v1, v2) in sorted(data_dict.items(), key=lambda x: x[1][0], reverse=True):
                    print("\t{}:{:>6.2%}({}/{})".format(lab, v2 / v1, v2, v1))
    print("---------------------------")
    print("准确率:{:>6.2%}({}/{})".format(ok_count / all_count, ok_count, all_count))
    for lab, (v1, v2) in sorted(data_dict.items(), key=lambda x: x[1][0], reverse=True):
        print("\t{}:{:>6.2%}({}/{})".format(lab, v2 / v1, v2, v1))


def demo4():
    """
    2000个测试
    """
    before_file = open('/home/walter/data/tts_data/英文正则化/before_sentences.txt', 'r', encoding='utf-8')
    after_file = open('/home/walter/data/tts_data/英文正则化/after_sentences.txt', 'r', encoding='utf-8')
    before_lines = [line.strip() for line in before_file.readlines()]
    after_lines = [line.strip() for line in after_file.readlines()]
    assert len(before_lines) == len(after_lines)
    process_count = 2000
    count = 0
    of = open("/home/walter/data/tts_data/英文正则化/1111.txt", 'w', encoding='utf-8')
    for i in tqdm(range(len(before_lines)), total=len(before_lines)):
        text = before_lines[i]
        try:
            before_result, classes = normalize_(text)
            before_result = re.sub("[^\da-zA-Z\u4e00-\u9fa5]+", " ", before_result).strip().lower()
            after = re.sub("[^\da-zA-Z\u4e00-\u9fa5]+", " ", after_lines[i]).strip().lower()
            before_result = re.sub(" +", " ", before_result)
            after = re.sub(" +", " ", after)
            if before_result == after:
                count += 1
            else:
                of.write(text + "\t" + after + "\t" + before_result + "\n")
        except Exception as e:
            print(text)
    print("处理了{}条测试数据，正确的有{}条，准确率为：{}".format(process_count, count, count / process_count))


"""
新
    sub_train 60.74%
    test 56.54%
旧
    sub_train   74.65%
    test        74.22%


"""

#
if __name__ == '__main__':
    demo2()
