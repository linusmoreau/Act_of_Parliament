import random
from typing import Dict, List, Tuple


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


def variable_weight(disp, breadth, loc: float = 3):
    w = (1 - (abs(disp) / breadth) ** 2) ** loc
    if w < 0:
        raise ValueError("Displacement is outside of range")
    else:
        return w


def cube_weight(disp, breadth):
    w = (1 - (abs(disp) / breadth) ** 3) ** 3
    if w < 0:
        raise ValueError("Displacement is outside of range")
    else:
        return w


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


def weighted_average(dat: Dict[float, List[float]], breadth: float, res: int, loc=False, start=None, end=None,
                     line_starts=None, line_ends=None):
    ndat = {}
    relv: List[int] = []

    upcome = sorted(filter(lambda k: len(dat[k]) > 0, list(dat.keys())))
    disc = []
    if upcome[0] - breadth / 4 <= line_starts:
        mini = line_starts
    else:
        mini = upcome[0]
    # print(mini, start, line_starts, upcome[0])
    if start is not None and mini < start:
        mini = start
    if upcome[-1] + breadth / 4 >= line_ends:
        maxi = line_ends
    else:
        maxi = upcome[-1]
    if end is not None and maxi > end:
        maxi = end
    place = mini
    step = (upcome[-1] - upcome[0]) / res
    while True:
        if place > maxi:
            place = maxi
        cutoff: int = -1
        for j, x in enumerate(upcome):
            if x >= place + breadth:
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
            if x >= place - breadth:
                cutoff = j
                break
        if cutoff != -1:
            disc.extend(relv[:cutoff])
            relv = relv[cutoff:]
        shown = relv.copy()
        spread = breadth
        try:
            if loc:
                locnum = sum([cube_weight(x - place, spread) for x in shown])
                if locnum < 3:
                    locnum = 3
                ndat[place] = (sum([sum(dat[x]) * variable_weight(x - place, spread, locnum) for x in shown]) /
                               sum([len(dat[x]) * variable_weight(x - place, spread, locnum) for x in shown]))
            else:
                ndat[place] = (sum([sum(dat[x]) * cube_weight(x - place, spread) for x in shown]) /
                               sum([len(dat[x]) * cube_weight(x - place, spread) for x in shown]))
        except ZeroDivisionError:
            pass
        if place == maxi:
            break
        else:
            place += step
    return ndat


# def weighted_average2(dat: Dict[float, List[float]], breadth: int, res: int, end=None):
#     # breadth here is the number of data points included in either direction
#     ndat = {}
#
#     points = sorted(filter(lambda k: len(dat[k]) > 0, list(dat.keys())))
#     mini = points[0]
#     if end is None:
#         maxi = points[-1]
#     else:
#         maxi = end
#     step = (maxi - mini) / res
#     relv = []
#     for i in range(res + 1):
#         place = round(mini + step * i)
#         if place > maxi:
#             break
#
#         for j, x in enumerate(points):
#             if x > place:
#                 cutoff = j
#                 break
#         else:
#             cutoff = None
#         if cutoff is not None:
#             s = cutoff - breadth
#             if s < 0:
#                 s = 0
#             e = cutoff + breadth
#             if e >= len(points):
#                 e = -1
#             relv = points[s:e]
#         b = max([abs(relv[0] - place), abs(relv[-1] - place)])
#         try:
#             ndat[place] = (sum([sum(dat[x]) * cube_weight(x - place, b) for x in relv]) /
#                            sum([len(dat[x]) * cube_weight(x - place, b) for x in relv]))
#         except ZeroDivisionError:
#             pass
#     return ndat

