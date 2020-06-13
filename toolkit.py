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
    string = str(string)
    if 97 <= ord(string[0]) <= 122:
        string = chr(ord(string[0]) - 32) + string[1:]
    return string
