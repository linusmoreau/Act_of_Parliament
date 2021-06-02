from ui import *
from toolkit import *
import date_kit
import types


def read_data(content, key, start, restart, date, choice):
    dat: Dict[str, Dict[int, List[float]]] = {}
    rot = None
    end = 0
    year = '2021'
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
                if choice in ['Norway', 'Austria']:
                    line = line[:line.find('{')]
                elif choice == 'Sweden':
                    if 'ref' in line:
                        i += 1
                        continue
                elif choice == "Peru":
                    line = line.strip().strip('}')
                elif choice == 'Czechia' and 'rowspan="2"' in line:
                    i += 20
                    rot += 2
                elif choice in ["Italy", "Cyprus"]:
                    line = prevline
                    if line[0] == '!':
                        rot = None
                        i += 1
                        continue
                dates = line.split('|')[-1]
                if '-' in dates:
                    temp = dates.split('-')
                elif '–' in dates:
                    temp = dates.split('–')
                else:
                    temp = dates.split('â€“')
                temp = temp[-1].strip()
                temps = temp.split()
                if len(temps) == 2:
                    try:
                        year = int(temps[-1])
                        temp = '1 ' + temp
                    except ValueError:
                        temp = temp + ' ' + year
                elif len(temps) == 1:
                    temp = '1' + ' ' + temp + ' ' + year
                temp = temp.strip("'")
                # print(temp)
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
                if choice == 'Cyprus' and temp == '-' and p == 4:
                    i += 1
                    continue
                if temp == 'â€“' or temp == '-' or temp == '' or "small" in temp:
                    share = None
                else:
                    try:
                        share = float(temp.strip().strip("'"))
                    except ValueError:
                        share = None
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
    return dat


