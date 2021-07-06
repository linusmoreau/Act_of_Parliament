from ui import *
from toolkit import *
import date_kit
import types
import datetime
import urllib.request
import threading
from bs4 import BeautifulSoup
from data import get_riding_data


options = ['Austria', 'Brazil', 'Bulgaria', 'Canada', 'Cyprus', 'Czechia', 'Denmark', 'Finland', 'Germany',
           'Hungary', 'Iceland', 'Ireland', 'Italy', 'Norway', 'Peru', 'Poland', 'Portugal', 'Slovakia', 'Spain',
           'Sweden', 'UK', 'New York']
olddata = {
    'Canada':   'test_data/old_canada_polling.txt',
    'Denmark':  'test_data/old_denmark_polling.txt',
    'Germany':  'test_data/old_germany_polling.txt',
    'Ireland':  'test_data/old_ireland_polling.txt',
    'Italy':    'test_data/old_italy_polling.txt',
    'Norway':   'test_data/old_norway_polling.txt',
    'Poland':   'test_data/old_poland_polling.txt',
    'UK':       'test_data/old_uk_polling.txt'
}
tod = str(datetime.date.today())
today = Date(int(tod[:4]), int(tod[5:7]), int(tod[8:]))


def read_data(content, key, start, restart, date, choice, include=None):
    def isrestart(line):
        if choice == 'Slovakia' and \
                'url=https://sava.sk/en/clenstvo/zoznam-clenov/|access-date=2021-03-27|language=en-US}}' in line:
            return False
        else:
            return sum(map(lambda r: r in line, restart))

    dat: Dict[str, Dict[int, List[float]]] = {}
    rot = None
    end = 0
    year = '2021'
    i = 0
    prevline = None
    flag = False
    while i < len(content):
        line = content[i]
        nline = line
        # print(rot, line, end='')
        if '===' in line:
            year = line.strip().strip('=').strip()
            if choice == 'Poland' and year == "2019":
                key = ['United Right', 'Civic Coalition', 'The Left', 'Polish Coalition', 'Confederation']
        elif line[:2] == '|}':
            rot = None
        elif choice == 'Poland':
            if "The [[Polish Coalition]] parts ways with member party [[Kukiz'15]]" in line:
                key = ['United Right', 'Civic Coalition', 'The Left', 'Polish Coalition', 'Confederation',
                       'Poland 2050']
        elif choice == 'New York':
            if '<!--' in line:
                line = line[:line.find('<!--')]
        elif choice == 'Ireland':
            if rot == 1 and 'url=' in line:
                i += 1
                continue
            if '|8 February 2020' in line:
                key = ['FG', 'FF', 'SF', 'Lab', 'PBP/S', 'SD', 'GP', 'O/I', 'O/I', 'O/I']
                flag = True
        if isrestart(line):
            rot = 0
        if rot is not None:
            if rot == date:
                if choice in ['Norway', 'Austria']:
                    line = line[:line.find('{')]
                elif choice == 'Sweden':
                    if 'ref' in line:
                        i += 1
                        continue
                elif choice == 'Czechia':
                    if 'rowspan="2"' not in line:
                        rot += 23
                        i += 1
                    if 'rowspan="2"' in prevline:
                        rot += 1
                elif choice in ['Italy', 'Cyprus', 'Slovakia', 'Hungary', 'Ireland']:
                    line = prevline
                    if line[0] == '!':
                        rot = None
                        i += 1
                        continue
                elif choice == "Poland":
                    if 'style=' in line:
                        rot = None
                        i += 1
                        continue
                line = line.strip().strip('}\'')
                if choice == 'Ireland' and 'dts' in line:
                    temp = line.strip('|').split('|')
                    d = temp[-1]
                    m = temp[-2]
                    y = temp[-3]
                    temp = d + ' ' + m + ' ' + y
                elif choice == 'UK' and 'opdrts' in line:
                    temp = line.strip('|').split('|')
                    y = temp[-1]
                    m = temp[-2]
                    d = temp[-3]
                    temp = d + ' ' + m + ' ' + y
                else:
                    dates = line.split('|')[-1]
                    if '-' in dates:
                        s = dates.split('-')
                    elif '–' in dates:
                        s = dates.split('–')
                    elif '−' in dates:
                        s = dates.split('−')
                    else:
                        s = dates.split('â€“')
                    temp = s[-1].strip()
                    temps = temp.strip().split()
                    if choice == 'Spain' and temps in [['?'], ['66.5']]:
                        rot += 2
                        continue
                    if choice == 'New York':
                        y = temps[-1]
                        d = temps[-2].strip(',')
                        if len(temps) == 3:
                            m = temps[-3][-3:]
                        else:
                            m = s[0].split()[0][s[0].find('|') + 1:]
                        temp = d + ' ' + m + ' ' + y
                    elif len(temps) == 2:
                        try:
                            y = int(temps[-1])
                            m = temps[0]
                            temp = str(date_kit.get_month_length(date_kit.get_month_number(m), y)) + ' ' + temp
                        except ValueError:
                            temp = temp + ' ' + year
                    elif len(temps) == 1:
                        temp = str(date_kit.get_month_length(date_kit.get_month_number(temps[0]), year)) + \
                               ' ' + temp + ' ' + year
                    temp = temp.strip("'")
                temp = temp.replace('X', '0')
                end_date = date_kit.Date(text=temp, form='dmy')
                end = date_kit.date_dif(today, end_date)
                if choice == "Italy":
                    if end_date.__repr__() == "2019-04-09":
                        key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'LeU', '+Eu', 'NcI', 'PaP']
                    elif end_date.__repr__() == "2019-09-19":
                        key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'LeU', '+Eu', 'EV', 'C!', 'A']
                    elif end_date.__repr__() == "2019-09-10":
                        key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'LeU', '+Eu', 'EV', 'C!']
                    elif end_date.__repr__() == "2019-08-12":
                        key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'LeU', '+Eu', 'EV']
                    elif 'https://www.youtrend.it/2021/05/25/draghi-cento-giorni/' in nline:
                        key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'LeU', '+Eu', 'EV', 'C!', 'A', 'IV']
                    elif 'https://www.termometropolitico.it/1595537_sondaggi-tp-un-italiano-su-due-non-vuole-draghi-' \
                         'al-quirinale.html' in nline:
                        key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'Art.1', 'SI', '+Eu', 'EV', 'A', 'IV']
            elif rot == 0 and choice == 'Canada':
                parts = line.split('||')
                temp = parts[date].split('|')[-1].strip().strip('}')
                end_date = date_kit.Date(text=temp, form='mdy')
                end = date_kit.date_dif(today, end_date)
                for n, p in enumerate(key):
                    if "''" in parts[start + n]:
                        share = float(parts[start + n].split('|')[-1].strip().strip("'"))
                    else:
                        num = parts[start + n].split('|')[-1].strip()
                        if num == '{{n/a}}' or num == '' or \
                                parts[start + n].split('|')[0].strip() == 'style="color:#F8F9FA;"':
                            if n <= 2:
                                for m in range(n):
                                    dat[key[m]][end].pop()
                                    if len(dat[key[m]][end]) == 0:
                                        del dat[key[m]][end]
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
                    key = ['LIB', 'CON', 'NDP', 'BQ', 'GRN', 'PPC']
                i += 1
                rot = None
                continue
            elif start <= rot < start + len(key):
                p = rot - start
                temp = line
                if '{{efn' in temp:
                    temp = temp[:temp.find('{{efn')]
                if choice in ['Spain', 'Portugal'] and '<br/>' in line:
                    temp = temp[:temp.find('<br/>')]
                elif choice == 'Ireland' and '<ref' in line:
                    temp = temp[:temp.find('<ref')]
                temp = temp.split('|')[-1].strip()
                if choice == 'Cyprus' and temp == '-' and p == 4:
                    i += 1
                    continue
                temp = temp.replace(',', '.')
                if temp in ['â€“', '-', ''] or "small" in temp:
                    share = None
                else:
                    try:
                        share = float(temp.strip().strip("'%"))
                    except ValueError:
                        share = None
                if key[p] not in dat:
                    dat[key[p]] = {}
                if end in dat[key[p]]:
                    if (choice == 'Slovakia' and len(dat[key[p]][end]) > 0 and p in (5, 10, 11, 12)) or \
                            (choice == 'Czechia' and len(dat[key[p]][end]) > 0 and p in (2, 3, 5, 10)) or \
                            (choice == 'Bulgaria' and len(dat[key[p]][end])) > 0 and p in (7, 8) or \
                            (flag and choice == 'Ireland' and len(dat[key[p]][end]) > 0 and p in (8, 9)):
                        if dat[key[p]][end][-1] is not None:
                            if share is not None:
                                dat[key[p]][end][-1] += share
                        else:
                            dat[key[p]][end][-1] = share
                    else:
                        dat[key[p]][end].append(share)
                else:
                    dat[key[p]][end] = [share]
                if choice in ['Slovakia', 'Italy', 'Hungary', 'Bulgaria']:
                    if 'colspan=' in line:
                        temp: str = line[line.find('colspan=') + len('colspan='):]
                        num = int(temp.strip('|').split()[0].split('|')[0].strip('" '))
                        rot += num - 1
            elif isrestart(line):
                rot = 0
            if choice == 'Czechia':
                if rot != 0:
                    if 'colspan=' in line:
                        temp: str = line[line.find('colspan=') + len('colspan='):]
                        num = int(temp.strip('|').split()[0].split('|')[0].strip('" '))
                        rot += num - 1
                    elif 'rowspan=' in line:
                        temp: str = line[line.find('rowspan=') + len('rowspan='):]
                        num = int(temp.strip('|').split()[0].split('|')[0].strip('" '))
                        rot += num - 1
            rot += 1
        i += 1
        prevline = line

    if include is not None:
        dat = {k: v for (k, v) in dat.items() if k in include}
    return dat


