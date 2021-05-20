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


def central_rolling_average(dat: Dict[float, List[float]], breadth: float):
    ndat = {}
    relv: List[Tuple] = []
    in_ord = sorted(list(dat.keys()))
    mini = in_ord[0]
    first = True
    for x in in_ord:
        for y in dat[x]:
            relv.append((x, y))
        cutoff: int = 0
        for i, point in enumerate(relv):
            if x - point[0] <= breadth:
                cutoff = i
                break
        relv = relv[cutoff:]
        if x >= mini + breadth / 2:
            if first:
                ndat[mini] = sum([p[1] for p in relv]) / len(relv)
                first = False
            else:
                ndat[x - breadth / 2] = sum([p[1] for p in relv]) / len(relv)
    maxi = relv[-1][0]
    in_ord = in_ord[in_ord.index(relv[0][0]):]
    for j, x in enumerate(in_ord):
        cutoff: int = 0
        for i, point in enumerate(relv):
            if point[0] != x:
                cutoff = i
                break
        relv = relv[cutoff:]
        if j + 1 < len(in_ord) and in_ord[j + 1] + breadth / 2 > maxi:
            ndat[maxi] = sum([p[1] for p in relv]) / len(relv)
            break
        else:
            ndat[x + breadth / 2] = sum([p[1] for p in relv]) / len(relv)
    return ndat


def rolling_averages(dat: Dict[str, Dict[float, List[float]]], breadth: float, central: bool = False) \
        -> Dict[str, Dict[float, List[float]]]:
    ndat = {}
    for line, points in dat.items():
        if central:
            npoints = central_rolling_average(points, breadth)
        else:
            npoints = rolling_average(points, breadth)
        ndat[line] = npoints
    return ndat


def weighted_average(dat: Dict[float, List[float]], breadth: float, res: int, power: int = 1):
    def weight(disp, power):
        w = (1 - (abs(disp) / (breadth / 2))) ** power
        if w < 0:
            raise ValueError("Displacement is outside of range")
        else:
            return w

    ndat = {}
    relv: List[int] = []
    upcome = sorted(list(dat.keys()))
    # print(upcome)
    mini = upcome[0]
    maxi = upcome[-1]
    step = (maxi - mini) / res
    for i in range(res + 1):
        place = round(mini + step * i)
        if place > maxi:
            break

        cutoff: int = -1
        for j, x in enumerate(upcome):
            # print(x, place, breadth / 2)
            if x >= place + breadth / 2:
                cutoff = j
                break
        if cutoff == -1:
            relv.extend(upcome)
            upcome = []
        else:
            relv.extend(upcome[:cutoff])
            upcome = upcome[cutoff:]

        cutoff = -1
        for j, x in enumerate(relv):
            if x >= place - breadth / 2:
                cutoff = j
                break
        if cutoff == -1:
            continue
        else:
            relv = relv[cutoff:]
        # print(relv, upcome)
        try:
            ndat[place] = (sum([sum(dat[x]) * weight(x - place, power) for x in relv]) /
                           sum([len(dat[x]) * weight(x - place, power) for x in relv]))
        except ZeroDivisionError:
            pass
    return ndat


def weighted_averages(dat: Dict[str, Dict[float, List[float]]], breadth: float, res=None, power=1) \
        -> Dict[str, Dict[float, List[float]]]:
    ndat = {}
    for line, points in dat.items():
        if res is None:
            inres = (max(list(points.keys())) - min(list(points.keys()))) // 6
        else:
            inres = res
        ndat[line] = weighted_average(points, breadth, inres, power)
    return ndat
