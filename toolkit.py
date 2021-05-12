import random
from typing import Dict, List, Set, Tuple, Any


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
    title = title.replace('_', ' ')
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


def rolling_average(dat: Dict[float, List[float]], breadth: float):
    ndat = {}
    relv: List[Tuple] = []
    for x in sorted(list(dat.keys())):
        for y in dat[x]:
            relv.append((x, y))
        cutoff: int = 0
        for i, point in enumerate(relv):
            if x - point[0] <= breadth:
                cutoff = i
                break
        relv = relv[cutoff:]
        ndat[x] = sum([p[1] for p in relv]) / len(relv)
    return ndat


def rolling_averages(dat: Dict[str, Dict[float, List[float]]], breadth: float):
    ndat = {}
    for line, points in dat.items():
        npoints = rolling_average(points, breadth)
        ndat[line] = npoints
    return ndat
