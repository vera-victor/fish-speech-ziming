import os

import json


def load_json2dict(json_path):
    with open(json_path, "r") as rf:
        data = json.load(rf)
    return data


def readlines(filename):
    if not filename or not os.path.isfile(filename):
        return []
    texts = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            text = line.replace("\n", "")
            texts.append(text)
    return texts


def load_single_file(filename):
    if not filename or not os.path.isfile(filename):
        return {}
    out = dict()
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            text = line.replace("\n", "")
            char, pys = text.split("|")
            out[ord(char)] = pys
    return out


def batch_selector(datas, batch_size=32, is_random=False, is_tqdm=False):
    """
    批次拾取器，只遍历一次
    :param datas:
    :param batch_size:
    :param is_random:
    :param is_tqdm:
    :return:
    """
    import types
    if is_random:
        if isinstance(datas, types.GeneratorType):
            temps = []
            for data in datas:
                temps.append(data)
            datas = temps
        np.random.shuffle(datas)
        datas = tuple(datas)
    if isinstance(datas, list):
        datas = tuple(datas)
    if is_tqdm and isinstance(datas, tuple):
        datas = tqdm(datas, total=len(datas))
    temp = []
    for data in datas:
        temp.append(data)
        if len(temp) >= batch_size:
            yield temp
            temp.clear()
    if len(temp) > 0:
        yield temp
        temp.clear()
