from ui import *
from toolkit import *
import date_kit


choice = 'Norway'
view = 'parties'

key = None

if choice == 'Germany':
    key = ['CDU/CSU', 'SPD', 'AfD', 'FDP', 'Linke', 'Gr\u00fcne']
    col = {'CDU/CSU': (0, 0, 0), 'Gr\u00fcne': (100, 161, 45), 'SPD': (235, 0, 31), 'FDP': (255, 237, 0),
           'AfD': (0, 158, 224), 'Linke': (190, 48, 117)}
    # coalitions = [['Gr\u00fcne', 'CDU/CSU'], ]
    file_name = 'german_polling.txt'
    spread = 7
elif choice == 'Norway':
    key = ['R', 'SV', 'MDG', 'Ap', 'Sp', 'V', 'KrF', 'H', 'FrP']
    col = {'R': (231, 52, 69), 'SV': (188, 33, 73), 'MDG': (106, 147, 37), 'Ap': (227, 24, 54), 'Sp': (0, 133, 66),
           'V': (17, 100, 104), 'KrF': (254, 193, 30), 'H': (135, 173, 215), 'FrP': (2, 76, 147)}
    file_name = 'norway_polling.txt'
    spread = 30
else:
    raise ValueError("No such choice.")

cycle = len(key) + 7
start = 4
date = 1

dat: Dict[str, Dict[int, List[float]]] = {}
for n in key:
    dat[n] = {}
f = open(file_name, 'r')

rot = None
end = 0

for line in f:
    if line[:2] == '|}':
        rot = None
    elif rot is None:
        if 'http' in line:
            rot = 1
    else:
        if rot == 1:
            lin = line[:line.find('{')]
            dates = lin.split('|')[-1]
            temp = dates.split('â€“')[-1].strip()
            end_date = date_kit.Date(text=temp, form='dmy')
            end = date_kit.date_dif(date_kit.Date(2021, 1, 1), end_date)
            # print('\n' + str(end), end_date)
        elif start <= rot < start + len(key):
            p = rot - start
            if "style=" in line:
                share = float(line.split('|')[-1].strip().strip("'"))
            else:
                share = float(line.strip('|').strip())
            # print(key[rot], share)
            if end in dat[key[p]]:
                dat[key[p]][end].append(share)
            else:
                dat[key[p]][end] = [share]
        elif 'http' in line or '[[' in line:
            rot = 0
        rot += 1
f.close()

# print(dat)

ndat = rolling_averages(dat, spread)
date = Date(2021, 1, 1)
title = "Opinion Polling for the 2021 Federal Election in " + choice
graph = GraphDisplay(screen_center, (screen_width, screen_height), ndat, x_title=None, y_title="Support (%)",
                     title=title, step=1, align=CENTER, colours=col, initial_date=date, leader=True, y_min=0,
                     dat_points=dat)
graph.show()
game_loop()