def choices_setup():
    choices = {
        'Austria': {
            'key': ['ÖVP', 'SPÖ', 'FPÖ', 'Gr\u00fcne', 'NEOS'],
            'col': {'ÖVP': (99, 195, 208), 'SPÖ': (206, 0, 12), 'FPÖ': (0, 86, 162), 'Gr\u00fcne': (136, 182, 38),
                    'NEOS': (232, 65, 136)},
            'gov': {'Government': ['ÖVP', 'Gr\u00fcne'], 'Opposition': ['SPÖ', 'FPÖ', 'NEOS']},
            'blocs': {'Progressive': ['SPÖ', 'Gr\u00fcne', 'NEOS'], 'Conservative': ['ÖVP', 'FPÖ']},
            'start': 4,
            'end_date': Date(2025, 1, 1),
            'restart': ['[http', 'election'],
            'toggle_seats': False
        },
        'Brazil': {
            'key': ['Bolsanaro (PSL/APB)', 'Lula (PT)', 'Haddad (PT)', 'Dino (PCdoB)', 'Gomes (PDT)', 'Boulos (PSOL)',
               'Doria (PSDB)', 'Amoedo (NOVO)', 'Silva (REDE)', 'Moro', 'Huck'],
            'include': ['Bolsanaro (PSL/APB)', 'Lula (PT)', 'Gomes (PDT)', 'Doria (PSDB)'],
            'col': {'Bolsanaro (PSL/APB)': (0, 140, 0), 'Lula (PT)': (204, 0, 0), 'Haddad (PT)': (204, 0, 0),
               'Dino (PCdoB)': (163, 0, 0), 'Gomes (PDT)': (238, 100, 100), 'Boulos (PSOL)': (163, 0, 0),
               'Doria (PSDB)': (0, 95, 164), 'Amoedo (NOVO)': (240, 118, 42), 'Silva (REDE)': (46, 139, 87),
               'Moro': dark_grey, 'Huck': grey},
            'start': 3,
            'vlines': {Date(2021, 3, 8): "Lula cleared of charges"},
            'end_date': Date(2022, 10, 2)
        },
        'Bulgaria': {
            'key': ['GERB', 'ITN', 'BSPzB', 'DPS', 'DB', 'ISMV', 'BP', 'BP', 'BP', 'Revival', 'BL', 'RB', 'LSChSR'],
            'col': {'GERB': (0, 86, 167), 'ITN': (75, 185, 222), 'BSPzB': (219, 15, 40), 'DPS': (0, 96, 170),
               'DB': (0, 74, 128), 'ISMV': (91, 165, 70), 'BP': black, 'Revival': (192, 159, 98),
               'BL': (243, 129, 20), 'RB': (43, 74, 153), 'LSChSR': (241, 25, 40)},
            'blocs': {'Conservative': ['GERB', 'RB'], 'Socialist': ['BSPzB', 'LSChSR'], 'DPS': ['DPS'],
                 'Nationalist': ['BP', 'Revival', 'BL'],
                 'Populist': ['ITN', 'DB', 'ISMV']},
            'start': 3,
            'end_date': Date(2021, 7, 11),
            'restart': ['[http', '2021 election']
        },
        'Canada': {
            'key': ['CON', 'LIB', 'NDP', 'BQ', 'GRN', 'PPC'],
            'col': {'CON': (100, 149, 237), 'LIB': (234, 109, 106), 'NDP': (244, 164, 96), 'BQ': (135, 206, 250),
               'GRN': (153, 201, 85), 'PPC': (131, 120, 158),
               'Government': (234, 109, 106), 'Opposition': (100, 149, 237)},
            'gov': {'Government': ['LIB'], 'Opposition': ['CON', 'NDP', 'BQ', 'GRN', 'PPC']},
            'blocs': {'Progressive': ['LIB', 'NDP', 'BQ', 'GRN'], 'Conservative': ['CON', 'PPC']},
            'start': 3,
            'vlines': {Date(2019, 10, 21): "General Election"},
            'end_date': Date(2023, 10, 16),
            'toggle_seats': True
        },
        'Cyprus': {
            'key': ['DISY', 'AKEL', 'DIKO', 'EDEK-SYPOL', 'KA', 'KOSP', 'ELAM', 'DIPA', 'Anex'],
            'col': {'DISY': (21, 105, 199), 'AKEL': (179, 27, 27), 'DIKO': (255, 126, 0), 'EDEK-SYPOL': (22, 79, 70),
               'KA': (0, 75, 145), 'KOSP': (127, 255, 0), 'ELAM': (0, 0, 0), 'DIPA': (255, 126, 0),
               'Anex': (68, 36, 100)},
            'date': 0,
            'start': 1,
            'end_date': Date(2021, 5, 30)
        },
        'Czechia': {
            'key': ['ANO', 'SPOLU', 'SPOLU', 'SPOLU', 'Pirati+STAN', 'Pirati+STAN', 'SPD', 'KSCM', 'CSSD', 'T-S',
                    'T-S', 'Z', 'P'],
            'col': {'ANO': (38, 16, 96), 'SPOLU': (35, 44, 119), 'Pirati+STAN': (0, 0, 0), 'SPD': (33, 117, 187),
                    'KSCM': (204, 0, 0), 'CSSD': (236, 88, 0), 'T-S': (0, 150, 130), 'Z': (96, 180, 76),
                    'P': (0, 51, 255),
                    'Government': (38, 16, 96), 'Opposition': (0, 0, 0)},
            'gov': {'Government': ['ANO', 'KSCM', 'CSSD'],
                    'Opposition': ['SPOLU', 'Pirati+STAN', 'SPD', 'T-S', 'Z', 'P']},
            'start': 26,
            'end_date': Date(2021, 10, 9)
        },
        'Denmark': {
            'key': ['A', 'V', 'O', 'B', 'F', '\u00d8', 'C', '\u00c5', 'D', 'I', 'P', 'K', 'E', 'G'],
            'col': {'A': (240, 77, 70), 'V': (0, 40, 131), 'O': (252, 208, 59), 'B': (229, 0, 125), 'F': (191, 3, 26),
               '\u00d8': (208, 0, 77), 'C': (0, 73, 49), '\u00c5': (0, 255, 0), 'D': (0, 80, 91),
               'I': (63, 178, 190),
               'P': (1, 152, 225), 'K': (255, 165, 0), 'E': (0, 66, 36), 'G': (128, 165, 26),
               'Red': (240, 77, 70), 'Blue': (0, 40, 131)},
            'blocs': {'Red': ['A', 'B', 'F', '\u00d8', '\u00c5', 'G'],
                      'Blue': ['V', 'O', 'C', 'D', 'I', 'P', 'K', 'E']},
            'start': 3,
            'restart': ['[http', 'election'],
            'end_date': Date(2023, 6, 4),
            'toggle_seats': True
        },
        'Finland': {
            'key': ['SDP', 'PS', 'KOK', 'KESK', 'VIHR', 'VAS', 'SFP', 'KD', 'LIIK'],
            'col': {'SDP': (245, 75, 75), 'PS': (255, 222, 85), 'KOK': (0, 98, 136), 'KESK': (52, 154, 43),
               'VIHR': (97, 191, 26), 'VAS': (240, 10, 100), 'SFP': (255, 221, 147), 'KD': (2, 53, 164),
               'LIIK': (180, 31, 121),
               'Government': (245, 75, 75), 'Opposition': (255, 222, 85)},
            'gov': {'Government': ['SDP', 'KESK', 'VIHR', 'VAS', 'SFP'], 'Opposition': ['KOK', 'PS', 'KD', 'LIIK']},
            'start': 3,
            'restart': ['http', 'election'],
            'end_date': Date(2023, 4, 30)
        },
        'Germany': {
            'key': ['CDU/CSU', 'SPD', 'AfD', 'FDP', 'Linke', 'Gr\u00fcne'],
            'col': {'CDU/CSU': (0, 0, 0), 'Gr\u00fcne': (100, 161, 45), 'SPD': (235, 0, 31), 'FDP': (255, 237, 0),
                    'AfD': (0, 158, 224), 'Linke': (190, 48, 117),
                    'Red-Red-Green': (190, 48, 117), 'Black-Yellow': (255, 237, 0), 'Jamaica': (118, 132, 15),
                    'Grand Coalition': (0, 0, 0), 'Traffic Light': (235, 0, 31), 'Black-Green': (100, 161, 45),
                    'Old Guard': (245, 118, 15)},
            'blocs': {'Red-Red-Green': ['Gr\u00fcne', 'SPD', 'Linke'],
                      'Black-Yellow': ['CDU/CSU', 'FDP'],
                      'Jamaica': ['CDU/CSU', 'FDP', 'Gr\u00fcne'],
                      'Traffic Light': ['SPD', 'Gr\u00fcne', 'FDP'],
                      'Grand Coalition': ['CDU/CSU', 'SPD'],
                      'Black-Green': ['CDU/CSU', 'Gr\u00fcne'],
                      'Old Guard': ['CDU/CSU', 'SPD', 'FDP']},
            'gov': {'Government': ['CDU/CSU', 'SPD'], 'Opposition': ['Gr\u00fcne', 'Linke', 'FDP', 'AfD']},
            'start': 4,
            'end_date': Date(2021, 9, 26),
            'restart': ['[http', 'election'],
            'toggle_seats': True
        },
        'Hungary': {
            'key': ['Fidesz', 'Jobbik', 'MSZP', 'Dialogue', 'DK', 'LMP', 'MM', 'MKKP', 'MHM'],
            'col': {'Fidesz': (255, 106, 0), 'Jobbik': (0, 131, 113), 'MSZP': (204, 0, 0), 'Dialogue': (60, 179, 77),
               'DK': (0, 103, 170), 'LMP': (54, 202, 139), 'MM': (142, 111, 206), 'MKKP': (128, 128, 128),
               'MHM': (86, 130, 3),
               'United Opposition': (32, 178, 170)},
            'blocs': {'Fidesz': ['Fidesz'], 'United Opposition': ['Jobbik', 'MSZP', 'Dialogue', 'DK', 'LMP', 'MM']},
            'date': 0,
            'start': 2,
            'end_date': Date(2022, 4, 8)
        },
        'Iceland': {
            'key': ['D', 'V', 'S', 'M', 'B', 'P', 'F', 'C', 'J'],
            'col': {'D': (0, 173, 239), 'V': (0, 184, 120), 'S': (234, 0, 56), 'M': (0, 33, 105), 'B': (160, 208, 103),
               'P': (137, 110, 189), 'F': (255, 202, 62), 'C': (255, 125, 20), 'J': (239, 72, 57),
               'Government': (0, 184, 120), 'Opposition': (234, 0, 56),
               'Socialist': (234, 0, 56), 'Liberal': (160, 208, 103), 'Conservative': (0, 173, 239)},
            'blocs': {'Socialist': ['V', 'S', 'J'], 'Liberal': ['B', 'M', 'C', 'P'], 'Conservative': ['D', 'F']},
            'gov': {'Government': ['V', 'B', 'D'], 'Opposition': ['S', 'M', 'P', 'F', 'C', 'J']},
            'start': 4,
            'restart': ['[http', 'election'],
            'end_date': Date(2021, 9, 25)
        },
        'Ireland': {
            'key': ['SF', 'FF', 'FG', 'GP', 'Lab', 'SD', 'PBP/S', 'Aon', 'O/I'],
            'col': {'SF': (50, 103, 96), 'FF': (102, 187, 102), 'FG': (102, 153, 255), 'GP': (34, 172, 111),
               'Lab': (204, 0, 0), 'SD': (117, 47, 139), 'PBP/S': (142, 36, 32), 'Aon': (68, 83, 42), 'O/I': grey},
            'blocs': {'Broad Left': ['SF', 'GP', 'Lab', 'SD', 'PBP/S'], 'Old Guard': ['FF', 'FG']},
            'gov': {'Government': ['FF', 'FG', 'GP'], 'Opposition': ['SF', 'Lab', 'SD', 'PBP/S', 'Aon', 'O/I']},
            'date': 0,
            'start': 2,
            'restart': ['Cite web', 'cite web', 'General election', 'cite news', 'Cite news'],
            'vlines': {Date(2020, 2, 8): 'General Election'},
            'end_date': Date(2025, 2, 20)
        },
        'Italy': {
            'key': ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'Art.1', 'SI', '+Eu', 'EV', 'A', 'IV', 'CI'],
            'col': {'M5S': (255, 235, 59), 'PD': (239, 28, 39), 'Lega': (0, 128, 0), 'FI': (0, 135, 220),
               'FdI': (3, 56, 106), 'LeU': (199, 40, 55), '+Eu': (255, 215, 0), 'EV': (115, 193, 112),
               'C!': (229, 131, 33), 'A': (0, 57, 170), 'IV': (214, 65, 140), 'NcI': (31, 107, 184),
               'PaP': (160, 20, 46), 'Art.1': (210, 27, 48), 'SI': (239, 62, 62), 'CI': (49, 39, 131),
               'Left': (239, 28, 39), 'Right': (0, 128, 0),
               'Government': (255, 235, 59), 'Opposition': (3, 56, 106)},
            'blocs': {'Left': ['PD', '+Eu', 'EV', 'LeU', 'IV', 'A', 'M5S', 'PaP', 'Art.1', 'SI'],
                 'Right': ['Lega', 'FI', 'FdI', 'C!', 'NcI', 'CI']},
            'gov': {'Government': ['M5S', 'Lega', 'PD', 'FI', 'LeU', 'IV', 'Art.1'],
               'Opposition': ['FdI', '+Eu', 'C!', 'A', 'SI', 'CI']},
            'date': 0,
            'start': 2,
            'end_date': Date(2023, 6, 1)
        },
        'New York': {
            'key': ['Eric Adams', 'Shaun Donovan', 'Kathryn Garcia', 'Raymond McGuire', 'Dianne Morales',
               'Scott Stringer', 'Maya Wiley', 'Andrew Yang'],
            'col': {'Eric Adams': (0, 0, 255), 'Shaun Donovan': (102, 0, 102), 'Kathryn Garcia': (255, 128, 0),
               'Raymond McGuire': (0, 102, 0), 'Dianne Morales': (255, 153, 255),
               'Scott Stringer': (120, 120, 255), 'Maya Wiley': red, 'Andrew Yang': yellow},
            'file_name': 'test_data/new_york_city_polling.txt',
            'start': 4,
            'end_date': Date(2021, 6, 22)
        },
        'Norway': {
            'key': ['R', 'SV', 'MDG', 'Ap', 'Sp', 'V', 'KrF', 'H', 'FrP'],
            'col': {'R': (231, 52, 69), 'SV': (188, 33, 73), 'MDG': (106, 147, 37), 'Ap': (227, 24, 54),
               'Sp': (0, 133, 66),
               'V': (17, 100, 104), 'KrF': (254, 193, 30), 'H': (135, 173, 215), 'FrP': (2, 76, 147),
               'Red-Green': (227, 24, 54), 'Blue': (135, 173, 215)},
            'blocs': {'Red-Green': ['R', 'SV', 'Ap', 'Sp'], 'Blue': ['V', 'KrF', 'H', 'FrP']},
            'start': 4,
            'restart': ['[http', 'election'],
            'end_date': Date(2021, 9, 13),
            'toggle_seats': True
        },
        'Peru': {
            'key': ['Castillo', 'Fujimori'],
            'col': {'Castillo': (192, 10, 10), 'Fujimori': (255, 128, 0)},
            'start': 3,
            'restart': ['http'],
            'end_date': Date(2021, 6, 6)
        },
        'Poland': {
            'key': ['United Right', 'Civic Coalition', 'The Left', 'Polish Coalition', 'Kukiz\'15', 'Confederation',
                    'Poland 2050'],
            'col': {'United Right': (38, 55, 120), 'Civic Coalition': (246, 143, 45), 'The Left': (172, 20, 90),
                    'Polish Coalition': (27, 177, 0), 'Kukiz\'15': (0, 0, 0), 'Confederation': (18, 39, 70),
                    'Poland 2050': (249, 192, 19),
                    'Government': (38, 55, 120), 'Opposition': (246, 143, 45),
                    'United Opposition': (246, 143, 45), 'Misc. Right': (18, 39, 70)},
            'gov': {'Government': ['United Right'],
                    'Opposition': ['Civic Coalition', 'The Left', 'Polish Coalition', 'Kukiz\'15', 'Confederation',
                                   'Poland 2050']},
            'blocs': {'United Right': ['United Right'],
                      'United Opposition': ['Civic Coalition', 'The Left', 'Polish Coalition', 'Poland 2050'],
                      'Misc. Right': ['Kukiz\'15', 'Confederation']},
            'start': 3,
            'restart': ['[http', 'election'],
            'end_date': Date(2023, 11, 11)
        },
        'Portugal': {
            'key': ['PS', 'PSD', 'BE', 'CDU', 'CDS-PP', 'PAN', 'Chega', 'IL', 'LIVRE'],
            'col': {'PS': (255, 102, 255), 'PSD': (255, 153, 0), 'BE': (139, 0, 0), 'CDU': (255, 0, 0),
               'CDS-PP': (0, 147, 221),
               'PAN': (0, 128, 128), 'Chega': (32, 32, 86), 'IL': (0, 173, 239), 'LIVRE': (143, 188, 143),
               'Left': (255, 102, 255), 'Right': (255, 153, 0)},
            'blocs': {'Left': ['PS', 'BE', 'CDU', 'PAN', 'LIVRE'], 'Right': ['PSD', 'CDS-PP', 'Chega', 'IL']},
            'start': 4,
            'restart': ['[http', 'election'],
            'end_date': Date(2023, 10, 8)
        },
        'Slovakia': {
            'key': [
                'OL\'aNO', 'SMER-SD', 'SR', 'L\'SNS', 'PS-SPOLU', 'PS-SPOLU', 'SaS', 'ZL\'', 'KDH',
                'Magyar', 'Magyar', 'Magyar', 'Magyar', 'SNS', 'DV', 'HLAS-SD', 'REP'],
            'col': {'OL\'aNO': (190, 214, 47), 'SMER-SD': (217, 39, 39), 'SR': (11, 76, 159), 'L\'SNS': (11, 87, 16),
                    'PS-SPOLU': (0, 188, 255), 'SaS': (166, 206, 58), 'ZL\'': (255, 187, 0), 'KDH': (253, 209, 88),
                    'Magyar': (39, 93, 51), 'SNS': (37, 58, 121), 'DV': (255, 0, 43), 'HLAS-SD': (180, 40, 70),
                    'REP': (220, 1, 22),
                    'Government': (190, 214, 47), 'Opposition': (180, 40, 70),
                    'Left': (180, 40, 70), 'Right': (190, 214, 47)},
            'gov': {'Government': ['OL\'aNO', 'SR', 'SaS', 'ZL\''],
                    'Opposition': ['SMER-SD', 'L\'SNS', 'PS-SPOLU', 'KDH', 'Magyar', 'SNS', 'DV', 'HLAS-SD', 'REP']},
            'blocs': {'Left': ['SMER-SD', 'PS-SPOLU', 'DV', 'HLAS-SD'],
                      'Right': ['OL\'aNO', 'SR', 'L\'SNS', 'SaS', 'ZL\'', 'KDH', 'Magyar', 'SNS', 'REP']},
            'date': 0,
            'start': 2,
            'restart': ['Focus', 'AKO', '2020 elections'],
            'end_date': Date(2024, 2, 24)
        },
        'Spain': {
            'key': ['PSOE', 'PP', 'VOX', 'UP', 'Cs', 'ERC', 'MP', 'JxCat', 'PNV', 'EHB', 'CUP', 'CC', 'BNG', 'NA+',
                    'PRC'],
            'col': {'PSOE': (239, 28, 39), 'PP': (29, 132, 206), 'VOX': (99, 190, 33), 'UP': (123, 73, 119),
                    'Cs': (235, 97, 9), 'ERC': (255, 178, 50), 'MP': (15, 222, 196), 'JxCat': (0, 199, 174),
                    'PNV': (74, 174, 74), 'EHB': (181, 207, 24), 'CUP': (255, 237, 0), 'CC': (255, 215, 0),
                    'BNG': (173, 207, 239), 'NA+': (129, 157, 163), 'PRC': (194, 206, 12),
                    'Government': (239, 28, 39), 'Opposition': (29, 132, 206),
                    'Left': (239, 28, 39), 'Right': (29, 132, 206), 'Regionalist': (255, 178, 50)},
            'gov': {'Government': ['PSOE', 'UP', 'PNV', 'MP', 'BNG'],
                    'Opposition': ['PP', 'VOX', 'Cs', 'JxCat', 'CUP', 'CC', 'PRC']},
            'blocs': {'Left': ['PSOE', 'UP', 'MP'], 'Right': ['PP', 'VOX', 'Cs'],
                      'Regionalist': ['ERC', 'JxCat', 'PNV', 'EHB', 'CUP', 'CC', 'BNG', 'NA+', 'PRC']},
            'restart': ['http', 'Spanish general election'],
            'start': 4,
            'end_date': Date(2023, 12, 10),
            'vlines': {Date(2021, 5, 4): 'Madrilenian', Date(2021, 2, 14): 'Catalan'}
        },
        'Sweden': {
            'key': ['V', 'S', 'MP', 'C', 'L', 'M', 'KD', 'SD'],
            'col': {'V': (176, 0, 0), 'S': (237, 27, 52), 'MP': (43, 145, 44), 'C': (1, 106, 57), 'L': (0, 106, 179),
               'M': (1, 156, 219), 'KD': (0, 70, 120), 'SD': (254, 223, 9),
               'Red-Green': (237, 27, 52), 'Alliance': (245, 137, 28),
               'Government': (237, 27, 52), 'Opposition': (245, 137, 28)},
            'blocs': {'Red-Green': ['S', 'V', 'MP'], 'Alliance': ['C', 'L', 'M', 'KD'], 'Right': ['M', 'L', 'KD', 'SD'],
                 'Left': ['C', 'S', 'V', 'MP']},
            'gov': {'Government': ['S', 'MP', 'V', 'C', 'L'], 'Opposition': ['M', 'KD', 'SD']},
            'start': 3,
            'restart': ['http', '2018 election'],
            'end_date': Date(2022, 9, 11),
            'toggle_seats': True
        },
        'UK': {
            'key': ['Conservative', 'Labour', 'Lib Dem', 'SNP', 'Green'],
            'col': {'Conservative': (0, 135, 220), 'Labour': (228, 0, 59), 'Lib Dem': (250, 166, 26),
               'SNP': (253, 243, 142), 'Green': (106, 176, 35)},
            'date': 2,
            'start': 5,
            'vlines': {Date(2020, 4, 4): 'Starmer becomes Labour leader',
                  Date(2021, 5, 6): 'Local elections'},
            'restart': ['[http', '2019 general election'],
            'end_date': Date(2024, 5, 2)
        }
    }
    for c, d in choices.items():
        if 'restart' not in d:
            d['restart'] = ['[http']
        if 'date' not in d:
            d['date'] = 1
        if 'end_date' not in d:
            d['end_date'] = None
        if 'blocs' not in d:
            d['blocs'] = None
        elif d['blocs'] is not None:
            for line in d['blocs'].keys():
                if line not in d['col'].keys():
                    d['col'][line] = d['col'][d['blocs'][line][0]]
        if 'gov' not in d:
            d['gov'] = None
        elif d['gov'] is not None:
            for line in d['gov'].keys():
                if line not in d['col'].keys():
                    d['col'][line] = d['col'][d['gov'][line][0]]
        if 'file_name' not in d:
            d['file_name'] = 'test_data/' + c.lower() + '_polling.txt'
        if 'include' not in d:
            d['include'] = None
        if 'vlines' not in d:
            d['vlines'] = None
        elif d['vlines'] is not None:
            d['vlines'] = {date_kit.date_dif(today, k): v for k, v in d['vlines'].items()}
        if 'toggle_seats' not in d:
            d['toggle_seats'] = False
    return choices


