from ui import *
from toolkit import *
import date_kit


choice = 'Germany'
view = 'parties'
restart = '[http'
key = None
date = 1
spread = 60

blocs = None
if choice == 'Germany':
    key = ['CDU/CSU', 'SPD', 'AfD', 'FDP', 'Linke', 'Gr\u00fcne']
    col = {'CDU/CSU': (0, 0, 0), 'Gr\u00fcne': (100, 161, 45), 'SPD': (235, 0, 31), 'FDP': (255, 237, 0),
           'AfD': (0, 158, 224), 'Linke': (190, 48, 117)}
    # coalitions = [['Gr\u00fcne', 'CDU/CSU'], ]
    file_name = 'test_data/german_polling.txt'
    spread = 30
    start = 4
elif choice == 'Norway':
    key = ['R', 'SV', 'MDG', 'Ap', 'Sp', 'V', 'KrF', 'H', 'FrP']
    col = {'R': (231, 52, 69), 'SV': (188, 33, 73), 'MDG': (106, 147, 37), 'Ap': (227, 24, 54), 'Sp': (0, 133, 66),
           'V': (17, 100, 104), 'KrF': (254, 193, 30), 'H': (135, 173, 215), 'FrP': (2, 76, 147),
           'Red-Green': (227, 24, 54), 'Blue': (135, 173, 215)}
    blocs = {'Red-Green': ['R', 'SV', 'Ap', 'Sp'], 'Blue': ['V', 'KrF', 'H', 'FrP']}
    file_name = 'test_data/norway_polling.txt'
    spread = 60
    start = 4
elif choice == 'Peru':
    key = ['Castillo', 'Fujimori']
    col = {'Castillo': (192, 10, 10), 'Fujimori': (255, 128, 0)}
    file_name = 'test_data/peru_polling.txt'
    spread = 30
    start = 3
    restart = 'http'
elif choice == 'Czechia':
    key = ['ANO', 'SPOLU', 'Pirati+STAN', 'SPD', 'KSCM', 'CSSD']
    col = {'ANO': (38, 16, 96), 'SPOLU': (35, 44, 119), 'Pirati+STAN': (0, 0, 0), 'SPD': (33, 117, 187),
           'KSCM': (204, 0, 0), 'CSSD': (236, 88, 0)}
    file_name = 'test_data/czechia_polling.txt'
    spread = 60
    start = 4
elif choice == 'Canada':
    key = ['CON', 'LIB', 'NDP', 'BQ', 'GPC', 'PPC']
    col = {'CON': (100, 149, 237), 'LIB': (234, 109, 106), 'NDP': (244, 164, 96), 'BQ': (135, 206, 250),
           'GPC': (153, 201, 85), 'PPC': (131, 120, 158)}
    file_name = 'test_data/canada_polling.txt'
    spread = 60
    start = 3
elif choice == 'Iceland':
    key = ['D', 'V', 'S', 'M', 'B', 'P', 'F', 'C', 'J']
    col = {'D': (0, 173, 239), 'V': (0, 184, 120), 'S': (234, 0, 56), 'M': (0, 33, 105), 'B': (160, 208, 103),
           'P': (137, 110, 189), 'F': (255, 202, 62), 'C': (255, 125, 20), 'J': (239, 72, 57)}
    file_name = 'test_data/iceland_polling.txt'
    spread = 60
    start = 4
elif choice == 'Italy':
    key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'LeU', '+Eu', 'EV', 'C!', 'A', 'IV']
    col = {'M5S': (255, 235, 59), 'PD': (239, 28, 39), 'Lega': (0, 128, 0), 'FI': (0, 135, 220), 'FdI': (3, 56, 106),
           'LeU': (199, 40, 55), '+Eu': (255, 215, 0), 'EV': (115, 193, 112), 'C!': (229, 131, 33), 'A': (0, 57, 170),
           'IV': (214, 65, 140), 'NcI': (31, 107, 184), 'PaP': (160, 20, 46)}
    file_name = 'test_data/italy_polling.txt'
    spread = 60
    date = 0
    start = 2
else:
    raise ValueError("No such choice.")


dat: Dict[str, Dict[int, List[float]]] = {}
f = open(file_name, 'r')

rot = None
end = 0
year = '2021'

