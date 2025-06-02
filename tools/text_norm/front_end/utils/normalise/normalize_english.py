import numpy as np
import re

from tools.text_norm.front_end.utils.normalise.parse_ordinal_num import parse_ordinal_number
from tools.text_norm.front_end.utils.normalise.parse_word_complex import parse_complex
from tools.text_norm.front_end.utils.normalise.tokenize_text_english import tokenize, extract_letter_only
from tools.text_norm.front_end.utils.normalise.predict_class_english import predict_class_

from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.address import address
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.cardinal import cardinal
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.date import date
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.decimal_ import decimal
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.digit import digit
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.electronic import electronic
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.fraction import fraction
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.letters import letters
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.measure import measure
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.money import money
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.ordinal import ordinal
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.plain import plain
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.telephone import telephone
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.time import time
from tools.text_norm.front_end.utils.normalise.en_normalize_funcs.verbatim import verbatim

alphabet_pronunciation_dict = {"A": "a", "B": "b", "C": "c",
                               "D": "d", "E": "e", "F": "f",
                               "G": "g", "H": "h", "I": "i",
                               "J": "j", "K": "k", "L": "l",
                               "M": "m", "N": "n", "O": "o",
                               "P": "p", "Q": "q", "R": "r",
                               "S": "s", "T": "t", "U": "u",
                               "V": "v", "W": "w", "X": "x",
                               "Y": "y", "Z": "z"}

def punct(text):
    return text

def fix_telephone(output):
    ''' if class prediction is telephone, normalized output always has "sil" string in between numbers- remove them. '''
    return output.replace("sil ", ", ")

def fix_letters(output):
    ''' replace sequence of single alphabets (separated by space) with their pronunciations '''
    split_by_space = output.split(" ")
    return " ".join([alphabet_pronunciation_dict[ch.upper()] if ch.upper() in alphabet_pronunciation_dict else ch for ch in split_by_space])

def fix_electronic(output):
    output = output.replace("c o m", "com")
    return fix_letters(output)

def fix_plural_alphabets(output, prev_word_eos):
    ''' replace plural form of single alphabets (e.g. A's, b's) with their correct pronunciations 
        : param prev_word_eos: whether previous word had EOS punc (i.e. end of sentence)- 
                              this case capital letter can be due to beginning of sentence (e.g. As ...)'''
    if re.findall("[a-zA-Z]'s", output) and output == re.findall("[a-zA-Z]'s", output)[0]:
        output = alphabet_pronunciation_dict[output[0].upper()] + "s"

    elif not prev_word_eos and re.findall("[A-Z]s", output) and output == re.findall("[A-Z]s", output)[0]: # As Bs Cs
        output = alphabet_pronunciation_dict[output[0].upper()] + "s"

    return output


def predict(classes, words):
    '''
        : param classes: predicted normalization classes of the words
        : param words: original words
    '''
    functions = [address, cardinal, date, decimal, digit, electronic, fraction,
                 letters, measure, money, ordinal, plain, telephone, time, verbatim, punct]

    acceptable_puncs= [' ', '!', "'", ',', '.', '-', '?', '~']
    acceptable_EOS_puncs = ['!', '.', '?', '~']
    error_values = ["AAAis is wrong!", 0]

    prev_word_eos = True # Is previous word End Of Sentence? (i.e. ending with EOS punctuation?)
    final = []
    for i, p in enumerate(classes):
        #print(words[i], p)
        # fixing class for "no", since it's ALWAYS incorrectly classified as "LETTERS"(=acronym) class
        if extract_letter_only(words[i]) == "no":
            p = "plain"

        # save (tts-acceptable) eos punc separately (because it could be removed during normalization process)
        eos_punc = ""
        word_eos = False
        if sum([w in acceptable_puncs for w in words[i]])<len(words[i]) and words[i][-1] in acceptable_puncs:
            eos_punc = words[i][-1]
            words[i] = words[i][:-1]
            word_eos = True if words[i][-1] in acceptable_EOS_puncs else False

        try:
            f_i = [ii for ii, f in enumerate(functions) if p.lower()==f.__name__][0] #function index

            # if the class prediction is "verbatim", just pass the original word 
            # this function just replaces special chars to their names (e.g. ~ -> tilde) - unnecessary.
            if p.lower()=="verbatim":
                pred = words[i]
            else:
                pred = functions[f_i]([words[i]])[0]  # make normalization predictions
                pred = pred[0] if np.shape(pred)==(1,) else pred

            # if error occurred during normalization, just return the original word
            if pred in error_values or pred=="":
                pred = words[i]
                pred += eos_punc # if original word had EOS punc, re-insert it at the end
                final.append(pred)
                continue

            word_no_punc = re.sub(r"[^a-zA-Z]", "", words[i])
            if p.lower()=="telephone":
                pred = fix_telephone(pred)

            elif p.lower()=="electronic":
                pred = fix_electronic(pred)

            elif p.lower()=="letters":
                pred = fix_letters(pred)

            # replacing single alphabet word (except 'a') with its pronunciation            
            elif len(word_no_punc) == 1 and word_no_punc.lower() != "a":
                pred = words[i].replace(word_no_punc, alphabet_pronunciation_dict[word_no_punc.upper()])

            pred = fix_plural_alphabets(pred, prev_word_eos)

            pred += eos_punc # if original word had EOS punc, re-insert it at the end
            final.append(pred)

        except: # if any error caused during normalization, just return the original word
            final.append(words[i])

        prev_word_eos = word_eos

    return final


def normalize_(text):
    input_text = text.strip().split("\n")
    input_text = [t for t in input_text if t!=""]

    tokens = [tokenize(t) for t in input_text]
    if len(tokens) == 0 or len(tokens[0]) == 0:
        return text
    classes = [predict_class_(t) for t in tokens] # predict classes

    final = []
    for i in range(len(tokens)):
        preds = predict(classes[i], tokens[i])
        final.append(preds)

    result = "\n\n".join([" ".join(f) for f in final]).replace(" , ",", ").replace(" . ", ". ").replace("@", "at")

    # remove repeated symbols and spaces        
    reg_spacedSymbols = re.compile(r'(\W+?)\1+')
    result = reg_spacedSymbols.sub(r'\1',result)
    # print('#########',result)
    # replace ", " in the beginning of a line due to opening bracket substitutions
    result = result.replace("\n, ", "\n")
    # return result.strip(), classes
    result = parse_ordinal_number(result)  # 处理英文序数
    # print('#########', result)
    result = parse_complex(result)  # 处理's的复数形式
    # print('#########',result)
    return result.strip()


if __name__ == '__main__':
    print(normalize_("In the 1950s a mining school built in z buch ."))
    # print(normalize_("it's a dog."))
    # print(normalize_("Project Horizon is the school's near space programme founded in 2012 which runs annual missions ."))
    # print(normalize_("99.3% , #EMNLP 2017 ."))

