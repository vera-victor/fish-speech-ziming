import json
import os

cur_path = os.path.split(os.path.realpath(__file__))[0]

def get_json(path):
    with open(path) as f_json:
        EN_word2phone = json.load(f_json)
    return EN_word2phone


EN_word2phone = get_json(os.path.join(cur_path, "en_words2phone.json"))
