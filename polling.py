from ui import *
from toolkit import *
import date_kit
import types
import urllib.request
from bs4 import BeautifulSoup

today = Date(2021, 6, 18)


def read_data(content, key, start, restart, date, choice):
    dat: Dict[str, Dict[int, List[float]]] = {}
    rot = None
    end = 0
    year = '2021'
    i = 0
    prevline = None
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
        if sum(map(lambda r: r in line, restart)):
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
                    if 'Oct–Jan' in line:
                        rot = None
                        i += 1
                        continue
                    elif 'rowspan="2"' not in line:
                        rot += 23
                        i += 1
                    if 'rowspan="2"' in prevline:
                        rot += 1
                elif choice in ["Italy", "Cyprus", 'Slovakia']:
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
                line = line.strip().strip('}')
                dates = line.split('|')[-1]
                if '-' in dates:
                    s = dates.split('-')
                elif '–' in dates:
                    s = dates.split('–')
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
                        m = s[0].split()[0][-3:]
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
                    elif 'https://www.youtrend.it/2021/05/25/draghi-cento-giorni/' in nline:
                        key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'LeU', '+Eu', 'EV', 'C!', 'A', 'IV']
                    elif 'https://www.termometropolitico.it/1595537_sondaggi-tp-un-italiano-su-due-non-vuole-draghi-' \
                         'al-quirinale.html' in nline:
                        key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'Art.1', 'SI', '+Eu', 'EV', 'A', 'IV']
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
                    key = ['LIB', 'CON', 'NDP', 'BQ', 'GPC', 'PPC']
                i += 1
                rot = None
                continue
            elif start <= rot < start + len(key):
                p = rot - start
                temp = line
                if '{{efn' in temp:
                    temp = temp[:temp.find('{{efn')]
                if choice == 'Spain' and '<br/>' in line:
                    temp = temp[:temp.find('<br/>')]
                temp = temp.split('|')[-1].strip()
                if choice == 'Cyprus' and temp == '-' and p == 4:
                    i += 1
                    continue
                temp = temp.replace(',', '.')
                if temp == 'â€“' or temp == '-' or temp == '' or "small" in temp:
                    share = None
                else:
                    try:
                        share = float(temp.strip().strip("'").strip('%'))
                    except ValueError:
                        share = None
                # print(key[rot], share)
                if key[p] not in dat:
                    dat[key[p]] = {}
                if end in dat[key[p]]:
                    if choice == 'Slovakia' and len(dat[key[p]][end]) > 0 and (p == 5 or p in range(10, 13)):
                        if dat[key[p]][end][-1] is not None:
                            if share is not None:
                                dat[key[p]][end][-1] += share
                        else:
                            dat[key[p]][end][-1] = share
                    else:
                        dat[key[p]][end].append(share)
                else:
                    dat[key[p]][end] = [share]
                if choice in ['Slovakia', 'Italy']:
                    if 'colspan=' in line:
                        temp: str = line[line.find('colspan=') + len('colspan='):]
                        num = int(temp.strip('|').split()[0].split('|')[0].strip('" '))
                        rot += num - 1
            elif sum(map(lambda r: r in line, restart)):
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
    return dat


