from ui import *
from toolkit import *
import date_kit


choice = 'Norway'
# view = 'parties'
restart = '[http'
key = None
date = 1

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
           'V': (17, 100, 104), 'KrF': (254, 193, 30), 'H': (135, 173, 215), 'FrP': (2, 76, 147)}
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
else:
    raise ValueError("No such choice.")


dat: Dict[str, Dict[int, List[float]]] = {}
for n in key:
    dat[n] = {}
f = open(file_name, 'r')

rot = None
end = 0
year = '2021'

content = f.readlines()
i = 0
while i < len(content):
    line = content[i]
    # print(rot, line, end='')
    if '===' in line:
        year = line.strip().strip('=').strip()
    elif line[:2] == '|}':
        rot = None
    elif rot is None:
        if restart in line:
            rot = 0
    if rot is not None:
        if rot == 1:
            if choice == "Norway":
                line = line[:line.find('{')]
            elif choice == "Peru":
                line = line.strip().strip('}')
            elif choice == 'Czechia' and 'rowspan="2"' in line:
                i += 20
                rot += 2
            dates = line.split('|')[-1]
            if '-' in dates:
                temp = dates.split('-')
            else:
                temp = dates.split('â€“')
            temp = temp[-1].strip()
            # print(temp)
            if len(temp.split()) == 2:
                temp = temp + ' ' + year
            elif len(temp.split()) == 1:
                temp = '1' + ' ' + temp + ' ' + year
            # print(temp)
            end_date = date_kit.Date(text=temp, form='dmy')
            end = date_kit.date_dif(date_kit.Date(2021, 1, 1), end_date)
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
            if "'''" in line:
                share = float(line.split('|')[-1].strip().strip("'"))
            else:
                share = float(line.split('|')[-1].strip())
            # print(key[rot], share)
            if end in dat[key[p]]:
                dat[key[p]][end].append(share)
            else:
                dat[key[p]][end] = [share]
        elif restart in line or 'election' in line:
            rot = 0
        rot += 1
    i += 1
f.close()

# print(dat)

ndat = weighted_averages(dat, spread, power=1)
date = Date(2021, 1, 1)
title = "Opinion Polling for " + choice
graph = GraphDisplay(screen_center, (screen_width, screen_height), ndat, x_title=None, y_title="Support (%)",
                     title=title, step=1, align=CENTER, colours=col, initial_date=date, leader=True, y_min=0,
                     dat_points=dat)
graph.show()
game_loop()

