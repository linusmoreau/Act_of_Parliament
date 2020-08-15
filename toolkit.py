import random


def round_up(num):
    return int(num) + (int(num) != num)


def largest_in_dictionary(d):
    keys = list(d)
    biggest = keys[0]
    thics = [biggest]
    for key in d:
        if d[key] > d[biggest]:
            biggest = key
            thics = [biggest]
        elif d[key] == d[biggest]:
            thics.append(key)
    if len(thics) > 1:
        biggest = random.choice(thics)
    return biggest


def capitalize(string):
    string = str(string).lower()
    if 97 <= ord(string[0]) <= 122:
        string = chr(ord(string[0]) - 32) + string[1:]
    return string


def entitle(title):
    syncategorematics = {'a', 'an', 'the', 'for', 'and', 'nor', 'but', 'or', 'yet', 'so', 'as', 'at', 'by', 'in', 'of',
                         'on', 'per', 'to', 'with', 'into'}
    title = str(title)
    title.replace('_', ' ')
    words = title.split()
    title = capitalize(words.pop(0))
    for word in words:
        title += ' '
        if word.lower() not in syncategorematics:
            title += capitalize(word)
        else:
            title += word.lower()
    return title


def translate_bool_string(string, default=None):
    if string in ["true", 't']:
        out = True
    elif string in ["false", 'f']:
        out = False
    elif string in ["default", 'd']:
        out = default
    else:
        out = None
    return out