# def loess(dat: Dict[float, List[float]], breadth: float, res: int):
#     ndat = {}
#     relv: List[int] = []
#     upcome = sorted(list(dat.keys()))
#     # print(upcome)
#     mini = upcome[0]
#     maxi = upcome[-1]
#     step = (maxi - mini) / res
#     for i in range(res + 1):
#         place = round(mini + step * i)
#         if place > maxi:
#             break
#
#         cutoff: int = -1
#         for j, x in enumerate(upcome):
#             # print(x, place, breadth / 2)
#             if x >= place + breadth / 2:
#                 cutoff = j
#                 break
#         if cutoff == -1:
#             relv.extend(upcome)
#             upcome = []
#         else:
#             relv.extend(upcome[:cutoff])
#             upcome = upcome[cutoff:]
#
#         cutoff = -1
#         for j, x in enumerate(relv):
#             if x >= place - breadth / 2:
#                 cutoff = j
#                 break
#         if cutoff == -1:
#             continue
#         else:
#             relv = relv[cutoff:]
#         # print(relv, upcome)
#         try:
#             # w = sum([weight(x - place, breadth) for x in relv])
#             # xavg = sum([x * weight(x - place, breadth) for x in relv]) / w
#             yavg = (sum([sum(dat[x]) * weight(x - place, breadth) for x in relv]) /
#                     sum([len(dat[x]) * weight(x - place, breadth) for x in relv]))
#             # beta1 = ((sum([weight(x - place, breadth) * x * sum(dat[x]) for x in relv]) - xavg * yavg * w) /
#             #          (sum([weight(x - place, breadth) * x**2 for x in relv]) - xavg**2 * w))
#             # beta0 = yavg - beta1 * xavg
#             # print(beta1)
#             ndat[place] = yavg
#         except ZeroDivisionError:
#             pass
#     return ndat


def weighted_averages(dat: Dict[str, Dict[float, List[float]]], breadth: int, res=None, loc=False,
                      start=None, end=None) -> Dict[str, Dict[float, List[float]]]:
    # Breadth is the x-distance considered in either direction
    ndat = {}
    mini = min([min(list(d.keys())) for d in dat.values()])
    if start is not None and mini - breadth <= start:
        line_starts = start
    else:
        line_starts = mini
    maxi = max([max(list(d.keys())) for d in dat.values()])
    if end is not None and maxi + breadth >= end:
        line_ends = end
    else:
        line_ends = maxi
    for line, points in dat.items():
        if res is None:
            inres = (max(list(points.keys())) - min(list(points.keys()))) // 4
            if inres == 0:
                inres = 1
            elif inres < 50:
                inres = 50
        else:
            inres = res
        ndat[line] = weighted_average(points, breadth, inres, loc, start, end, line_starts, line_ends)
    return ndat


def geothmetic_meandian(seq):
    def arithmetic_mean(seq):
        return sum(seq) / len(seq)

    def geometric_mean(seq):
        tot = None
        for t in seq:
            if tot is None:
                tot = t
            else:
                tot *= t
        return tot ** (1 / len(seq))

    def median(seq):
        seq = sorted(seq)
        if len(seq) % 2 == 0:
            return (seq[(len(seq) + 1) // 2 - 1] + seq[(len(seq) + 1) // 2]) / 2
        else:
            return seq[(len(seq) + 1) // 2 - 1]

    if len(seq) == 3 and abs(seq[0] - seq[1]) + abs(seq[0] - seq[2]) + abs(seq[1] - seq[2]) < 0.001:
        return round(median(seq), 3)
    else:
        inter = (arithmetic_mean(seq), geometric_mean(seq), median(seq))
        # print(inter)
        return geothmetic_meandian(inter)


class CustomObject:
    def json_dump(self):
        def deep_identifier(d):
            if isinstance(d, Dict):
                for k, a in d.items():
                    if isinstance(a, (Dict, List)):
                        d[k] = deep_identifier(a)
                    elif isinstance(a, CustomObject):
                        d[k] = a.identifier()
            elif isinstance(d, List):
                for i, a in enumerate(d):
                    if isinstance(a, (Dict, List)):
                        d[i] = deep_identifier(a)
                    elif isinstance(a, CustomObject):
                        d[i] = a.identifier()
            return d

        attr = self.__dict__.copy()
        attr = deep_identifier(attr)
        attr["type"] = type(self).__name__
        return attr

    def identifier(self):
        raise ValueError("No identifier")


if __name__ == '__main__':
    seq = tuple(range(1, 90))
    print(geothmetic_meandian(seq))