def choice_setting(c):
    dat = choices[c]
    file_name = dat['file_name']
    key = dat['key']
    col = dat['col']
    blocs = dat['blocs']
    gov = dat['gov']
    start = dat['start']
    restart = dat['restart']
    date = dat['date']
    end_date = dat['end_date']
    include = dat['include']
    vlines = dat['vlines']
    toggle_seats = dat['toggle_seats']
    return file_name, key, col, blocs, gov, start, restart, date, end_date, include, vlines, toggle_seats


def filter_nils(dat, view):
    if dat is not None:
        for line, vals in dat.items():
            for x, ys in vals.items():
                dat[line][x] = list(filter(lambda x: x is not None and (x != 0 or view == 'parties'), ys))
    return dat


class GraphPage:
    spread = 60
    high_res = 5 / 2
    low_res = 21

    def __init__(self, choice, view='parties', metric='percentage', to_end_date=False):
        widgets.clear()

        self.graph = None
        self.choice = choice
        self.view = view
        self.metric = metric
        self.minx = -1
        self.spread = GraphPage.spread
        self.file_name, self.key, self.col, self.blocs, self.gov, self.start, self.restart, self.date, \
            self.end_date, self.include, self.vlines, toggle_seats = choice_setting(self.choice)

        self.to_end_date = to_end_date

        self.dat = None
        self.blocs_dat = None
        self.gov_dat = None
        self.seats_dat = None
        self.seats_blocs_dat = None
        self.seats_gov_dat = None

        self.graph_dat = None
        self.graph_blocs_dat = None
        self.graph_gov_dat = None
        self.seats_graph_dat = None
        self.seats_graph_blocs_dat = None
        self.seats_graph_gov_dat = None

        height = screen_height / 12
        unit_size = height * 2 / 3
        back_button = Button((3 / 2 * unit_size, height * 2 / 3), (unit_size, unit_size), align=CENTER)
        back_button.callback(menu_page.show)
        img = Image(back_button.rect.center,
                    (back_button.rect.width * 3 / 4, back_button.rect.height * 3 / 4),
                    "images/arrow.png")
        img.surface = pygame.transform.rotate(img.surface, 270)
        back_button.set_tooltip("Return to Menu")
        back_button.components.append(img)
        back_button.show()

        pinboard = types.SimpleNamespace()
        pinboard.select_buttons = []

        bloc_button = SelectButton((screen_width - 3 / 2 * unit_size, height * 2 / 3),
                                   (unit_size, unit_size),
                                   align=CENTER, parent=pinboard, deselectable=False)
        pinboard.select_buttons.append(bloc_button)
        bloc_img = Image(bloc_button.rect.center, (bloc_button.rect.w * 4 / 5, bloc_button.rect.h * 4 / 5),
                         img_path='images/hierarchy.png')
        bloc_button.components.append(bloc_img)
        bloc_button.set_tooltip('Blocs')
        bloc_button.callback(functools.partial(self.change_view, 'blocs'))
        if self.blocs is None:
            bloc_button.disable()
        bloc_button.show()

        gov_button = SelectButton((screen_width - 3 * unit_size, height * 2 / 3),
                                  (unit_size, unit_size),
                                  align=CENTER, parent=pinboard, deselectable=False)
        gov_img = Image(gov_button.rect.center, (gov_button.rect.w * 4/5, gov_button.rect.h * 4/5),
                        img_path='images/parliament.png')
        gov_button.components.append(gov_img)
        gov_button.set_tooltip('Government/Opposition')
        pinboard.select_buttons.append(gov_button)
        gov_button.callback(functools.partial(self.change_view, 'gov'))
        if self.gov is None:
            gov_button.disable()
        gov_button.show()

        party_button = SelectButton((screen_width - 9 / 2 * unit_size, height * 2 / 3),
                                    (unit_size, unit_size),
                                    align=CENTER, parent=pinboard, deselectable=False)
        pinboard.select_buttons.append(party_button)
        party_img = Image(party_button.rect.center, (party_button.rect.w * 4 / 5, party_button.rect.h * 4 / 5),
                          img_path='images/ballot.png')
        party_button.components.append(party_img)
        party_button.set_tooltip('Parties')
        party_button.callback(functools.partial(self.change_view, 'parties'))
        party_button.select()
        party_button.show()

        seats_button = SelectButton((screen_width - 12 / 2 * unit_size, height * 2 / 3),
                                    (unit_size, unit_size), align=CENTER, deselectable=True)
        seats_button.callback(functools.partial(self.change_metric, 'seats'))
        seats_button.release_callback(functools.partial(self.change_metric, 'percentage'))
        seats_button.set_tooltip('Toggle estimated seat/vote distribution')
        seats_img = Image(seats_button.rect.center, (seats_button.rect.w * 4 / 5, seats_button.rect.h * 4 / 5),
                          img_path='images/cabinet.png')
        seats_button.components.append(seats_img)
        if not toggle_seats:
            seats_button.disable()
        seats_button.show()

        end_button = SelectButton((screen_width - 15 / 2 * unit_size, height * 2 / 3),
                                  (unit_size, unit_size), align=CENTER, deselectable=True)
        end_button.callback(functools.partial(self.change_toend, True))
        end_button.release_callback(functools.partial(self.change_toend, False))
        end_button.set_tooltip('Show up to next election')
        end_img = Image(end_button.rect.center, (end_button.rect.w * 4 / 5, end_button.rect.h * 4 / 5),
                        img_path='images/next.png')
        end_button.components.append(end_img)
        if self.end_date is None:
            end_button.disable()
        else:
            end_button.select()
        end_button.show()

        self.spread_txt = Text(str(self.spread), (back_button.rect.centerx, back_button.rect.bottom + 8), align=TOP)
        self.spread_txt.show()

        area = (self.spread_txt.rect.h, self.spread_txt.rect.h)
        self.up_spread = Button((self.spread_txt.rect.right + area[0] / 2, self.spread_txt.rect.centery), area,
                                align=LEFT)
        self.up_spread.callback(self.change_spread, returns=True)
        img = Image(self.up_spread.rect.center,
                    (self.up_spread.rect.width * 3 / 4, self.up_spread.rect.height * 3 / 4),
                    "images/arrow.png")
        img.surface = pygame.transform.rotate(img.surface, 90)
        self.up_spread.components.append(img)
        self.up_spread.show()

        self.down_spread = Button((self.spread_txt.rect.left - area[0] / 2, self.spread_txt.rect.centery), area,
                                  align=RIGHT)
        self.down_spread.callback(self.change_spread, returns=True)
        img = Image(self.down_spread.rect.center,
                    (self.down_spread.rect.width * 3 / 4, self.down_spread.rect.height * 3 / 4),
                    "images/arrow.png")
        img.surface = pygame.transform.rotate(img.surface, 270)
        self.down_spread.components.append(img)
        self.down_spread.show()

        pinboard2 = types.SimpleNamespace()
        pinboard2.select_buttons = []
        timescales = [1, 2, 5, 10, -1]
        for i, s in enumerate(timescales):
            b = SelectButton((screen_width - (9 + 3/2 * i) * unit_size, height * 2 / 3),
                             (unit_size, unit_size), label='MAX' if s == -1 else str(s),
                             align=CENTER, parent=pinboard2, deselectable=False, exclusive=True)
            b.callback(functools.partial(self.change_minx, s))
            if s == -1:
                b.select()
            b.show()
            pinboard2.select_buttons.append(b)

        self.change_view(view='parties')

    def init_dat(self):
        with open(self.file_name, 'r', encoding='utf-8') as f:
            content = f.readlines()
        if self.choice in olddata:
            with open(olddata[self.choice], 'r', encoding='utf-8') as f:
                content.extend(f.readlines())
        return read_data(content, self.key, self.start, self.restart, self.date, self.choice, self.include)

    def init_seats_dat(self):
        xs = set()
        for party in self.dat:
            xs.update(set(self.dat[party].keys()))
        if self.choice == 'Canada':
            total_share, all_shares, rel_votes = process_riding_data(get_riding_data())
            seats_dat = {p: {} for p in total_share.keys()}
            for x in xs:
                n = max([len(self.dat[p][x]) if x in self.dat[p] else 0 for p in self.dat])
                for p in total_share:
                    if p == 'IND' or not x < min(self.dat[p]):
                        seats_dat[p][x] = [0 for _ in range(n)]
                for ridata in all_shares.values():
                    for i in range(n):
                        ridat = {}
                        for p in ridata:
                            if p in self.dat and x in self.dat[p] and len(self.dat[p][x]) > i:
                                k = ridata[p] + (self.dat[p][x][i] / 100 - total_share[p]) / rel_votes[p]
                            elif x not in seats_dat[p]:
                                continue
                            else:
                                k = ridata[p]
                            ridat[k] = p
                        p = ridat[max(ridat)]
                        seats_dat[p][x][i] += 1
        elif self.choice in ['Sweden', 'Norway', 'Denmark', 'Germany']:
            seats_dat = {p: {} for p in self.dat}
            for x in xs:
                n = max([len(self.dat[p][x]) if x in self.dat[p] else 0 for p in self.dat])
                for p in self.dat:
                    if len(self.dat[p][x]) > 0:
                        seats_dat[p][x] = [0 for _ in range(n)]
                for i in range(n):
                    shares = {}
                    if self.choice == 'Sweden':
                        seats = 349
                        divisor = 2
                        bar = 0.2
                        threshold = 4
                    elif self.choice == 'Denmark':
                        seats = 175
                        divisor = 2
                        bar = 0
                        threshold = 2
                    elif self.choice == 'Germany':
                        seats = 598
                        divisor = 2
                        bar = 0
                        threshold = 5
                    else:
                        seats = 169
                        divisor = 2
                        bar = 0.4
                        threshold = 4
                    for p in self.dat:
                        if p in self.dat and x in self.dat[p] and len(self.dat[p][x]) > i and \
                                self.dat[p][x][i] >= threshold:
                            shares[p] = self.dat[p][x][i]
                        elif x not in seats_dat[p]:
                            continue
                        else:
                            shares[p] = 0
                    seatdist = highest_quotient_method(shares, seats, divisor, bar)
                    for p in seatdist:
                        if x in seats_dat[p]:
                            seats_dat[p][x][i] = seatdist[p]
        else:
            seats_dat = None
        return seats_dat

    @staticmethod
    def dat_ymax(dat):
        try:
            ymax = max([max([max(ys) if len(ys) > 0 else 0 for ys in line.values() if line is not None])
                        for line in dat.values()])
            return ymax * 5 / 4
        except AttributeError:
            return False

    def improve_res(self, resratio):
        if self.metric == 'seats':
            if self.view == 'blocs':
                self.seats_graph_blocs_dat = self.init_graph_data(self.seats_blocs_dat, resratio=resratio)
            elif self.view == 'gov':
                self.seats_graph_gov_dat = self.init_graph_data(self.seats_gov_dat, resratio=resratio)
            else:
                self.seats_graph_dat = self.init_graph_data(self.seats_dat, resratio=resratio)
        else:
            if self.view == 'blocs':
                self.graph_blocs_dat = self.init_graph_data(self.blocs_dat, resratio=resratio)
            elif self.view == 'gov':
                self.graph_gov_dat = self.init_graph_data(self.gov_dat, resratio=resratio)
            else:
                self.graph_dat = self.init_graph_data(self.dat, resratio=resratio)
        self.make_graph()

    def init_group(self, view, idat):
        if view == 'blocs':
            if self.blocs is None:
                return None
            else:
                relev = self.blocs
        else:
            if self.gov is None:
                return None
            else:
                relev = self.gov
        dat = {}
        for b, ps in relev.items():
            dat[b] = {}
            for p in ps:
                for x, ys in idat[p].items():
                    if x in dat[b].keys():
                        for i, y in enumerate(ys):
                            if y is None:
                                count = 0
                            else:
                                count = y
                            dat[b][x][i] += count
                    else:
                        dat[b][x] = list(map(lambda y: 0 if y is None else y, ys))
        return dat

    def init_graph_data(self, dat, resratio=7):
        if dat is not None:
            start = min([min(d) for d in dat.values()])
            end = date_kit.date_dif(today, self.end_date)
            limit = 0
            dat = weighted_averages(dat, self.spread, loc=True, resratio=resratio, start=start, end=end, limit=limit)
        return dat

    def make_graph(self):
        if self.to_end_date and self.end_date is not None:
            x_max = date_kit.date_dif(today, self.end_date)
        else:
            x_max = None
        if self.minx == -1:
            x_min = None
        else:
            if x_max is not None:
                end_date = self.end_date
            else:
                end_date = today
            x_min = -date_kit.date_dif(Date(end_date.year - self.minx, end_date.month, end_date.day), today)
        title = "Opinion Polling for " + self.choice

        if self.metric == 'seats':
            if self.view == 'blocs':
                dat = self.seats_graph_blocs_dat
                points = self.seats_blocs_dat
            elif self.view == 'gov':
                dat = self.seats_graph_gov_dat
                points = self.seats_gov_dat
            else:
                dat = self.seats_graph_dat
                points = self.seats_dat
            y_title = "Number of Seats"
            intg = True
        else:
            if self.view == 'blocs':
                dat = self.graph_blocs_dat
                points = self.blocs_dat
            elif self.view == 'gov':
                dat = self.graph_gov_dat
                points = self.gov_dat
            else:
                dat = self.graph_dat
                points = self.dat
            y_title = "Support (%)"
            intg = False
        y_max = self.dat_ymax(points)
        if y_max is not False:
            graph = GraphDisplay(screen_center, (screen_width, screen_height), dat, x_title=None,
                                 y_title=y_title, title=title, step=1, align=CENTER, colours=self.col,
                                 initial_date=today, leader=True, y_min=0, y_max=y_max, x_max=x_max, x_min=x_min,
                                 dat_points=points, vlines=self.vlines, intg=intg)
            with lock:
                if self.graph is not None:
                    self.graph.hide()
                self.graph = graph
                self.graph.catch(pygame.mouse.get_pos())
                self.graph.show()

    def change_view_or_metric(self):
        if self.dat is None:
            self.dat = filter_nils(self.init_dat(), 'parties')
        if self.metric == 'seats':
            if self.seats_dat is None:
                self.seats_dat = self.init_seats_dat()
            if self.view == 'blocs' and self.seats_graph_blocs_dat is None:
                if self.seats_blocs_dat is None:
                    self.seats_blocs_dat = filter_nils(self.init_group(self.view, self.seats_dat), self.view)
                self.seats_graph_blocs_dat = self.init_graph_data(self.seats_blocs_dat, resratio=self.low_res)
            elif self.view == 'gov' and self.seats_graph_gov_dat is None:
                if self.seats_gov_dat is None:
                    self.seats_gov_dat = filter_nils(self.init_group(self.view, self.seats_dat), self.view)
                self.seats_graph_gov_dat = self.init_graph_data(self.seats_gov_dat, resratio=self.low_res)
            elif self.view == 'parties' and self.seats_graph_dat is None:
                self.seats_graph_dat = self.init_graph_data(self.seats_dat, resratio=self.low_res)
        else:
            if self.view == 'blocs' and self.graph_blocs_dat is None:
                if self.blocs_dat is None:
                    self.blocs_dat = filter_nils(self.init_group(self.view, self.dat), self.view)
                self.graph_blocs_dat = self.init_graph_data(self.blocs_dat, resratio=self.low_res)
            elif self.view == 'gov' and self.graph_gov_dat is None:
                if self.gov_dat is None:
                    self.gov_dat = filter_nils(self.init_group(self.view, self.dat), self.view)
                self.graph_gov_dat = self.init_graph_data(self.gov_dat, resratio=self.low_res)
            elif self.view == 'parties' and self.graph_dat is None:
                self.graph_dat = self.init_graph_data(self.dat, resratio=self.low_res)
        self.make_graph()
        thread = threading.Thread(target=self.improve_res, args=(self.high_res,))
        thread.start()

    def change_view(self, view):
        self.view = view
        self.change_view_or_metric()

    def change_metric(self, metric):
        self.metric = metric
        self.change_view_or_metric()

    def change_spread(self, button):
        if button == self.up_spread:
            self.down_spread.enable()
            self.spread += 10
            if self.spread >= 360:
                self.spread = 360
                self.up_spread.disable()
        elif button == self.down_spread:
            self.up_spread.enable()
            self.spread -= 10
            if self.spread <= 10:
                self.spread = 10
                self.down_spread.disable()
        self.spread_txt.update(str(self.spread))
        self.graph_dat = None
        self.graph_blocs_dat = None
        self.graph_gov_dat = None
        self.seats_graph_dat = None
        self.seats_gov_dat = None
        self.seats_blocs_dat = None
        self.change_view_or_metric()

    def change_minx(self, minx):
        self.minx = minx
        self.make_graph()

    def change_toend(self, toend):
        self.to_end_date = toend
        self.make_graph()


