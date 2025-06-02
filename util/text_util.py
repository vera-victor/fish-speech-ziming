from config import config


def split_sentence(all_text_str):
    all_texts = [all_text_str]
    if len(all_text_str) > 0:
        for split_symbol in config.split_symbols:
            temp_arr = []
            for text in all_texts:
                temp_arr.extend(text.split(split_symbol))
            all_texts = temp_arr

    new_texts = []
    for text in all_texts:
        if len(text) < config.split_len:
            new_texts.append(text)
        else:
            new_texts.append(text[:config.split_len])
            new_texts.append(text[config.split_len:])
    print(">>>>>>>>>>>>>>>>>>>>>>", new_texts)
    new_texts = [text.strip() for text in new_texts if text.strip()]
    return new_texts


if __name__ == '__main__':
    r_text = '生活并没有如你所愿，这个世界上没有那么多的刚刚好，努力不一定会有回报，但是努力的过程一定会让我们成为更优秀的自己。人生路上的每一步都算数，你付出的每一点都有意义。我们在世界上选择什么样的，成为什么样的人。人生丰富多彩，得靠自己成全。你此刻的付出，决定你未来会成为什么样的人。当你改变不了世界的时候，你可以改变自己。人的人生，永远不会辜负你。'
    rt = split_sentence(r_text)
    print(rt)
