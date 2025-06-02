import re

ordinal_dict = {
    "one -st": "first",
    "two -nd": "second",
    "three -rd": "third",
    "four -th": "fourth",
    "five -th": "fifth",
    "six -th": "sixth",
    "seven -th": "seventh",
    "eight -th": "eighth",
    "nine -th": "nineth",
    "ten -th": "tenth",
    "eleven -th": "eleventh",
    "twelve -th": "twelfth",
    "thirteen -th": "thirteenth",
    "fourteen -th": "fourteenth",
    "fifteen -th": "fifteenth",
    "sixteen -th": "sixteenth",
    "seventeen -th": "seventeenth",
    "eighteen -th": "eighteenth",
    "ninteen -th": "ninteenth",
    "twenty -th": "twentieth",
    "thirty -th": "thirtieth",
    "forty -th": "fortieth",
    "fifty -th": "fiftieth",
    "sixty -th": "sixtieth",
    "seventy -th": "seventieth",
    "eighty -th": "eightieth",
    "ninety -th": "ninetieth",
    "hundred -th": "hundredth",
}


def parse_ordinal_number(text):
    def func(match):
        ord_num = ordinal_dict.get(match.group(2), match.group(2))
        return match.group(1) + ord_num

    text = re.sub(r"(^| )(([a-zA-Z]+) -((st)|(th)|(rd)|(nd)))", func, text)

    return text


if __name__ == '__main__':
    print(parse_ordinal_number("Sri Lankawe Diya e l i, one -st ed"))
    # print(re.search("[a-zA-Z]+ -st", "Sri Lankawe Diya e l i, one -st ed"))