class MenuPage:

    def __init__(self):
        button_size = 64
        self.display = ScrollButtonDisplay(screen_center, (300, screen_height * 4 / 5), button_size * len(options),
                                           CENTER, button_size=button_size)
        buttons = []
        for i, entry in enumerate(options):
            b = Button((self.display.contain_rect.left, self.display.contain_rect.top + i * button_size),
                       (self.display.contain_rect.w, button_size), parent=self.display)
            b.callback(functools.partial(GraphPage, entry, to_end_date=True))
            img_path = 'images/flags/' + entry.lower() + '.png'
            try:
                img = Image((b.rect.centerx + b.rect.w / 8, b.rect.centery), (b.rect.h * 3 / 4, b.rect.h * 3 / 4),
                            img_path, align=LEFT)
                b.components.append(img)
            except FileNotFoundError:
                pass
            label = Text(entry.upper(), (b.rect.centerx + b.rect.w / 16, b.rect.centery), 24, align=RIGHT,
                         background_colour=self.display.colour)
            b.components.append(label)
            buttons.append(b)
        self.display.add_select_buttons(buttons)

        self.update_b = Button((screen_rect.centerx / 2, screen_rect.centery), align=CENTER, label='Update Data')
        self.update_b.callback(update_data)

        self.show()

    def show(self):
        widgets.clear()
        self.display.show()
        self.update_b.show()