class GraphPage:
    spread = 60

    def __init__(self, choice, view='parties', to_end_date=False):
        widgets.clear()

        self.graph = None
        self.choice = choice
        self.view = view
        self.spread = GraphPage.spread
        self.file_name, self.key, self.col, self.blocs, self.gov, self.start, self.restart, self.date, \
            self.end_date = self.choice_setting(self.choice)

        self.to_end_date = to_end_date

        with open(self.file_name, 'r', encoding='utf-8') as f:
            content = f.readlines()

        self.dat = read_data(content, self.key, self.start, self.restart, self.date, self.choice)
        # print(self.dat)

        height = screen_height / 12
        unit_size = height * 2 / 3
        back_button = Button((3 / 2 * unit_size, height * 2 / 3), (unit_size, unit_size), align=CENTER)
        back_button.callback(menu_page)
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

        self.spread_txt = Text(str(self.spread), (screen_rect.centerx, height * 2 / 3))
        self.spread_txt.show()

        area = (self.spread_txt.rect.h, self.spread_txt.rect.h)
        self.up_spread = Button((self.spread_txt.rect.right + area[0] / 2, height * 2 / 3), area, align=LEFT)
        self.up_spread.callback(self.change_spread, returns=True)
        img = Image(self.up_spread.rect.center,
                    (self.up_spread.rect.width * 3 / 4, self.up_spread.rect.height * 3 / 4),
                    "images/arrow.png")
        img.surface = pygame.transform.rotate(img.surface, 90)
        self.up_spread.components.append(img)
        self.up_spread.show()

        self.down_spread = Button((self.spread_txt.rect.left - area[0] / 2, height * 2 / 3), area, align=RIGHT)
        self.down_spread.callback(self.change_spread, returns=True)
        img = Image(self.down_spread.rect.center,
                    (self.down_spread.rect.width * 3 / 4, self.down_spread.rect.height * 3 / 4),
                    "images/arrow.png")
        img.surface = pygame.transform.rotate(img.surface, 270)
        self.down_spread.components.append(img)
        self.down_spread.show()

        self.make_graph()

    @staticmethod
    def choice_setting(choice):
        restart = ['[http']
        date = 1
        end_date = None
        blocs = None
        gov = None
        if choice == 'Germany':
            key = ['CDU/CSU', 'SPD', 'AfD', 'FDP', 'Linke', 'Gr\u00fcne']
            col = {'CDU/CSU': (0, 0, 0), 'Gr\u00fcne': (100, 161, 45), 'SPD': (235, 0, 31), 'FDP': (255, 237, 0),
                   'AfD': (0, 158, 224), 'Linke': (190, 48, 117),
                   'Red-Red-Green': (190, 48, 117), 'Black-Yellow': (255, 237, 0), 'Jamaica': (118, 132, 15),
                   'Grand Coalition': (0, 0, 0), 'Traffic Light': (235, 0, 31), 'Black-Green': (100, 161, 45),
                   'Old Guard': (245, 118, 15),
                   'Government': (0, 0, 0), 'Opposition': (100, 161, 45)}
            blocs = {'Red-Red-Green': ['Gr\u00fcne', 'SPD', 'Linke'],
                     'Black-Yellow': ['CDU/CSU', 'FDP'],
                     'Jamaica': ['CDU/CSU', 'FDP', 'Gr\u00fcne'],
                     'Traffic Light': ['SPD', 'Gr\u00fcne', 'FDP'],
                     'Grand Coalition': ['CDU/CSU', 'SPD'],
                     'Black-Green': ['CDU/CSU', 'Gr\u00fcne'],
                     'Old Guard': ['CDU/CSU', 'SPD', 'FDP']}
            gov = {'Government': ['CDU/CSU', 'SPD'], 'Opposition': ['Gr\u00fcne', 'Linke', 'FDP', 'AfD']}
            file_name = 'test_data/germany_polling.txt'
            start = 4
            end_date = Date(2021, 9, 26)
            restart.append('election')
        elif choice == 'Austria':
            key = ['ÖVP', 'SPÖ', 'FPÖ', 'Gr\u00fcne', 'NEOS']
            col = {'ÖVP': (99, 195, 208), 'SPÖ': (206, 0, 12), 'FPÖ': (0, 86, 162), 'Gr\u00fcne': (136, 182, 38),
                   'NEOS': (232, 65, 136),
                   'Government': (99, 195, 208), 'Opposition': (206, 0, 12),
                   'Progressive': (206, 0, 12), 'Conservative': (99, 195, 208)}
            gov = {'Government': ['ÖVP', 'Gr\u00fcne'], 'Opposition': ['SPÖ', 'FPÖ', 'NEOS']}
            blocs = {'Progressive': ['SPÖ', 'Gr\u00fcne', 'NEOS'], 'Conservative': ['ÖVP', 'FPÖ']}
            file_name = 'test_data/austria_polling.txt'
            start = 4
            restart.append('election')
        elif choice == 'Poland':
            key = ['United Right', 'Civic Coalition', 'The Left', 'Polish Coalition', 'Kukiz\'15', 'Confederation',
                   'Poland 2050']
            col = {'United Right':  (38, 55, 120), 'Civic Coalition': (246, 143, 45), 'The Left': (172, 20, 90),
                   'Polish Coalition': (27, 177, 0), 'Kukiz\'15': (0, 0, 0), 'Confederation': (18, 39, 70),
                   'Poland 2050': (249, 192, 19),
                   'Government': (38, 55, 120), 'Opposition': (246, 143, 45),
                   'United Opposition': (246, 143, 45), 'Misc. Right': (18, 39, 70)}
            gov = {'Government': ['United Right'],
                   'Opposition': ['Civic Coalition', 'The Left', 'Polish Coalition', 'Kukiz\'15', 'Confederation',
                                  'Poland 2050']}
            blocs = {'United Right': ['United Right'],
                     'United Opposition': ['Civic Coalition', 'The Left', 'Polish Coalition', 'Poland 2050'],
                     'Misc. Right': ['Kukiz\'15', 'Confederation']}
            file_name = 'test_data/poland_polling.txt'
            start = 3
            restart.append('election')
        elif choice == 'Slovakia':
            key = ['OL\'aNO', 'SMER-SD', 'SR', 'L\'SNS', 'PS-SPOLU', 'PS-SPOLU', 'SaS', 'ZL\'', 'KDH',
                   'Magyar', 'Magyar', 'Magyar', 'Magyar', 'SNS', 'DV', 'HLAS-SD', 'REP']
            col = {'OL\'aNO': (190, 214, 47), 'SMER-SD': (217, 39, 39), 'SR': (11, 76, 159), 'L\'SNS': (11, 87, 16),
                   'PS-SPOLU': (0, 188, 255), 'SaS': (166, 206, 58), 'ZL\'': (255, 187, 0), 'KDH': (253, 209, 88),
                   'Magyar': (39, 93, 51), 'SNS': (37, 58, 121), 'DV': (255, 0, 43), 'HLAS-SD': (180, 40, 70),
                   'REP': (220, 1, 22),
                   'Government': (190, 214, 47), 'Opposition': (180, 40, 70),
                   'Left': (180, 40, 70), 'Right': (190, 214, 47)}
            gov = {'Government': ['OL\'aNO', 'SR', 'SaS', 'ZL\''],
                   'Opposition': ['SMER-SD', 'L\'SNS', 'PS-SPOLU', 'KDH', 'Magyar', 'SNS', 'DV', 'HLAS-SD', 'REP']}
            blocs = {'Left': ['SMER-SD', 'PS-SPOLU', 'DV', 'HLAS-SD'],
                     'Right': ['OL\'aNO', 'SR', 'L\'SNS', 'SaS', 'ZL\'', 'KDH', 'Magyar', 'SNS', 'REP']}
            file_name = 'test_data/slovakia_polling.txt'
            date = 0
            start = 2
            restart = ['Focus', 'AKO', '2020 elections']
        elif choice == 'Spain':
            key = ['PSOE', 'PP', 'VOX', 'UP', 'Cs', 'ERC', 'MP', 'JxCat', 'PNV', 'EHB', 'CUP', 'CC', 'BNG', 'NA+',
                   'PRC']
            col = {'PSOE': (239, 28, 39), 'PP': (29, 132, 206), 'VOX': (99, 190, 33), 'UP': (123, 73, 119),
                   'Cs': (235, 97, 9), 'ERC': (255, 178, 50), 'MP': (15, 222, 196), 'JxCat': (0, 199, 174),
                   'PNV': (74, 174, 74), 'EHB': (181, 207, 24), 'CUP': (255, 237, 0), 'CC': (255, 215, 0),
                   'BNG': (173, 207, 239), 'NA+': (129, 157, 163), 'PRC': (194, 206, 12),
                   'Government': (239, 28, 39), 'Opposition': (29, 132, 206),
                   'Left': (239, 28, 39), 'Right': (29, 132, 206), 'Regionalist': (255, 178, 50)}
            gov = {'Government': ['PSOE', 'UP', 'PNV', 'MP', 'BNG'],
                   'Opposition': ['PP', 'VOX', 'Cs', 'JxCat', 'CUP', 'CC', 'PRC']}
            blocs = {'Left': ['PSOE', 'UP'], 'Right': ['PP', 'VOX', 'Cs'],
                     'Regionalist': ['ERC', 'MP', 'JxCat', 'PNV', 'EHB', 'CUP', 'CC', 'BNG', 'NA+', 'PRC']}
            file_name = 'test_data/spain_polling.txt'
            restart = ['http']
            start = 4
            restart.append('Spanish general election')
        elif choice == 'Peru':
            key = ['Castillo', 'Fujimori']
            col = {'Castillo': (192, 10, 10), 'Fujimori': (255, 128, 0)}
            file_name = 'test_data/peru_polling.txt'
            start = 3
            restart = ['http']
            end_date = Date(2021, 6, 6)
        elif choice == 'Czechia':
            key = ['ANO', 'SPOLU', 'SPOLU', 'SPOLU', 'Pirati+STAN', 'Pirati+STAN', 'SPD', 'KSCM', 'CSSD']
            col = {'ANO': (38, 16, 96), 'SPOLU': (35, 44, 119), 'Pirati+STAN': (0, 0, 0), 'SPD': (33, 117, 187),
                   'KSCM': (204, 0, 0), 'CSSD': (236, 88, 0),
                   'Government': (38, 16, 96), 'Opposition': (0, 0, 0)}
            gov = {'Government': ['ANO', 'KSCM', 'CSSD'], 'Opposition': ['SPOLU', 'Pirati+STAN', 'SPD']}
            file_name = 'test_data/czechia_polling.txt'
            start = 26
        elif choice == 'Canada':
            key = ['CON', 'LIB', 'NDP', 'BQ', 'GPC', 'PPC']
            col = {'CON': (100, 149, 237), 'LIB': (234, 109, 106), 'NDP': (244, 164, 96), 'BQ': (135, 206, 250),
                   'GPC': (153, 201, 85), 'PPC': (131, 120, 158),
                   'Government': (234, 109, 106), 'Opposition': (100, 149, 237)}
            gov = {'Government': ['LIB'], 'Opposition': ['CON', 'NDP', 'BQ', 'GPC', 'PPC']}
            blocs = {'Progressive': ['LIB', 'NDP', 'BQ', 'GPC'], 'Conservative': ['CON', 'PPC']}
            file_name = 'test_data/canada_polling.txt'
            start = 3
        elif choice == 'Italy':
            key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'Art.1', 'SI', '+Eu', 'EV', 'A', 'IV', 'CI']
            col = {'M5S': (255, 235, 59), 'PD': (239, 28, 39), 'Lega': (0, 128, 0), 'FI': (0, 135, 220),
                   'FdI': (3, 56, 106), 'LeU': (199, 40, 55), '+Eu': (255, 215, 0), 'EV': (115, 193, 112),
                   'C!': (229, 131, 33), 'A': (0, 57, 170), 'IV': (214, 65, 140), 'NcI': (31, 107, 184),
                   'PaP': (160, 20, 46), 'Art.1': (210, 27, 48), 'SI': (239, 62, 62), 'CI': (49, 39, 131),
                   'Left': (239, 28, 39), 'Right': (0, 128, 0),
                   'Government': (255, 235, 59), 'Opposition': (3, 56, 106)}
            blocs = {'Left': ['PD', '+Eu', 'EV', 'LeU', 'IV', 'A', 'M5S', 'PaP'],
                     'Right': ['Lega', 'FI', 'FdI', 'C!', 'NcI']}
            gov = {'Government': ['M5S', 'Lega', 'PD', 'FI', 'LeU', 'IV', 'Art.1'],
                   'Opposition': ['FdI', '+Eu', 'C!', 'A', 'SI', 'CI']}
            file_name = 'test_data/italy_polling.txt'
            date = 0
            start = 2
        elif choice == 'Cyprus':
            key = ['DISY', 'AKEL', 'DIKO', 'EDEK-SYPOL', 'KA', 'KOSP', 'ELAM', 'DIPA', 'Anex']
            col = {'DISY': (21, 105, 199), 'AKEL': (179, 27, 27), 'DIKO': (255, 126, 0), 'EDEK-SYPOL': (22, 79, 70),
                   'KA': (0, 75, 145), 'KOSP': (127, 255, 0), 'ELAM': (0, 0, 0), 'DIPA': (255, 126, 0),
                   'Anex': (68, 36, 100)}
            file_name = 'test_data/cyprus_polling.txt'
            date = 0
            start = 1
        elif choice == 'Denmark':
            key = ['A', 'V', 'O', 'B', 'F', '\u00d8', 'C', '\u00c5', 'D', 'I', 'P', 'K', 'E', 'G']
            col = {'A': (240, 77, 70), 'V': (0, 40, 131), 'O': (252, 208, 59), 'B': (229, 0, 125), 'F': (191, 3, 26),
                   '\u00d8': (208, 0, 77), 'C': (0, 73, 49), '\u00c5': (0, 255, 0), 'D': (0, 80, 91),
                   'I': (63, 178, 190),
                   'P': (1, 152, 225), 'K': (255, 165, 0), 'E': (0, 66, 36), 'G': (128, 165, 26),
                   'Red': (240, 77, 70), 'Blue': (0, 40, 131)}
            blocs = {'Red': ['A', 'B', 'F', '\u00d8', '\u00c5', 'G'], 'Blue': ['V', 'O', 'C', 'D', 'I', 'P', 'K', 'E']}
            file_name = 'test_data/denmark_polling.txt'
            start = 3
            restart.append('election')
        elif choice == 'Finland':
            key = ['SDP', 'PS', 'KOK', 'KESK', 'VIHR', 'VAS', 'SFP', 'KD', 'LIIK']
            col = {'SDP': (245, 75, 75), 'PS': (255, 222, 85), 'KOK': (0, 98, 136), 'KESK': (52, 154, 43),
                   'VIHR': (97, 191, 26), 'VAS': (240, 10, 100), 'SFP': (255, 221, 147), 'KD': (2, 53, 164),
                   'LIIK': (180, 31, 121),
                   'Government': (245, 75, 75), 'Opposition': (255, 222, 85)}
            gov = {'Government': ['SDP', 'KESK', 'VIHR', 'VAS', 'SFP'], 'Opposition': ['KOK', 'PS', 'KD', 'LIIK']}
            file_name = 'test_data/finland_polling.txt'
            start = 3
            restart = ['http', 'election']
        elif choice == 'Sweden':
            key = ['V', 'S', 'MP', 'C', 'L', 'M', 'KD', 'SD']
            col = {'V': (176, 0, 0), 'S': (237, 27, 52), 'MP': (43, 145, 44), 'C': (1, 106, 57), 'L': (0, 106, 179),
                   'M': (1, 156, 219), 'KD': (0, 70, 120), 'SD': (254, 223, 9),
                   'Red-Green': (237, 27, 52), 'Alliance': (245, 137, 28),
                   'Government': (237, 27, 52), 'Opposition': (245, 137, 28)}
            blocs = {'Red-Green': ['S', 'V', 'MP'], 'Alliance': ['C', 'L', 'M', 'KD'], 'SD': ['SD']}
            gov = {'Government': ['S', 'MP', 'V', 'C', 'L'], 'Opposition': ['M', 'KD', 'SD']}
            file_name = 'test_data/sweden_polling.txt'
            start = 3
            restart = ['http', '2018 election']
        elif choice == 'Norway':
            key = ['R', 'SV', 'MDG', 'Ap', 'Sp', 'V', 'KrF', 'H', 'FrP']
            col = {'R': (231, 52, 69), 'SV': (188, 33, 73), 'MDG': (106, 147, 37), 'Ap': (227, 24, 54),
                   'Sp': (0, 133, 66),
                   'V': (17, 100, 104), 'KrF': (254, 193, 30), 'H': (135, 173, 215), 'FrP': (2, 76, 147),
                   'Red-Green': (227, 24, 54), 'Blue': (135, 173, 215)}
            blocs = {'Red-Green': ['R', 'SV', 'Ap', 'Sp'], 'Blue': ['V', 'KrF', 'H', 'FrP'], 'MDG': ['MDG']}
            file_name = 'test_data/norway_polling.txt'
            start = 4
            restart.append('election')
        elif choice == 'Iceland':
            key = ['D', 'V', 'S', 'M', 'B', 'P', 'F', 'C', 'J']
            col = {'D': (0, 173, 239), 'V': (0, 184, 120), 'S': (234, 0, 56), 'M': (0, 33, 105), 'B': (160, 208, 103),
                   'P': (137, 110, 189), 'F': (255, 202, 62), 'C': (255, 125, 20), 'J': (239, 72, 57),
                   'Government': (0, 184, 120), 'Opposition': (234, 0, 56),
                   'Socialist': (234, 0, 56), 'Liberal': (160, 208, 103), 'Conservative': (0, 173, 239)}
            blocs = {'Socialist': ['V', 'S', 'J'], 'Liberal': ['B', 'M', 'C', 'P'], 'Conservative': ['D', 'F']}
            gov = {'Government': ['V', 'B', 'D'], 'Opposition': ['S', 'M', 'P', 'F', 'C', 'J']}

            file_name = 'test_data/iceland_polling.txt'
            start = 4
            restart.append('election')
        elif choice == 'Portugal':
            key = ['PS', 'PSD', 'BE', 'CDU', 'CDS-PP', 'PAN', 'Chega', 'IL', 'LIVRE']
            col = {'PS': (255, 102, 255), 'PSD': (255, 153, 0), 'BE': (139, 0, 0), 'CDU': (255, 0, 0),
                   'CDS-PP': (0, 147, 221),
                   'PAN': (0, 128, 128), 'Chega': (32, 32, 86), 'IL': (0, 173, 239), 'LIVRE': (143, 188, 143),
                   'Left': (255, 102, 255), 'Right': (255, 153, 0)}
            blocs = {'Left': ['PS', 'BE', 'CDU', 'PAN', 'LIVRE'], 'Right': ['PSD', 'CDS-PP', 'Chega', 'IL']}
            file_name = 'test_data/portugal_polling.txt'
            start = 4
            restart.append('election')
        elif choice == 'New York':
            key = ['Eric Adams', 'Shaun Donovan', 'Kathryn Garcia', 'Raymond McGuire', 'Dianne Morales',
                   'Scott Stringer', 'Maya Wiley', 'Andrew Yang']
            col = {'Eric Adams': (0, 0, 255), 'Shaun Donovan': (102, 0, 102), 'Kathryn Garcia': (255, 128, 0),
                   'Raymond McGuire': (0, 102, 0), 'Dianne Morales': (255, 153, 255),
                   'Scott Stringer': (120, 120, 255), 'Maya Wiley': red, 'Andrew Yang': yellow}
            file_name = 'test_data/new_york_city_polling.txt'
            start = 4
            end_date = Date(2021, 6, 22)
        else:
            raise ValueError("No such choice.")
        if blocs is not None:
            for line in blocs.keys():
                if line not in col.keys():
                    col[line] = col[blocs[line][0]]
        if gov is not None:
            for line in gov.keys():
                if line not in col.keys():
                    col[line] = col[gov[line][0]]
        return file_name, key, col, blocs, gov, start, restart, date, end_date

    def make_graph(self):
        dat = copy.deepcopy(self.dat)
        if self.view in ['blocs', 'gov']:
            if self.view == 'blocs':
                relev = self.blocs
            else:
                relev = self.gov
            bdat = {}
            for b, ps in relev.items():
                bdat[b] = {}
                for p in ps:
                    for x, ys in dat[p].items():
                        if x in bdat[b].keys():
                            for i, y in enumerate(ys):
                                if y is None:
                                    count = 0
                                else:
                                    count = y
                                bdat[b][x][i] += count
                        else:
                            bdat[b][x] = list(map(lambda y: 0 if y is None else y, ys))
            dat = bdat

        for line, vals in dat.items():
            for x, ys in vals.items():
                dat[line][x] = list(filter(lambda x: x is not None and (x != 0 or self.view == 'parties'), ys))

        date = Date(2021, 1, 1)
        if self.end_date is not None and date_kit.date_dif(today, self.end_date) < 0:
            end = date_kit.date_dif(date, self.end_date)
        else:
            end = None
        ndat = weighted_averages(dat, self.spread, loc=True, end=end)
        if self.to_end_date and self.end_date is not None:
            x_max = date_kit.date_dif(date, self.end_date)
        else:
            x_max = None
        title = "Opinion Polling for " + self.choice

        if self.graph is not None:
            self.graph.hide()

        self.graph = GraphDisplay(screen_center, (screen_width, screen_height), ndat, x_title=None,
                                  y_title="Support (%)", title=title, step=1, align=CENTER, colours=self.col,
                                  initial_date=date, leader=True, y_min=0, dat_points=dat, x_max=x_max)
        self.graph.show()

    def change_view(self, view):
        self.view = view
        self.make_graph()

    def change_spread(self, button):
        if button == self.up_spread:
            self.down_spread.enable()
            self.spread *= 2
            if self.spread >= 240:
                self.spread = 240
                self.up_spread.disable()
        elif button == self.down_spread:
            self.up_spread.enable()
            self.spread //= 2
            if self.spread <= 15:
                self.spread = 15
                self.down_spread.disable()
        self.spread_txt.update(str(self.spread))
        self.make_graph()