class GraphPage:

    def __init__(self, choice, view='parties', to_election=False):
        widgets.clear()

        self.graph = None
        self.choice = choice
        self.view = view
        self.file_name, self.key, self.col, self.blocs, self.gov, self.spread, self.start, self.restart, self.date, \
            self.election = self.choice_setting(self.choice)

        if not to_election:
            self.election = None

        with open(self.file_name, 'r', encoding='utf-8') as f:
            content = f.readlines()

        self.dat = read_data(content, self.key, self.start, self.restart, self.date, self.choice)

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
                                   align=CENTER, label="BLOC", parent=pinboard)
        pinboard.select_buttons.append(bloc_button)
        bloc_button.callback(functools.partial(self.change_view, 'blocs'))
        bloc_button.release_callback(functools.partial(self.change_view, 'parties'))
        if self.blocs is None:
            bloc_button.disable()
        bloc_button.show()

        gov_button = SelectButton((screen_width - 3 * unit_size, height * 2 / 3),
                                  (unit_size, unit_size),
                                  align=CENTER, label="GOV", parent=pinboard)
        pinboard.select_buttons.append(gov_button)
        gov_button.callback(functools.partial(self.change_view, 'gov'))
        gov_button.release_callback(functools.partial(self.change_view, 'parties'))
        if self.gov is None:
            gov_button.disable()
        gov_button.show()

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
        restart = '[http'
        date = 1
        spread = 60
        election = None
        blocs = None
        gov = None
        if choice == 'Germany':
            key = ['CDU/CSU', 'SPD', 'AfD', 'FDP', 'Linke', 'Gr\u00fcne']
            col = {'CDU/CSU': (0, 0, 0), 'Gr\u00fcne': (100, 161, 45), 'SPD': (235, 0, 31), 'FDP': (255, 237, 0),
                   'AfD': (0, 158, 224), 'Linke': (190, 48, 117),
                   'Left': (235, 0, 31), 'Right': (0, 0, 0),
                   'Government': (0, 0, 0), 'Opposition': (100, 161, 45)}
            blocs = {'Left': ['Gr\u00fcne', 'SPD', 'Linke'], 'Right': ['CDU/CSU', 'FDP', 'AfD']}
            gov = {'Government': ['CDU/CSU', 'SPD'], 'Opposition': ['Gr\u00fcne', 'Linke', 'FDP', 'AfD']}
            file_name = 'test_data/germany_polling.txt'
            start = 4
            election = Date(2021, 9, 26)
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
        elif choice == 'Peru':
            key = ['Castillo', 'Fujimori']
            col = {'Castillo': (192, 10, 10), 'Fujimori': (255, 128, 0)}
            file_name = 'test_data/peru_polling.txt'
            start = 3
            restart = 'http'
            election = Date(2021, 6, 6)
        elif choice == 'Czechia':
            key = ['ANO', 'SPOLU', 'Pirati+STAN', 'SPD', 'KSCM', 'CSSD']
            col = {'ANO': (38, 16, 96), 'SPOLU': (35, 44, 119), 'Pirati+STAN': (0, 0, 0), 'SPD': (33, 117, 187),
                   'KSCM': (204, 0, 0), 'CSSD': (236, 88, 0),
                   'Government': (38, 16, 96), 'Opposition': (0, 0, 0)}
            gov = {'Government': ['ANO', 'KSCM', 'CSSD'], 'Opposition': ['SPOLU', 'Pirati+STAN', 'SPD']}
            file_name = 'test_data/czechia_polling.txt'
            start = 4
        elif choice == 'Canada':
            key = ['CON', 'LIB', 'NDP', 'BQ', 'GPC', 'PPC']
            col = {'CON': (100, 149, 237), 'LIB': (234, 109, 106), 'NDP': (244, 164, 96), 'BQ': (135, 206, 250),
                   'GPC': (153, 201, 85), 'PPC': (131, 120, 158),
                   'Government': (234, 109, 106), 'Opposition': (100, 149, 237)}
            gov = {'Government': ['LIB'], 'Opposition': ['CON', 'NDP', 'BQ', 'GPC', 'PPC']}
            file_name = 'test_data/canada_polling.txt'
            start = 3
        elif choice == 'Italy':
            key = ['M5S', 'PD', 'Lega', 'FI', 'FdI', 'LeU', '+Eu', 'EV', 'C!', 'A', 'IV']
            col = {'M5S': (255, 235, 59), 'PD': (239, 28, 39), 'Lega': (0, 128, 0), 'FI': (0, 135, 220),
                   'FdI': (3, 56, 106), 'LeU': (199, 40, 55), '+Eu': (255, 215, 0), 'EV': (115, 193, 112),
                   'C!': (229, 131, 33), 'A': (0, 57, 170), 'IV': (214, 65, 140), 'NcI': (31, 107, 184),
                   'PaP': (160, 20, 46),
                   'Left': (239, 28, 39), 'Right': (0, 128, 0)}
            blocs = {'Left': ['PD', '+Eu', 'EV', 'LeU', 'IV', 'A', 'M5S', 'PaP'],
                     'Right': ['Lega', 'FI', 'FdI', 'C!', 'NcI']}
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
        elif choice == 'Finland':
            key = ['SDP', 'PS', 'KOK', 'KESK', 'VIHR', 'VAS', 'SFP', 'KD', 'LIIK']
            col = {'SDP': (245, 75, 75), 'PS': (255, 222, 85), 'KOK': (0, 98, 136), 'KESK': (52, 154, 43),
                   'VIHR': (97, 191, 26), 'VAS': (240, 10, 100), 'SFP': (255, 221, 147), 'KD': (2, 53, 164),
                   'LIIK': (180, 31, 121),
                   'Government': (245, 75, 75), 'Opposition': (255, 222, 85)}
            gov = {'Government': ['SDP', 'KESK', 'VIHR', 'VAS', 'SFP'], 'Opposition': ['KOK', 'PS', 'KD', 'LIIK']}
            file_name = 'test_data/finland_polling.txt'
            start = 3
            restart = 'http'
        elif choice == 'Sweden':
            key = ['V', 'S', 'MP', 'C', 'L', 'M', 'KD', 'SD']
            col = {'V': (176, 0, 0), 'S': (237, 27, 52), 'MP': (43, 145, 44), 'C': (1, 106, 57), 'L': (0, 106, 179),
                   'M': (1, 156, 219), 'KD': (0, 70, 120), 'SD': (254, 223, 9),
                   'Red-Greens': (237, 27, 52), 'Alliance': (245, 137, 28),
                   'Government': (237, 27, 52), 'Opposition': (245, 137, 28)}
            blocs = {'Red-Greens': ['S', 'V', 'MP'], 'Alliance': ['C', 'L', 'M', 'KD'], 'SD': ['SD']}
            gov = {'Government': ['S', 'MP', 'V', 'C', 'L'], 'Opposition': ['M', 'KD', 'SD']}
            file_name = 'test_data/sweden_polling.txt'
            start = 3
            restart = 'http'
        elif choice == 'Norway':
            key = ['R', 'SV', 'MDG', 'Ap', 'Sp', 'V', 'KrF', 'H', 'FrP']
            col = {'R': (231, 52, 69), 'SV': (188, 33, 73), 'MDG': (106, 147, 37), 'Ap': (227, 24, 54),
                   'Sp': (0, 133, 66),
                   'V': (17, 100, 104), 'KrF': (254, 193, 30), 'H': (135, 173, 215), 'FrP': (2, 76, 147),
                   'Red-Green': (227, 24, 54), 'Blue': (135, 173, 215)}
            blocs = {'Red-Green': ['R', 'SV', 'Ap', 'Sp'], 'Blue': ['V', 'KrF', 'H', 'FrP'], 'MDG': ['MDG']}
            file_name = 'test_data/norway_polling.txt'
            start = 4
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
        elif choice == 'Portugal':
            key = ['PS', 'PSD', 'BE', 'CDU', 'CDS-PP', 'PAN', 'Chega', 'IL', 'LIVRE']
            col = {'PS': (255, 102, 255), 'PSD': (255, 153, 0), 'BE': (139, 0, 0), 'CDU': (255, 0, 0),
                   'CDS-PP': (0, 147, 221),
                   'PAN': (0, 128, 128), 'Chega': (32, 32, 86), 'IL': (0, 173, 239), 'LIVRE': (143, 188, 143),
                   'Left': (255, 102, 255), 'Right': (255, 153, 0)}
            blocs = {'Left': ['PS', 'BE', 'CDU', 'PAN', 'LIVRE'], 'Right': ['PSD', 'CDS-PP', 'Chega', 'IL']}
            file_name = 'test_data/portugal_polling.txt'
            start = 4
        else:
            raise ValueError("No such choice.")
        return file_name, key, col, blocs, gov, spread, start, restart, date, election

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
                            bdat[b][x] = ys.copy()
            dat = bdat

        for line, vals in dat.items():
            for x, ys in vals.items():
                dat[line][x] = list(filter(lambda x: x is not None, ys))

        ndat = weighted_averages(dat, self.spread)
        date = Date(2021, 1, 1)
        if self.election is not None:
            x_max = date_kit.date_dif(date, self.election)
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

    options = ['Austria', 'Canada', 'Cyprus', 'Czechia', 'Denmark', 'Finland', 'Germany', 'Iceland', 'Italy', 'Norway',
               'Peru', 'Portugal', 'Sweden']

    button_size = 64
    display = ScrollButtonDisplay(screen_center, (300, screen_height * 4 / 5), button_size * len(options), CENTER,
                                  button_size=button_size)
    buttons = []
    for i, entry in enumerate(options):
        b = Button((display.contain_rect.left, display.contain_rect.top + i * button_size),
                   (display.contain_rect.w, button_size), parent=display)
        b.callback(functools.partial(GraphPage, entry))
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


menu_page()
game_loop()