def update_data(sel="All"):
    def update_dat(dest, url, tag):
        content = urllib.request.urlopen(url)
        read_content = content.read()
        soup = BeautifulSoup(read_content, 'html.parser')
        content = soup.find_all('textarea')
        if tag == 'New York':
            text = content[0].text
            text = text[text.find('=== First-past-the-post polls ==='):
                        text.find('!scope="row"| [https://www.filesforprogress.org/datasets/2020/1/'
                                  'dfp_poll_january_ny.pdf Data for Progress (D)]')]
        else:
            text = content[0].text
        final = text.encode('utf-8')
        with open(dest, 'wb') as f:
            f.write(final)

    urls = {
        'Austria':  'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_next_Austrian_legislative_election&action=edit&section=3',
        'Brazil':   'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_2022_Brazilian_general_election&action=edit&section=3',
        'Bulgaria': 'https://en.wikipedia.org/w/index.php?title='
                    'July_2021_Bulgarian_parliamentary_election&action=edit&section=4',
        'Canada':   'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_44th_Canadian_federal_election&action=edit&section=1',
        'Czechia':  'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_2021_Czech_legislative_election&action=edit&section=3',
        'Denmark':  'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_next_Danish_general_election&action=edit&section=3',
        'Germany':  'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_2021_German_federal_election&action=edit&section=3',
        'Hungary':  'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_2022_Hungarian_parliamentary_election&action=edit&section=4',
        'Iceland':  'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_next_Icelandic_parliamentary_election&action=edit&section=2',
        'Ireland':  'https://en.wikipedia.org/w/index.php?title=Next_Irish_general_election&action=edit&section=3',
        'Italy':    'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_next_Italian_general_election&action=edit&section=3',
        'Norway':   'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_2021_Norwegian_parliamentary_election&action=edit&section=3',
        'Poland':   'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_next_Polish_parliamentary_election&action=edit&section=3',
        'Portugal': 'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_next_Portuguese_legislative_election&action=edit&section=3',
        'Slovakia': 'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_next_Slovak_parliamentary_election&action=edit&section=1',
        'Spain':    'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_next_Spanish_general_election&action=edit&section=4',
        'Sweden':   'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_2022_Swedish_general_election&action=edit&section=4',
        'UK':       'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_next_United_Kingdom_general_election&action=edit&section=3'
    }
    files = {
        'New York': 'test_data/new_york_city_polling.txt'
    }
    if sel == 'All':
        for tag, url in urls.items():
            if tag in files:
                dest = files[tag]
            else:
                dest = 'test_data/' + tag.lower() + '_polling.txt'
            thread = threading.Thread(target=update_dat, args=(dest, url, tag))
            thread.start()


def process_riding_data(dat):
    tags = ['LIB', 'CON', 'NDP', 'BQ', 'GRN', 'PPC', 'IND']
    total_votes = {p: 0 for p in tags}
    rel_votes = total_votes.copy()
    all_shares = {}
    for region in dat:
        for riding in dat[region]:
            totloc = 0
            for party in total_votes:
                v = riding[party]
                total_votes[party] += v
                totloc += v
            all_shares[riding['name']] = {p: riding[p] / totloc for p in total_votes}
            for party in rel_votes:
                if riding[party] > 0:
                    rel_votes[party] += totloc
    tot = sum(total_votes.values())
    rel_votes = {p: rel_votes[p] / tot for p in rel_votes}
    total_share = {p: total_votes[p] / tot for p in total_votes}
    return total_share, all_shares, rel_votes


if __name__ == '__main__':
    choices = choices_setup()
    lock = threading.Lock()
    menu_page = MenuPage()
    game_loop(lock)