def menu_page():
    widgets.clear()

    button_size = 64
    display = ScrollButtonDisplay(screen_center, (300, screen_height * 4 / 5), button_size * len(options), CENTER,
                                  button_size=button_size)
    buttons = []
    for i, entry in enumerate(options):
        b = Button((display.contain_rect.left, display.contain_rect.top + i * button_size),
                   (display.contain_rect.w, button_size), parent=display)
        b.callback(functools.partial(GraphPage, entry, to_end_date=True))
        img_path = 'images/flags/' + entry.lower() + '.png'
        try:
            img = Image((b.rect.centerx + b.rect.w / 8, b.rect.centery), (b.rect.h * 3 / 4, b.rect.h * 3 / 4),
                        img_path, align=LEFT)
            b.components.append(img)
        except FileNotFoundError:
            pass
        label = Text(entry.upper(), (b.rect.centerx + b.rect.w / 16, b.rect.centery), 24, align=RIGHT,
                     background_colour=display.colour)
        b.components.append(label)
        buttons.append(b)
    display.add_select_buttons(buttons)
    display.show()

    update_b = Button((screen_rect.centerx / 2, screen_rect.centery), align=CENTER, label='Update Data')
    update_b.callback(update_data)
    update_b.show()


def update_data(sel="All"):
    def update_dat(dest, url, olddat=None):
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
        if olddat is not None:
            with open(olddat, 'r', encoding='utf-8') as f:
                text += f.read()
        final = text.encode('utf-8')
        with open(dest, 'wb') as f:
            f.write(final)

    urls = {
        'Austria':  'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_next_Austrian_legislative_election&action=edit&section=3',
        'Canada':   'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_44th_Canadian_federal_election&action=edit&section=1',
        'Czechia':  'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_2021_Czech_legislative_election&action=edit&section=3',
        'Denmark':  'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_next_Danish_general_election&action=edit&section=3',
        'Germany':  'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_2021_German_federal_election&action=edit&section=3',
        'Iceland':  'https://en.wikipedia.org/w/index.php?title='
                    'Opinion_polling_for_the_next_Icelandic_parliamentary_election&action=edit&section=2',
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
        'New York': 'https://en.wikipedia.org/w/index.php?title='
                    'Template:Opinion_polling_for_the_2021_New_York_City_mayoral_election/Democratic_primaries&action='
                    'edit'
    }
    files = {
        'New York': 'test_data/new_york_city_polling.txt'
    }
    olddata = {
        'Canada':   'test_data/old_canada_polling.txt',
        'Denmark':  'test_data/old_denmark_polling.txt',
        'Germany':  'test_data/old_germany_polling.txt',
        'Italy':    'test_data/old_italy_polling.txt',
        'Norway':   'test_data/old_norway_polling.txt',
        'Poland':   'test_data/old_poland_polling.txt'
    }
    if sel == 'All':
        for tag, url in urls.items():
            if tag in files:
                dest = files[tag]
            else:
                dest = 'test_data/' + tag.lower() + '_polling.txt'
            if tag in olddata:
                olddat = olddata[tag]
            else:
                olddat = None
            update_dat(dest, url, olddat)


if __name__ == '__main__':
    options = ['Austria', 'Canada', 'Cyprus', 'Czechia', 'Denmark', 'Finland', 'Germany', 'Iceland', 'Italy', 'Norway',
               'Peru', 'Poland', 'Portugal', 'Slovakia', 'Spain', 'Sweden', 'New York']
    menu_page()
    game_loop()