content = f.readlines()
i = 0
prevline = None
while i < len(content):
    line = content[i]
    # print(rot, line, end='')
    if '===' in line:
        year = line.strip().strip('=').strip()
    elif line[:2] == '|}':
        rot = None
    if restart in line:
        rot = 0
    if rot is not None:
        if rot == date:
            if choice == "Norway":
                line = line[:line.find('{')]
            elif choice == "Peru":
                line = line.strip().strip('}')
            elif choice == 'Czechia' and 'rowspan="2"' in line:
                i += 20
                rot += 2
            elif choice == "Italy":
                line = prevline
                if line[0] == '!':
                    rot = None
                    i += 1
                    continue
            dates = line.split('|')[-1]
            if '-' in dates:
                temp = dates.split('-')
            else:
                temp = dates.split('â€“')
            temp = temp[-1].strip()
            # print(temp)
            temps = temp.split()
            if len(temps) == 2:
                try:
                    year = int(temps[-1])
                    temp = '1 ' + temp
                except ValueError:
                    temp = temp + ' ' + year
            elif len(temps) == 1:
                temp = '1' + ' ' + temp + ' ' + year
            end_date = date_kit.Date(text=temp, form='dmy')
            end = date_kit.date_dif(date_kit.Date(2021, 1, 1), end_date)
            if choice == "Italy":
                if end_date.__repr__() == "2019-04-09":
                    key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'LeU', '+Eu', 'NcI', 'PaP']
                elif end_date.__repr__() == "2019-09-19":
                    key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'LeU', '+Eu', 'EV', 'C!', 'A']
                elif end_date.__repr__() == "2019-09-10":
                    key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'LeU', '+Eu', 'EV', 'C!']
                elif end_date.__repr__() == "2019-08-12":
                    key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'LeU', '+Eu', 'EV']
            # print('\n' + str(end), end_date)
        elif rot == 0 and choice == 'Canada':
            # print(line)
            parts = line.split('||')
            temp = parts[date].split('|')[-1].strip().strip('}')
            end_date = date_kit.Date(text=temp, form='mdy')
            end = date_kit.date_dif(date_kit.Date(2021, 1, 1), end_date)
            for n, p in enumerate(key):
                if "''" in parts[start + n]:
                    share = float(parts[start + n].split('|')[-1].strip().strip("'"))
                else:
                    num = parts[start + n].split('|')[-1].strip()
                    if num == '{{n/a}}' or num == '' or \
                            parts[start + n].split('|')[0].strip() == 'style="color:#F8F9FA;"':
                        continue
                    else:
                        share = float(num)
                if p not in dat:
                    dat[p] = {}
                if end in dat[p]:
                    dat[p][end].append(share)
                else:
                    dat[p][end] = [share]
            if "2019 Canadian federal election" in line:
                key = ['LIB', 'CON', 'NDP', 'BQ', 'GPC', 'PPC']
            i += 1
            rot = None
            continue
        elif start <= rot < start + len(key):
            p = rot - start
            temp = line.split('|')[-1].strip()
            if "'''" in line:
                share = float(temp.strip("'"))
            elif temp == 'â€“' or temp == '-' or temp == '' or "small" in temp:
                if view == 'blocs' or view == 'both':
                    share = 0
                else:
                    rot += 1
                    i += 1
                    continue
            else:
                try:
                    share = float(temp.strip())
                except ValueError:
                    # print(temp)
                    if view == 'blocs' or view == 'both':
                        share = 0
                    else:
                        rot += 1
                        i += 1
                        continue
            # print(key[rot], share)
            if key[p] not in dat:
                dat[key[p]] = {}
            if end in dat[key[p]]:
                dat[key[p]][end].append(share)
            else:
                dat[key[p]][end] = [share]
        elif restart in line or 'election' in line:
            rot = 0
        rot += 1
    i += 1
    prevline = line
f.close()

if view == 'blocs' or view == 'both':
    bdat = {}
    for b, ps in blocs.items():
        bdat[b] = {}
        for p in ps:
            for x, ys in dat[p].items():
                if x in bdat[b].keys():
                    for i, y in enumerate(ys):
                        bdat[b][x][i] += y
                else:
                    bdat[b][x] = ys.copy()
    if view == 'both':
        dat.update(bdat)
    else:
        dat = bdat
# print(dat)

ndat = weighted_averages(dat, spread)
date = Date(2021, 1, 1)
title = "Opinion Polling for " + choice
graph = GraphDisplay(screen_center, (screen_width, screen_height), ndat, x_title=None, y_title="Support (%)",
                     title=title, step=1, align=CENTER, colours=col, initial_date=date, leader=True, y_min=0,
                     dat_points=dat)
graph.show()
game_loop()

