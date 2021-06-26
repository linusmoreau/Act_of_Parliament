import logic
import random
import data
import threading
import time
from base_ui import *
from collections import OrderedDict

display_rect = pygame.Rect((0, screen_height / 12), (screen_width, screen_height * 11 / 12))
MENU_WIDTH = screen_width / 4

# cursor_size = 20
# point_pos = int(cursor_size / 3)
# hand_cursor = pygame.transform.scale(pygame.image.load("images/hand_cursor.png"), (cursor_size, cursor_size))

if not os.path.isdir("saves"):
    os.makedirs("saves")


class Music:
    channel = None
    file_path = "sound/"
    maximum = 1000

    def __init__(self, track):
        self.soundtrack = track
        random.shuffle(self.soundtrack)
        self.track_num = 0
        self.volume = data.settings['volume']
        self.min = 1
        self.max = Music.maximum
        self.slider = None
        self.showing = None
        self.playing = None
        self.pause_b = None
        self.unpause_b = None
        self.paused = False
        self.volume_txt = None
        pygame.mixer.init()
        # noinspection PyArgumentList
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        self.update_volume()
        self.new_track()
        Music.channel = self

    def show_widget(self, x, y, base=None, w=None):
        if base is None:
            base = text_size(BASE_FONT_SIZE)
        if w is None:
            w = screen_width / 8
        h = w / 12
        x2 = x * 3 / 4
        self.make_slider((x, y), (w, h))
        self.show_playing((x2, y + base[1]), x2, align=TOPLEFT)
        self.skip((x2 - base[0], y + h), (h, h), align=TOPRIGHT)
        self.set_up_pause((x2 - base[0] - h * 3 / 2, y + h), (h, h), align=TOPRIGHT)
        Text("Audio", (x, y - base[1]), align=BOTTOM).show()

    def update_text(self):
        text = str(int(self.volume))
        if self.volume_txt is not None:
            self.volume_txt.update(text, RIGHT, (self.slider.rect.left - 10, self.slider.rect.centery))
        else:
            self.volume_txt = Text(text, (self.slider.rect.left - 10, self.slider.rect.centery),
                                   align=RIGHT, parent=self)
        self.volume_txt.show()

    def update_volume(self):
        pygame.mixer.music.set_volume(self.volume / 1000)

    def make_slider(self, pos, area, align=CENTER, parent=None):
        if self.volume == 0:
            point = self.min
        else:
            point = self.volume
        self.slider = Slider(pos, area, self, point, align=align, parent=parent,
                             minimum=self.min, maximum=self.max, log=True)
        self.slider.show()
        self.update_text()

    def show_playing(self, pos, width, align=TOPLEFT):
        if self.showing in widgets:
            self.showing.hide()
        self.showing = Text("Now playing: \n" + data.soundtrack[self.playing], pos, align=align,
                            multiline=True, width=width)
        self.showing.show()

    def skip(self, pos, area, align=CENTER):
        b = Button(pos, area, align=align)
        b.components.append(Image(b.rect.center, (b.rect.w * 0.8, b.rect.h * 0.8), "images/skip.png", align=CENTER))
        b.callback(self.new_track)
        b.set_tooltip("Skip")
        b.show()

    def set_up_pause(self, pos, area, align=CENTER):
        b = Button(pos, area, align=align)
        b.components.append(Image(b.rect.center, (b.rect.w * 0.8, b.rect.h * 0.8), "images/pause.png", align=CENTER))
        b.callback(self.pause)
        b.set_tooltip("Pause")
        b.show()
        self.pause_b = b
        b = Button(pos, area, align=align)
        b.components.append(Image(b.rect.center, (b.rect.w * 0.8, b.rect.h * 0.8), "images/play.png", align=CENTER))
        b.callback(self.unpause)
        b.set_tooltip("Play")
        self.unpause_b = b

    def pause(self):
        pygame.mixer.music.pause()
        self.pause_b.hide()
        self.unpause_b.show()
        self.paused = True

    def unpause(self):
        pygame.mixer.music.unpause()
        self.unpause_b.hide()
        self.pause_b.show()
        self.paused = False

    def update_slider(self):
        if self.slider is not None:
            v = self.slider.get_value()
            if v == self.min:
                self.volume = 0
            else:
                self.volume = v
            self.update_volume()
            self.update_text()

    def new_track(self):
        try:
            self.playing = self.soundtrack[self.track_num]
            self.track_num += 1
        except IndexError:
            random.shuffle(self.soundtrack)
            self.playing = self.soundtrack[0]
            self.track_num = 1
        pygame.mixer.music.load(Music.file_path + self.playing)
        pygame.mixer.music.play()
        if self.showing in widgets:
            self.show_playing(self.showing.rect.topleft, self.showing.rect.w)
        if self.paused:
            pygame.mixer.music.pause()

    def now_playing(self):
        return data.soundtrack[self.playing]


class Confirmation(PopUp):

    def __init__(self, func=None, text=None):
        super().__init__(screen_center, (screen_width / 3, screen_height / 3), close=False, kind='confirm',
                         unique=True)
        generic = "Are you sure you want to"
        if text is None:
            generic = generic + " do this?"
        msg = Text(generic, (self.rect.centerx, self.rect.top + text_size(BASE_FONT_SIZE)[1]),
                   align=TOP, justify=CENTER, colour=white, background_colour=black)
        self.components.append(msg)

        if text is not None:
            inf = Text(text, (self.rect.centerx, msg.rect.bottom + text_size(BASE_FONT_SIZE)[1]), align=TOP,
                       justify=CENTER, colour=gold, background_colour=black, multiline=True, width=self.rect.w)
            self.components.append(inf)

        yes = Button((self.rect.right - self.rect.w / 8, self.rect.bottom - self.rect.h / 8),
                     (self.rect.w / 4, self.rect.h / 8), align=BOTTOMRIGHT, label="Do it!")
        if func is not None:
            yes.callback(func)
        yes.callback(self.close)
        self.components.append(yes)
        no = Button((self.rect.left + self.rect.w / 8, self.rect.bottom - self.rect.h / 8),
                    (self.rect.w / 4, self.rect.h / 8), align=BOTTOMLEFT, label="Actually...")
        no.callback(self.close)
        self.components.append(no)


class HierarchyButtonDisplay(ScrollButtonDisplay):

    def __init__(self, position, area, categories, align=TOPLEFT, step=None, edge=DEFAULT_EDGE, colour=light_grey,
                 deselect=True, button_labels=None):
        """categories is an ordered dictionary"""
        self.categories = categories
        if step is None:
            self.step = Button.default_height
        else:
            self.step = step
        self.deselect = deselect
        super().__init__(position, area, self.step * len(categories), align=align, edge=edge, button_size=self.step,
                         colour=colour)
        self.button_tags = {}
        if button_labels is None:
            self.button_labels = {}
        else:
            self.button_labels = button_labels
        self.buttons = self.gen_buttons(categories)
        self.all_buttons = flatten(self.buttons)
        self.visible_buttons = list(self.buttons.keys())
        self.update_display()

    def gen_buttons(self, categories, encaps=None):
        font_colour = black
        buttons = OrderedDict()
        for i, button_tag in enumerate(list(categories.keys())):
            if type(categories[button_tag]).__name__ == "OrderedDict":
                b = Button((self.contain_rect.left, self.contain_rect.top + i * self.step),
                    (self.contain_rect.w, self.step), parent=self)
                b.normal_colour = fade_colour((100, 100, 200), 200)
                if button_tag in self.button_labels:
                    text = self.button_labels[button_tag]
                else:
                    text = toolkit.entitle(button_tag.split('/')[-1])
                b.components.append(
                    Text(text, b.rect.center, font_size=BASE_FONT_SIZE, align=CENTER,
                         colour=font_colour, background_colour=b.normal_colour)
                )
                b.callback(b.expand)
                b.update()
                buttons[b] = self.gen_buttons(categories[button_tag], b)
            else:
                b = SelectButton((self.contain_rect.left, self.contain_rect.top + i * self.step),
                    (self.contain_rect.w, self.step), parent=self, deselectable=self.deselect)
                b.normal_colour = fade_colour((200, 200, 100), 200)
                if button_tag in self.button_labels:
                    text = self.button_labels[button_tag]
                else:
                    text = toolkit.entitle(button_tag.split('/')[-1])
                b.components.append(
                    Text(text, b.rect.center, font_size=BASE_FONT_SIZE,
                         align=CENTER, colour=font_colour, background_colour=b.normal_colour, width=b.rect.w,
                         multiline=True, justify=CENTER)
                )
                if categories[button_tag] is not None:
                    for func in categories[button_tag]["funcs"]:
                        b.callback(func)
                    if self.deselect:
                        for func in categories[button_tag]["release_funcs"]:
                            b.release_callback(func)
                b.update()
                buttons[b] = None
                self.select_buttons.append(b)
            b.encaps = encaps
            self.button_tags[button_tag] = b
        return buttons

    def update_display(self, wid=None):
        for b in self.all_buttons:
            if b in self.components:
                self.components.remove(b)
            if b in Button.buttons:
                Button.buttons.remove(b)
        self.total_size = len(self.visible_buttons) * self.step + SHADOW
        if self.scroll_bar in self.extensions:
            self.extensions.remove(self.scroll_bar)
        if self.total_size > self.contain_rect.h:
            self.set_scroll_bar()
        for i, b in enumerate(self.visible_buttons):
            if b is not wid:
                b.move_to([self.contain_rect.left, self.contain_rect.top + i * self.step - round(self.scroll_pos)])
                if b.state is SELECT_STATE:
                    b.move(y=SHADOW)
            self.components.append(b)
            Button.buttons.append(b)
        if self.total_size - self.scroll_pos < self.contain_rect.h and \
                self.visible_buttons[-1].rect.bottom < self.contain_rect.bottom:
            self.overshot_down()
        Widget.change = True

    def expand(self, wid):
        if wid in self.buttons:
            butt = list(self.buttons[wid].keys())
            butt.reverse()
            for i, b in enumerate(butt):
                if b in self.visible_buttons:
                    self.visible_buttons.remove(b)
                else:
                    self.visible_buttons.insert(self.visible_buttons.index(wid) + 1, b)
        self.update_display(wid)


def flatten(buttons):
    flat = []
    for b in buttons:
        flat.append(b)
        if buttons[b] is not None:
            flat.extend(flatten(buttons[b]))
    return flat


class PartiesButtonDisplay(ScrollButtonDisplay):

    def __init__(self, position, area, parties, align=TOPLEFT, step=None, edge=DEFAULT_EDGE):
        if step is None:
            step = Button.default_height
        self.parties = parties
        order = sorted(list(parties), key=lambda party: parties[party].seats, reverse=True)

        super().__init__(position, area, step * len(order), align=align, edge=edge, button_size=step)

        for i, party in enumerate(order):
            b = SelectButton((self.contain_rect.left, self.contain_rect.top + i * step), (self.contain_rect.w, step),
                parent=self)
            b.party = party
            font_colour = black
            b.normal_colour = fade_colour(data.colours[party])
            b.components.append(
                Text(parties[party].name, (b.rect.x + b.rect.w / 10, b.rect.y + b.rect.h / 3),
                     font_size=int(b.rect.h / 3), align=TOPLEFT, colour=font_colour, background_colour=b.normal_colour)
            )
            self.select_buttons.append(b)
            b.update()

        self.components.extend(self.select_buttons)
        # self.visible_buttons.extend(self.select_buttons)


class SavePopUp(PopUp):
    width = screen_width / 4
    height = screen_height / 2

    def __init__(self):
        super().__init__(screen_center, (self.width, self.height), kind="save", unique=True)
        self.title = Text("Save Game", (self.rect.center[0], self.rect.y + self.rect.height / 16),
                          font_size=TITLE_SIZE, parent=self, colour=white, background_colour=black,
                          align=TOP)
        self.components.append(self.title)

        save = Button((self.rect.center[0], self.rect.bottom - self.rect.h / 16),
                      (self.width / 3, text_size(BASE_FONT_SIZE)[1] * 2), align=BOTTOM, label="Save", parent=self)
        save.callback(self.make_save)
        self.components.append(save)
        self.user_input = TextInput('', (self.rect.center[0], save.rect.top - self.rect.h / 16),
                                    (self.rect.w * 3 / 4, text_size(BASE_FONT_SIZE)[1]), align=BOTTOM,
                                    colour=black, background_colour=white)
        text_capture.append(self.user_input)
        self.components.append(self.user_input)

        self.scroll_list = self.make_selection()
        self.components.append(self.scroll_list)

    def make_selection(self):
        with os.scandir('saves/') as entries:
            files = []
            for entry in entries:
                if not entry.name.startswith('.') and entry.is_file():
                    files.append(entry)
            order = sorted(list(files), key=lambda file: file.stat().st_mtime, reverse=True)
        if len(files) > 0:
            b_size = text_size(BASE_FONT_SIZE)[1] * 2
            scroll_list = ScrollButtonDisplay(
                (self.rect.center[0], self.title.rect.bottom + self.rect.h / 16), (self.rect.w * 3 / 4, self.rect.h -
                (self.title.rect.h + self.rect.h / 8) - (self.rect.bottom - self.user_input.rect.top)),
                align=TOP, button_size=b_size, total_size=b_size * len(order)
            )
            for i, entry in enumerate(order):
                SavesButton((scroll_list.contain_rect.left, scroll_list.contain_rect.top + i * b_size),
                            (scroll_list.contain_rect.w, b_size), parent=scroll_list, label=entry.name[:-4],
                            entry=entry)
            scroll_list.components.extend(scroll_list.select_buttons)
        else:
            scroll_list = Text("No existing save files", self.rect.center, colour=white, background_colour=black)
        return scroll_list

    def make_save(self):
        done = False
        if type(self.scroll_list).__name__ == "ScrollButtonDisplay":
            for b in self.scroll_list.select_buttons:
                if b.state == SELECT_STATE:
                    logic.make_save(b.entry.name)
                    done = True
                    break
        if not done:
            if self.user_input.text == '':
                logic.make_save("autosave.txt")
            else:
                logic.make_save(self.user_input.text + ".txt")
        self.close()


class LoadPopUp(PopUp):
    width = screen_width / 4
    height = screen_height / 2

    def __init__(self):
        super().__init__(screen_center, (self.width, self.height), kind="load", unique=True)
        self.title = Text("Load Game", (self.rect.center[0], self.rect.y + self.rect.height / 16),
                          font_size=TITLE_SIZE, parent=self, colour=white, background_colour=black,
                          align=TOP)
        self.components.append(self.title)

        self.load = Button((self.rect.center[0], self.rect.bottom - self.rect.h / 16),
                           (self.width / 3, text_size(BASE_FONT_SIZE)[1] * 2), align=BOTTOM, label="Load", parent=self)
        self.load.callback(self.make_load)
        self.components.append(self.load)
        self.scroll_list = self.make_selection()
        self.components.append(self.scroll_list)

    def make_selection(self):
        with os.scandir('saves/') as entries:
            files = []
            for entry in entries:
                if not entry.name.startswith('.') and entry.is_file():
                    files.append(entry)
            order = sorted(list(files), key=lambda file: file.stat().st_mtime, reverse=True)
        if len(files) > 0:
            b_size = text_size(BASE_FONT_SIZE)[1] * 2
            scroll_list = \
                ScrollButtonDisplay((self.rect.center[0], self.title.rect.bottom + self.rect.h / 16),
                                    (self.rect.w * 3 / 4, self.rect.h - (self.title.rect.h + self.rect.h / 8) -
                                     (self.rect.bottom - self.load.rect.top) - self.rect.h / 16),
                                    align=TOP, button_size=b_size, total_size=b_size * len(order), parent=self)
            for i, entry in enumerate(order):
                SavesButton((scroll_list.contain_rect.left, scroll_list.contain_rect.top + i * b_size),
                            (scroll_list.contain_rect.w, b_size), parent=scroll_list, label=entry.name[:-4],
                            entry=entry)
            scroll_list.components.extend(scroll_list.select_buttons)
        else:
            scroll_list = Text("No existing save files", self.rect.center, colour=white, background_colour=black)
        return scroll_list

    def make_load(self):
        if type(self.scroll_list).__name__ == "ScrollButtonDisplay":
            for b in self.scroll_list.select_buttons:
                if b.state == SELECT_STATE:
                    LoadingScreen(functools.partial(self.loading, b.entry.name))
                    break

    def loading(self, name):
        logic.load_save(name)
        set_up_first_page()
        self.fading = False
        self.close()


class SavesButton(SelectButton):

    def __init__(self, pos, area, parent, label, entry):
        self.entry = entry
        super().__init__(pos, area, parent=parent, label=label)
        delete = Button((self.rect.right - self.rect.w / 16, self.rect.center[1]), (self.rect.h / 2, self.rect.h / 2),
                        align=RIGHT, parent=self, colour=(200, 20, 20))
        bin_img = Image(delete.rect.center, (delete.rect.w * 0.8, delete.rect.h * 0.8), img_path="images/bin.png")
        delete.components.append(bin_img)
        delete.callback(self.confirm)
        self.components.append(delete)
        self.parent.select_buttons.append(self)
        self.parent.button_tags[label] = self
        self.update()

    def confirm(self):
        text = "Delete save file '" + self.entry.name + "'"
        Confirmation(func=self.delete_save, text=text)

    def delete_save(self):
        logic.delete_save(self.entry.name)
        popup = self.parent.parent
        if popup is not None:
            popup.components.remove(self.parent)
            popup.scroll_list = popup.make_selection()
            popup.components.append(popup.scroll_list)


class PersonDisplay(CircleSelectButton):
    velocity = 5
    default_alpha = 255
    alpha_rate = 5

    def __init__(self, position, radius, person, parent=None, appearing=False, card=None):
        self.card = card
        super().__init__(position, radius=radius, align=CENTER, border_thickness=0,
                         parent=parent, threed=False, exclusive=False)
        if card is not None:
            self.state = SELECT_STATE
            self.card = card
        self.person = person
        self.dest = position
        self.disappearing = False
        self.appearing = appearing
        self.surface.set_colorkey(white)
        if self.appearing:
            self.surface.set_alpha(0)
        else:
            self.surface.set_alpha(self.default_alpha)
        self.callback(self.make_card)
        self.normal_colour = self.person.party.colour
        self.update()

    def make_card(self):
        self.card = PersonCard(self)

    def make_tooltip(self, mouse):
        return PersonTag(self.person, (mouse[0], mouse[1] + TOOLTIP_OFFSET), parent=self)

    def update(self):
        super().update()
        if self.card is not None and self.state is not SELECT_STATE:
            self.card.close()

    def animate(self):
        if self.dest != self.rect.topleft:
            self.change_pos()
            Widget.change = True
        super().animate()

    def change_pos(self):
        direct = (self.dest[0] - self.rect[0], self.dest[1] - self.rect[1])
        if direct[0] ** 2 + direct[1] ** 2 <= self.velocity ** 2:
            self.rect.topleft = self.dest
        elif direct[0] == 0:
            if direct[1] > 0:
                self.rect[1] += self.velocity
            else:
                self.rect[1] -= self.velocity
        elif direct[1] == 0:
            if direct[0] > 0:
                self.rect[0] += self.velocity
            else:
                self.rect[0] -= self.velocity
        else:
            ratio = abs(direct[0] / direct[1])
            vx = (self.velocity ** 2 * ratio ** 2 / (ratio ** 2 + 1)) ** 0.5
            vy = vx / ratio
            if direct[0] > 0:
                self.rect[0] += vx
            else:
                self.rect[0] -= vx
            if direct[1] > 0:
                self.rect[1] += vy
            else:
                self.rect[1] -= vy


class PersonTag(BaseToolTip):

    def __init__(self, person, pos, colour=whitish, background_colour=black, align=LEFT, appearing=True, parent=None):
        self.person = person
        self.parent = parent
        self.vote_num = self.parent.parent.display_vote
        if self.parent.parent.display_vote is not None:
            self.vote = self.parent.parent.display_vote[self.person.id_num]
        else:
            self.vote = None
        if background_colour is None:
            canvas = black
        else:
            canvas = background_colour
        name = Text(self.person.name, (0, 0), colour=colour, background_colour=canvas, multiline=False, margin=2)
        height = name.rect.height
        width = name.rect.width
        reasons = []
        total_reason = None
        margin = 0
        if self.vote is not None:
            margin = 8
            font_size = 14
            total = sum(list(self.vote.values()))
            if total > 0:
                colour = green
            else:
                colour = red
            total_reason = Text(' ' + str(total), (0, 0), colour=colour, background_colour=canvas)
            width += total_reason.rect.width
            for reason in sorted(list(self.vote.keys()), key=lambda x: abs(self.vote[x]), reverse=True):
                if self.vote[reason] > 0:
                    colour = green
                elif self.vote[reason] < 0:
                    colour = red
                else:
                    colour = gold
                disp = Text(reason + ': ', (0, 0), colour=white, background_colour=canvas, font_size=font_size)
                amount = Text(str(self.vote[reason]), (0, 0), colour=colour, background_colour=canvas,
                              font_size=font_size)
                w = disp.rect.w + amount.rect.w
                h = disp.rect.h
                row = pygame.Surface((w, h))
                row.fill(canvas)
                row.set_colorkey(canvas)
                row.blit(disp.surface, (0, 0))
                row.blit(amount.surface, (disp.rect.w, 0))
                reasons.append(row)
                if w > width:
                    width = w
                height += disp.rect.h
        width += 2 * margin
        height += 2 * margin
        surf = pygame.Surface((width, height))
        super().__init__(pos, surf, align=align, background_colour=canvas, appearing=appearing, default_alpha=230)
        loc = margin
        self.surface.blit(name.surface, (margin, margin))
        loc += name.rect.height
        for reason in reasons:
            self.surface.blit(reason, (margin, loc))
            loc += reason.get_height()
        if total_reason is not None:
            self.surface.blit(total_reason.surface, (width - total_reason.rect.w - margin, margin))


class PersonCard(PopUp):
    width = int(screen_width / 4)
    height = int(screen_height / 2)
    instances = []
    actions_panel_width = width / 2

    def __init__(self, visual):
        if data.settings['graphics'] == 0:
            opacity = 255
            colour = (20, 20, 20)
        elif data.settings['graphics'] == 1:
            opacity = 240
            colour = black
        else:
            opacity = 255
            colour = black
        surface = pygame.Surface((self.width, self.height))
        surface.fill(colour)
        pos = (screen_center[0] + 4 * len(PersonCard.instances), screen_center[1] + 4 * len(PersonCard.instances))
        super().__init__(pos, (self.width, self.height), surface=surface, opacity=opacity)
        self.visual = visual
        self.person = self.visual.person

        self.action_toggle = Button((self.rect.right, self.rect.top + self.rect.h / 4),
                                    (self.rect.w / 16, self.rect.h / 8),
                                    parent=self, label='>', threed=False)
        self.action_toggle.set_tooltip("Open Actions Panel")
        self.action_toggle.callback(self.open_actions_panel)
        self.extensions.append(self.action_toggle)
        self.action_panel = None

        margin = 20
        name = Text(self.person.name, (margin, margin), int(BASE_FONT_SIZE * 5 / 4), align=TOPLEFT, colour=white,
                    background_colour=colour)
        self.surface.blit(name.surface, name.rect)

        char_h = text_size(BASE_FONT_SIZE)[1]
        pos = (self.rect.x + margin, self.rect.y + name.rect.bottom + margin)
        area = (self.rect.w - 2 * margin, char_h * 6)
        descriptors = self.descriptors(pos, area, colour, char_h)
        self.components.append(descriptors)

        pos = (descriptors.rect.left, descriptors.rect.bottom + margin)
        area = (self.rect.w - 2 * margin, char_h * 8)
        beliefs = self.beliefs(pos, area, colour, char_h)
        self.components.append(beliefs)

        PersonCard.instances.append(self)

    def open_actions_panel(self):
        self.action_toggle.move(x=self.actions_panel_width)
        self.action_toggle.reset_callbacks()
        self.action_toggle.callback(self.close_actions_panel)
        self.action_toggle.label('<')
        self.action_toggle.set_tooltip("Close Actions Panel")

        button_size = int(self.rect.h / 10)
        if self.rect.h * 3 / 4 > button_size * len(self.person.actions) + SHADOW:
            height = button_size * len(self.person.actions) + SHADOW
        else:
            height = self.rect.h * 3 / 4
        self.action_panel = ScrollButtonDisplay(self.rect.topright, (self.actions_panel_width, height),
                            total_size=len(self.person.actions) * button_size, align=TOPLEFT,
                            button_size=button_size, parent=self, edge=0, colour=black)
        for i, action in enumerate(self.person.actions):
            b = SelectButton((self.action_panel.contain_rect.left,
                              self.action_panel.contain_rect.top + i * button_size),
                             (self.action_panel.contain_rect.w, button_size), parent=self.action_panel, label=action)
            self.action_panel.select_buttons.append(b)
            self.action_panel.components.append(b)
        self.extensions.append(self.action_panel)

    def close_actions_panel(self):
        self.action_toggle.move(x=-self.actions_panel_width)
        self.action_toggle.reset_callbacks()
        self.action_toggle.callback(self.open_actions_panel)
        self.action_toggle.label('>')
        self.action_toggle.set_tooltip("Open Actions Panel")
        self.extensions.remove(self.action_panel)

    def descriptors(self, pos, area, colour, char_h):
        descriptors = [self.person.age, self.person.gender, self.person.background, self.person.language,
                       self.person.party.name, self.person.riding]
        desc_names = ["Age", "Gender", "Background", "Language", "Party", "Riding"]
        x = 0
        y = 0
        total_size = char_h * len(descriptors)
        cont = Widget(pos, (area[0], total_size))
        cont.surface.set_colorkey(black)
        for i in range(len(descriptors)):
            if desc_names[i] == "Riding":
                written = descriptors[i]
                riding = logic.ridings[self.person.riding]
                func = functools.partial(get_page, 'ridings', riding.region + '/' + riding.tag)
            else:
                written = toolkit.entitle(descriptors[i])
                func = None
            if desc_names[i] == "Party":
                desc_colour = self.person.party.colour
            else:
                desc_colour = gold
            self.draw_descriptor(cont, written, desc_names[i], (x, y), desc_colour,
                                 background=colour, in_func=func)
            y += char_h
        display = ScrollDisplay([cont], pos, area, total_size=total_size, parent=self)
        return display

    def beliefs(self, pos, area, colour, char_h):   # todo sort the beliefs by value importance
        x = 0
        y = 0
        total_size = char_h * len(self.person.values)
        cont = Widget(pos, (area[0], total_size))
        cont.surface.set_colorkey(black)
        for belief in self.person.values:
            pol_pos = logic.det_pol_pos(self.person.values[belief])
            if pol_pos in ["far-left", "left", "far-right", "right"]:
                bold = True
            else:
                bold = False
            msg = toolkit.capitalize(pol_pos) + ' (' + str(self.person.values[belief]) + ')'
            self.draw_descriptor(cont, msg, toolkit.entitle(belief), (x, y), data.colours[pol_pos], background=colour,
                                 bold=bold)
            y += char_h
        display = ScrollDisplay([cont], pos, area, total_size=total_size, parent=self)
        return display

    @staticmethod
    def draw_descriptor(wid, descriptor, desc_name, pos, desc_colour=gold, background=black, bold=False, italic=False,
                        underline=False, in_func=None):
        marker = Text(desc_name + ': ', pos, align=TOPLEFT, colour=white, background_colour=background)
        desc = Text(descriptor, marker.rect.topright, align=TOPLEFT, colour=desc_colour, background_colour=background,
                    bold=bold, italic=italic, underline=underline, in_func=in_func)
        wid.surface.blit(marker.surface, marker.rect)
        if in_func is None:
            wid.surface.blit(desc.surface, desc.rect)
        else:
            desc.move(wid.rect.left, wid.rect.top)
            wid.components.append(desc)

    def close(self):
        self.visual.state = NORMAL_STATE
        self.visual.card = None
        self.visual.update()
        PersonCard.instances.remove(self)
        super().close()


class PageParliament:

    def __init__(self):
        self.loc = None
        self.incumbent = []
        self.radius = int(screen_width / 128) + 1
        self.gap = 2
        self.step = self.radius * 2 + self.gap
        self.mps = []
        self.rect = pygame.Rect((screen_width / 4, display_rect.y + display_rect.height / 6),
                                (screen_width * 2 / 3, display_rect.height * 2 / 3))

        self.display_vote = None
        self.headings = []
        self.vote_reasons = {}
        self.vote_order = None
        self.row_num = None
        self.yea_order = None
        self.nay_order = None
        self.places = {}
        self.select_buttons = []
        pages["parliament"] = self

    def clear(self):
        self.mps.clear()
        self.headings.clear()
        self.display_vote = None
        self.vote_reasons.clear()
        self.vote_order = None
        self.row_num = None
        self.yea_order = None
        self.nay_order = None
        self.places.clear()
        self.select_buttons.clear()

    def open_page(self, loc='gov'):
        self.clear()
        set_up_page("parliament", toolbar=True)
        self.loc = loc
        self.incumbent = [tag for tag, party in logic.parties.items() if party.isincumbent]
        for person in logic.politicians.values():
            card = None
            for p in PersonCard.instances:
                if person == p.person:
                    card = p
                    break
            mp = PersonDisplay((0, 0), self.radius, person, parent=self, card=card)
            self.mps.append(mp)

        self.places = {}
        dist = MENU_WIDTH / 8
        w = MENU_WIDTH * 3 / 4
        spacing = screen_height / 32
        button_size = Button.default_height * 7 / 5
        s_button_size = Button.default_height * 3 / 4

        gov = SelectButton((MENU_WIDTH / 2, display_rect.centery - spacing / 2), (MENU_WIDTH / 2, s_button_size),
              align=BOTTOM, label="Government", parent=self, exclusive=True, deselectable=False)
        gov.callback(self.gov)
        self.places['gov'] = gov
        gov.show()

        provinces = SelectButton((MENU_WIDTH / 2, display_rect.centery + spacing / 2), (MENU_WIDTH / 2, s_button_size),
                    align=TOP, label="Provinces", parent=self, exclusive=True, deselectable=False)
        provinces.callback(self.provincial)
        self.places['province'] = provinces
        provinces.show()

        disp_height = (display_rect.h - (spacing * 5) - (2 * s_button_size)) / 2

        self.set_up_upcoming((dist, gov.rect.top - spacing), (w, disp_height), button_size)
        self.set_up_past((dist, provinces.rect.bottom + spacing), (w, disp_height), button_size)

        self.select_buttons = list(self.places.values())

        for func in self.places[loc].funcs:
            func()
        self.places[loc].state = SELECT_STATE
        self.places[loc].update()
        for mp in self.mps:
            mp.rect.topleft = mp.dest
            mp.show()

    def set_up_upcoming(self, pos, area, button_size):
        vote_subjects = []
        for i in logic.bills:
            bill = logic.bills[i]
            if logic.Bill.stages.index("First Reading") < bill.stage <= logic.Bill.stages.index("Third Reading"):
                vote_subjects.append([bill.id_num, bill.stage])
        order = [logic.vote(logic.bills[subject[0]], logic.bills[subject[0]].stage, hypothetical=True)[1]
                 for subject in vote_subjects]
        proposed = ScrollButtonDisplay(pos, area, total_size=len(order) * button_size, align=BOTTOMLEFT,
                                       button_size=button_size, parent=self)
        self.set_up_vote_display(order, vote_subjects, proposed, button_size, "Upcoming Votes",
                                 "No proposed bills")
        return proposed

    def set_up_past(self, pos, area, button_size):
        order = data.votes
        past = ScrollButtonDisplay(pos, area, total_size=len(order) * button_size, align=TOPLEFT,
                                   button_size=button_size, parent=self)
        vote_subjects = data.vote_subjects
        self.set_up_vote_display(order, vote_subjects, past, button_size, "Previous Votes", "No previous votes")
        return past

    def set_up_vote_display(self, order, vote_subjects, disp, button_size, heading_txt, if_none_txt):
        for i in range(len(order)):
            vote_subject = vote_subjects[-(i + 1)]
            bill = logic.bills[vote_subject[0]]
            vote = order[-(i + 1)]

            b = SelectButton((disp.contain_rect.left, disp.contain_rect.top + i * button_size),
                             (disp.contain_rect.w, button_size),
                             parent=disp, exclusive=True, deselectable=False)

            bill_tag = Text("Bill C-" + str(bill.num), (b.rect.left + 8, b.rect.top + 4), align=TOPLEFT,
                            background_colour=b.normal_colour, font_size=int(BASE_FONT_SIZE * 5 / 4))
            b.components.append(bill_tag)

            bill_name = Text(bill.name, bill_tag.rect.bottomleft, align=TOPLEFT, background_colour=b.normal_colour)
            b.components.append(bill_name)

            if vote_subject[1] == 1:
                stage = "2nd reading"
            else:
                stage = "3rd reading"
            bill_stage = Text(stage, bill_name.rect.bottomleft, align=TOPLEFT, background_colour=b.normal_colour)
            b.components.append(bill_stage)

            vote_num = logic.vote_num(vote)
            result = Text("Yea: " + "</-c (0,140,0)/>" + str(vote_num['Yea']) + "</-c d/> " +
                          "Nay: " + "</-c (200,0,0)/>" + str(vote_num['Nay']),
                          bill_stage.rect.bottomleft, align=TOPLEFT, background_colour=b.normal_colour)
            b.components.append(result)

            b.callback(functools.partial(self.move_for_vote, vote))
            b.callback(functools.partial(self.update_loc, vote_subject))
            b.callback(self.deselect_buttons, returns=True)
            self.places[str(bill.id_num) + '-' + str(vote_subject[1])] = b
            disp.select_buttons.append(b)
        if len(order) == 0:
            disp.components.append(Text(if_none_txt, disp.rect.center, background_colour=disp.colour))
        disp.components.extend(disp.select_buttons)
        disp.show()

        heading = Text(heading_txt, (disp.rect.left / 2, disp.rect.centery))
        heading.surface = pygame.transform.rotate(heading.surface, 90)
        x, y = heading.rect.center
        heading.rect = heading.surface.get_rect()
        heading.rect.center = (x, y)
        heading.show()

    def deselect_buttons(self, wid):
        for b in self.select_buttons:
            if b is not wid:
                b.state = NORMAL_STATE
                b.update()

    def update_loc(self, vote_subject):
        self.loc = str(vote_subject[0]) + '-' + str(vote_subject[1])

    def sort_vote(self):
        for side in self.vote_order:
            for party in self.vote_order[side]:
                self.vote_order[side][party] = sorted(self.vote_order[side][party],
                                                      key=lambda p: logic.get_politician(p).seniority)

    def det_rows(self, vote_num):
        if vote_num["Yea"] >= vote_num["Nay"]:
            limiting = vote_num["Yea"]
        else:
            limiting = vote_num["Nay"]
        row_num = 1
        while (self.radius * 2 + self.gap) * toolkit.round_up(limiting / row_num) - self.gap > self.rect.w:
            row_num += 1
        if row_num < 6:
            row_num = 6
        if row_num > 8:
            row_num = 10
        return row_num

    def det_order(self, vote):
        member_order = [[] for _ in range(self.row_num)]
        for party in sorted(logic.get_house_parties(), key=lambda party: len(self.vote_order[vote][party]),
                            reverse=True):
            for row in range(self.row_num):
                columns = int(len(self.vote_order[vote][party]) / self.row_num)
                for col in range(columns):
                    member_order[row].append(self.vote_order[vote][party][col + row * columns])
            for i in range(len(self.vote_order[vote][party]) % self.row_num):
                for row in range(self.row_num):
                    lengths = [len(member_order[row]) for row in range(self.row_num)]
                    if lengths[row] == min(lengths):
                        member_order[row].append(self.vote_order[vote][party]
                                                 [-(len(self.vote_order[vote][party]) % self.row_num - i)])
                        break
        return member_order

    def gov_as_vote(self):
        vote = {"Yea": {}, "Nay": {}}
        for tag, party in logic.parties.items():
            if party.seats > 0:
                vote["Yea"][tag] = []
                vote["Nay"][tag] = []
        for member in logic.politicians.values():
            if member.party.tag in self.incumbent:
                vote["Yea"][member.party.tag].append(member.id_num)
            else:
                vote["Nay"][member.party.tag].append(member.id_num)
        return vote

    def move_for_vote(self, vote):
        self.vote_reasons = {}
        self.vote_order = {}
        for side in vote:
            parties = {}
            for party in vote[side]:
                mps = []
                for mp in vote[side][party]:
                    self.vote_reasons[mp] = vote[side][party][mp]
                    mps.append(mp)
                parties[party] = mps
            self.vote_order[side] = parties
        self.move()
        self.display_vote = self.vote_reasons

        vote_num = logic.vote_num(self.vote_order)
        yea = vote_num['Yea']
        nay = vote_num['Nay']

        favour = Text("For (" + str(yea) + ')',
                      (self.rect.x, self.rect.y + (self.rect.h + self.radius * 5) / 2 + self.row_num * self.step),
                      align=TOPLEFT, font_size=self.radius * 3, appearing=True, default_alpha=faded_text)
        self.headings.append(favour)
        favour.show()

        oppose = Text("Against (" + str(nay) + ')',
                      (self.rect.x, self.rect.y + (self.rect.h - self.radius * 5) / 2 - self.row_num * self.step),
                      align=BOTTOMLEFT, font_size=self.radius * 3, appearing=True, default_alpha=faded_text)
        self.headings.append(oppose)
        oppose.show()

    def gov(self):
        self.loc = 'gov'
        # Turn incumbency into vote format
        self.display_vote = None
        self.vote_order = self.gov_as_vote()
        self.move()

        vote_num = logic.vote_num(self.vote_order)
        government = Text("Government (" + str(vote_num['Yea']) + ')',
                          (self.rect.x, self.rect.y + (self.rect.h + self.radius * 5) / 2 + self.row_num * self.step),
                          align=TOPLEFT, font_size=self.radius * 3, appearing=True, default_alpha=faded_text)
        self.headings.append(government)
        government.show()

        opposition = Text("Opposition (" + str(vote_num['Nay']) + ')',
                          (self.rect.x, self.rect.y + (self.rect.h - self.radius * 5) / 2 - self.row_num * self.step),
                          align=BOTTOMLEFT, font_size=self.radius * 3, appearing=True, default_alpha=faded_text)
        self.headings.append(opposition)
        opposition.show()

    def move(self):
        for heading in self.headings:
            heading.disappearing = True
        self.sort_vote()
        vote_num = logic.vote_num(self.vote_order)
        # Determine number of rows required
        self.row_num = self.det_rows(vote_num)
        # Determine the order of members on each row on each side
        self.yea_order = self.det_order("Yea")
        self.nay_order = self.det_order("Nay")

        all_yeas = []
        for row in self.yea_order:
            all_yeas = all_yeas + row
        all_nays = []
        for row in self.nay_order:
            all_nays = all_nays + row

        all_persons = [show.person for show in self.mps]
        for i in range(len(all_persons)):
            if all_persons[i].id_num not in all_yeas and all_persons[i].id_num not in all_nays:
                self.mps[i].disappearing = True

        for row in range(len(self.yea_order)):
            for col in range(len(self.yea_order[row])):
                x = int(self.rect.x + self.step * col)
                y = int(self.rect.y + (self.rect.h + self.radius * 5) / 2 + self.step * row)
                person = logic.get_politician(self.yea_order[row][col])
                self.set_dest(x, y, person)
        for row in range(len(self.nay_order)):
            for col in range(len(self.nay_order[row])):
                x = int(self.rect.x + self.step * col)
                y = int(self.rect.y + (self.rect.h - self.radius * 5) / 2 - 2 * self.radius - self.step * row)
                person = logic.get_politician(self.nay_order[row][col])
                self.set_dest(x, y, person)

    def provincial(self):
        self.loc = 'province'
        for heading in self.headings:
            heading.disappearing = True
        prov_col = 0
        prov_row = 0
        not_done = list(logic.regions.keys())
        while len(not_done) > 0:
            not_done, prov_col, prov_row = self.provincial_placement(not_done, prov_col, prov_row, new_row=False)
            not_done, prov_col, prov_row = self.provincial_placement(not_done, prov_col, prov_row, new_row=True)

    def provincial_placement(self, provinces, prov_col, prov_row, new_row=False):
        self.display_vote = None
        not_done = []
        for region in provinces:
            done = False
            province = logic.regions[region]
            order = []
            for riding in province.ridings:
                for mp in logic.ridings[riding].mp:
                    order.append(logic.persons[mp])
            max_col = int(self.rect.w / self.step)
            rows, columns = self.det_dimensions(len(order))
            if prov_col + columns > max_col:
                if new_row:
                    prov_col = 0
                    prov_row += 1
                    new_row = False
                else:
                    not_done.append(region)
                    done = True
            if not done:
                name = Text(province.tag + ' (' + str(len(order)) + ')', (self.rect.x + self.step * prov_col,
                                           self.rect.y + (rows + 2) * self.step * prov_row),
                            align=BOTTOMLEFT, appearing=True)
                self.headings.append(name)
                name.show()
                for row in range(rows):
                    for col in range(columns):
                        if col + row * columns < len(order):
                            person = order[col + row * columns]
                            if person is not None:
                                x = int(self.rect.x + self.step * (prov_col + col))
                                y = int(self.rect.y + self.step * row + (rows + 2) * self.step * prov_row)
                                self.set_dest(x, y, person)
                        else:
                            break
                prov_col += columns + 1
        return not_done, prov_col, prov_row

    def det_dimensions(self, num):
        min_columns = 2
        rows = int(self.rect.h / 2 / self.step)
        columns = toolkit.round_up(num / rows)
        if columns < min_columns:
            columns = min_columns
        return rows, columns

    def set_dest(self, x, y, person):
        all_persons = [show.person for show in self.mps]
        if person in all_persons:
            display = self.mps[all_persons.index(person)]
            display.dest = (x, y)
            display.velocity = ((x - display.rect[0]) ** 2 + (y - display.rect[1]) ** 2) ** 0.5 / 120 + 2
        else:
            mp = PersonDisplay((x, y), self.radius, person, parent=self, appearing=True)
            self.mps.append(mp)
            mp.show()


class PageListBase:

    def __init__(self):
        self.x = MENU_WIDTH
        self.w = screen_width - self.x
        self.mid_x = self.w / 2 + self.x
        self.button_disp = None
        self.components = []

    def set_up_title(self, title):
        title = Text(title, (self.x / 2, screen_height / 16 + ToolBar.height),
                     font_size=TITLE_SIZE, align=CENTER)
        title.show()

    def set_up_name(self, name):
        name = Text(name, (self.mid_x, display_rect.top + text_size(TITLE_SIZE)[1]), font_size=TITLE_SIZE, align=TOP)
        self.components.append(name)

    def update(self):
        for tag, button in self.button_disp.button_tags.items():
            if button.state is SELECT_STATE:
                self.display(tag)
                break
        else:
            self.first_page()

    def display(self, tag):
        pass

    def first_page(self):
        pass

    def new_page(self):
        for w in self.components:
            w.hide()
        self.components.clear()

    def find_loc(self, loc):
        if loc is not None:
            self.display(loc)
            b = self.button_disp.button_tags[loc]
            b.state = SELECT_STATE
            b.update()
            while b.encaps is not None:
                b = b.encaps
                b.expand()


class PagePolicy(PageListBase):

    def __init__(self):
        super().__init__()
        self.loc = None
        self.policy = None
        self.policy_pos = None
        self.orig_pos = None
        self.slider = None
        self.reset = None
        self.pos_txt = None
        pages['policy'] = self

    def open_page(self, loc=None):
        set_up_page('policy')
        self.loc = loc
        self.policy = None
        self.policy_pos = None
        self.orig_pos = None
        self.slider = None
        self.reset = None
        self.pos_txt = None
        self.first_page()
        self.set_up_title("Policies")
        self.set_up_list()
        self.find_loc(loc)

    def set_up_list(self):
        order = sorted(data.policies.keys())
        categories = OrderedDict()
        for category in order:
            layer = OrderedDict()
            for policy in data.policies[category]:
                layer[category + '/' + policy] = {"funcs": [self.update], "release_funcs": [self.update],
                                                  "label": policy}
            categories[category] = layer
        x = MENU_WIDTH / 8
        w = MENU_WIDTH * 3 / 4
        labels = {}
        for tag, policy in logic.policies.items():
            labels[policy.area + '/' + tag] = policy.name
        self.button_disp = HierarchyButtonDisplay((x, screen_height / 8 + ToolBar.height),
                                                  (w, screen_height * 3 / 4 - ToolBar.height), categories,
                                                  button_labels=labels)
        self.button_disp.show()

    def first_page(self):
        self.loc = None
        self.new_page()
        msg = Text("No policy selected", (self.mid_x, screen_height / 2), font_size=TITLE_SIZE)
        self.components.append(msg)
        msg.show()

    def display(self, tag):
        self.loc = tag
        self.policy = tag.split('/')[-1]
        self.new_page()
        marg = display_rect.w / 16
        width = screen_width - self.x - 2 * marg
        self.policy_pos = logic.policies[self.policy].current_law
        self.orig_pos = self.policy_pos

        policy = logic.policies[self.policy]
        if policy.name is not None:
            self.set_up_name(policy.name)
        if policy.desc is not None:
            desc = Text("Description:\n" + policy.desc,
                        (self.x + marg, display_rect.top + display_rect.h / 6), width=width,
                        align=TOPLEFT, multiline=True)
            desc_display = ScrollDisplay([desc], desc.rect.topleft, (width, display_rect.h / 6), total_size=desc.rect.h)
            self.components.append(desc_display)
        if policy.effects is not None:
            effects = Text("Effects:\n" + policy.effects,
                           (self.x + marg, display_rect.top + display_rect.h / 3), width=width,
                           align=TOPLEFT, multiline=True)
            effects_display = ScrollDisplay([effects], effects.rect.topleft, (width, display_rect.h / 6),
                                            total_size=effects.rect.h)
            self.components.append(effects_display)
        if policy.desc is None or policy.effects is None:
            msg = Text("Page is work-in-progress", (self.mid_x, screen_height / 2), font_size=24, align=CENTER)
            self.components.append(msg)

        self.slider = Slider((self.mid_x, display_rect.top + display_rect.h * 2 / 3), (width, 20), self,
                             self.policy_pos, minimum=-100, maximum=100)
        self.components.append(self.slider)

        self.pos_txt = Text(str(self.policy_pos), (self.slider.rect.left, self.slider.rect.top - 50), align=TOPLEFT)
        self.components.append(self.pos_txt)

        bottom_h = self.slider.rect.bottom + marg
        self.reset = Button((self.mid_x, bottom_h), align=TOP, label="Reset", parent=self)
        self.reset.callback(self.reset_slider)
        self.components.append(self.reset)

        propose = Button((display_rect.right - display_rect.w / 16, bottom_h),
                         align=TOPRIGHT, label="Draft Changes", parent=self)
        propose.callback(functools.partial(self.draft))
        self.components.append(propose)

        for w in self.components:
            w.show()

    def reset_slider(self):
        self.policy_pos = self.orig_pos
        self.slider.set_value(self.policy_pos)
        self.update_text()

    def draft(self):
        player_id = data.game_state["player"]
        if player_id in logic.cabinet:
            bill_type = 'gov'
        else:
            bill_type = 'member'
        bill = logic.Bill(player_id, {self.policy: self.policy_pos}, bill_type, data.game_state["parliament"])
        pages['bills'].open_page(loc=bill.id_num)

    def update_slider(self):
        if self.slider is not None:
            self.policy_pos = round(self.slider.get_value())
            self.update_text()

    def update_text(self):
        self.pos_txt.update(str(self.policy_pos))


class PageBills(PageListBase):

    def __init__(self):
        super().__init__()
        self.bill = None
        self.loc = None
        self.propose_b = None
        self.progress_disp = None
        pages['bills'] = self

    def open_page(self, loc=None):
        set_up_page('bills')
        self.loc = loc
        self.bill = None
        self.propose_b = None
        self.progress_disp = None

        self.first_page()
        self.set_up_list()
        self.set_up_title("Bills")
        self.find_loc(loc)

    def set_up_list(self):
        x = MENU_WIDTH / 8
        w = MENU_WIDTH * 3 / 4
        button_size = screen_height / 9
        contents = sorted(list(logic.bills.values()), key=lambda bill: bill.id_num, reverse=True)
        self.button_disp = \
            ScrollButtonDisplay((x, screen_height / 8 + ToolBar.height), (w, screen_height * 3 / 4 - ToolBar.height),
            total_size=len(contents) * button_size, button_size=button_size, parent=self)
        self.button_disp.button_tags = {}
        for i, bill in enumerate(contents):
            b = SelectButton((self.button_disp.contain_rect.x, self.button_disp.contain_rect.y + i * button_size),
                             (self.button_disp.contain_rect.w, button_size), parent=self.button_disp)
            name = Text(bill.name, (b.rect.left + 10, b.rect.top + 2), align=TOPLEFT,
                        background_colour=b.normal_colour, parent=b)
            b.components.append(name)
            b.callback(self.update)
            b.release_callback(self.update)
            self.button_disp.select_buttons.append(b)
            self.button_disp.button_tags[bill.id_num] = b
        self.button_disp.components.extend(self.button_disp.select_buttons)
        if len(self.button_disp.select_buttons) == 0:
            msg = Text("No proposed bills", self.button_disp.rect.center, background_colour=self.button_disp.colour,
                       parent=self.button_disp)
            self.button_disp.components.append(msg)
        self.button_disp.show()

    def find_loc(self, loc):
        if loc is not None:
            self.display(loc)
            b = self.button_disp.button_tags[loc]
            b.state = SELECT_STATE
            b.update()

    def display(self, tag):
        self.bill = tag
        self.loc = self.bill
        self.new_page()

        bill = logic.bills[self.bill]
        self.set_up_name(bill.name)

        marg = display_rect.w / 16
        person = logic.get_politician(bill.sponsor)
        if person is None:
            name = str(None)
        else:
            name = person.name
        txt = "Sponsor: " + name
        sponsor = Text(txt, (self.x + marg, display_rect.y + display_rect.h / 6), align=TOPLEFT, parent=self)
        self.components.append(sponsor)

        txt = "Stage: " + logic.Bill.stages[bill.stage]
        stage = Text(txt, sponsor.rect.bottomleft, align=TOPLEFT, parent=self)
        self.components.append(stage)

        size = 100
        pos = stage.rect.bottomleft
        y = pos[1]
        contents = []
        for prov in bill.provisions:
            contents.append(self.show_provision(prov, bill.provisions[prov], (pos[0], y), (self.w, size)))
            y += size
        provision_display = ScrollDisplay(contents, pos, (self.w, display_rect.h * 2 / 3),
                                          total_size=len(bill.provisions) * size, parent=self)
        for c in contents:
            c.parent = provision_display
        self.components.append(provision_display)

        self.propose_b = Button((display_rect.right - display_rect.w / 16, display_rect.bottom - display_rect.h / 16),
                         align=BOTTOMRIGHT, label="Progress", parent=self)
        self.propose_b.callback(functools.partial(self.advance_bill, bill))
        self.components.append(self.propose_b)
        self.progress_check()

        self.progress_disp = BillProgress(self.bill,
                                          (self.propose_b.rect.centerx, self.propose_b.rect.top - display_rect.h / 16),
                                          align=BOTTOM, parent=self)
        self.components.append(self.progress_disp)

        for w in self.components:
            w.show()

    def advance_bill(self, bill):
        bill.advance()
        self.progress_check()

    def progress_check(self):
        bill = logic.bills[self.bill]
        if bill.in_queue():
            self.propose_b.disable()
            self.propose_b.set_tooltip("Bill is already on the agenda")
        elif logic.Bill.stages[bill.stage] == "Passed":
            self.propose_b.disable()
            self.propose_b.set_tooltip("Bill has already been passed")
        elif bill.dead:
            self.propose_b.disable()
            self.propose_b.set_tooltip("Bill is dead and may not be advanced in this session")
        else:
            self.propose_b.enable()
            self.propose_b.set_tooltip()

    @staticmethod
    def show_provision(prov, policy_pos, pos, size):
        txt = logic.policies[prov].name + ': ' + str(policy_pos) + '\n' + \
              'Current: ' + str(logic.policies[prov].current_law)
        display = Text(txt, pos, align=TOPLEFT, width=size[0], height=size[1], multiline=True)
        return display

    def first_page(self):
        self.loc = None
        self.new_page()
        msg = Text("No bill selected", (self.mid_x, screen_height / 2), font_size=TITLE_SIZE)
        self.components.append(msg)
        msg.show()


class BillProgress(Widget):

    def __init__(self, bill, pos, align=TOPLEFT, parent=None):
        self.stage = logic.bills[bill].stage
        width = display_rect.w / 32
        height = display_rect.h / 2
        area = (width, height)
        super().__init__(pos, area, align=align, parent=parent)
        self.surface.set_colorkey(white)
        self.surface.fill(white)
        rod = pygame.Rect((0, 0), (self.rect.w / 4, self.rect.h * 3 / 4))
        rod.center = (width / 2, height / 2)
        pygame.draw.rect(self.surface, grey, rod)

        num = len(logic.Bill.stages) - 1
        stagger = rod.height / (num - 1)
        r = int(width / 4)
        r2 = int(r * 2 / 3)
        if r2 < 1:
            r2 = r
        for i in range(num):
            x = rod.centerx
            y = round(rod.bottom - stagger * i)
            if i < self.stage:
                colour = green
            elif i == self.stage:
                colour = (255, 255, 0)
            else:
                colour = (255, 0, 0)
            pygame.gfxdraw.aacircle(self.surface, x, y, r, grey)
            pygame.gfxdraw.filled_circle(self.surface, x, y, r, grey)
            pygame.gfxdraw.aacircle(self.surface, x, y, r2, colour)
            pygame.gfxdraw.filled_circle(self.surface, x, y, r2, colour)
            text = Text(logic.Bill.stages[i], (self.rect.x + x - r * 2, self.rect.y + y), align=RIGHT)
            self.extensions.append(text)


class PageStatistics(PageListBase):

    parameters = {
        "party_support": {"x_min": None, "x_max": None, "y_min": 0, "y_max": None,
                          "y_title": "Support (%)", "leader": True, "time": True}
    }

    def __init__(self):
        super().__init__()
        self.loc = None
        pages['data'] = self

    def open_page(self, loc="party_support/national"):
        set_up_page('data')
        self.loc = loc
        self.set_up_title("Statistics")
        self.set_up_list()
        self.find_loc(loc)

    def display(self, tag):
        self.loc = tag
        self.new_page()

        split_tag = tag.split('/')
        for i in range(len(split_tag) - 2, -1, -1):
            if split_tag[0] in PageStatistics.parameters:
                kwargs = PageStatistics.parameters[split_tag[0]]
                break
        else:
            kwargs = {}
        try:
            title = logic.regions[split_tag[-1]].name + " Party Support"
        except KeyError:
            title = toolkit.entitle(split_tag[-1] + ' ' + split_tag[0])
        graph = GraphDisplay((screen_width / 4, ToolBar.height), (screen_width * 3 / 4, screen_height - ToolBar.height),
                data.opinion_polls[split_tag[0]][split_tag[1]], title=title, colours=data.colours,
                initial_date=data.default_game_state["date"], step=data.settings['turn_length'], **kwargs)
        self.components.append(graph)

        for w in self.components:
            w.show()

    def set_up_list(self):
        # order = sorted(data.opinion_polls.keys())
        categories = OrderedDict()
        layer = OrderedDict()
        labels = {}
        for region in sorted(list(data.opinion_polls["party_support"].keys()), key=logic.get_population, reverse=True):
            tag = "party_support" + '/' + region
            layer[tag] = {"funcs": [self.update], "label": region}
            try:
                labels[tag] = logic.regions[region].name
            except KeyError:
                pass
        categories["party_support"] = layer
        x = MENU_WIDTH / 8
        w = MENU_WIDTH * 3 / 4
        self.button_disp = HierarchyButtonDisplay(
            (x, screen_height / 8 + ToolBar.height), (w, screen_height * 3 / 4 - ToolBar.height), categories,
            deselect=False, button_labels=labels)
        self.button_disp.show()


class PageRidings(PageListBase):

    def __init__(self):
        super().__init__()
        self.loc = None
        self.set_up_list()
        pages['ridings'] = self

    def open_page(self, loc=None):
        set_up_page('ridings')
        self.loc = loc
        self.set_up_title("Electoral Districts")
        self.find_loc(loc)
        self.button_disp.show()

    def set_up_list(self):
        categories = OrderedDict()
        labels = {}
        for region in sorted(list(logic.regions.keys()), key=logic.get_population, reverse=True):
            layer = OrderedDict()
            for riding in logic.regions[region].ridings:
                tag = region + '/' + riding
                layer[tag] = {"funcs": [self.update], "label": riding}
                labels[tag] = riding
            labels[region] = logic.regions[region].name
            categories[region] = layer
        x = MENU_WIDTH / 8
        w = MENU_WIDTH * 3 / 4
        self.button_disp = HierarchyButtonDisplay(
            (x, screen_height / 8 + ToolBar.height), (w, screen_height * 3 / 4 - ToolBar.height), categories,
            deselect=False, button_labels=labels)


class PageTitle:

    def __init__(self):
        self.title = None
        pages['title'] = self

    def open_page(self):
        set_up_page("title", toolbar=False)

        self.title = Text(data.game_title, (screen_width / 2, screen_height / 4),
                          font_size=screen_height // 8, align=CENTER)
        self.title.show()

        buttons = ["new game", "load", "credits", "quit"]
        button_functions = {
            "new game": functools.partial(LoadingScreen, set_up_new_game,
                                          threading.Thread(target=logic.init_game, daemon=True)),
            "load": LoadPopUp,
            "credits": make_credits_pop_up,
            "quit": terminate
        }
        for i, button in enumerate(buttons):
            b = Button((screen_width / 2, screen_height / 4 * 2 + i * Button.default_height * 3 / 2),
                       align=CENTER, label=toolkit.entitle(button))
            if button_functions[button] is not None:
                b.callback(button_functions[button])
            b.show()
        Music.channel.show_widget(screen_width / 4, screen_height / 2)


# class PageSelection:
#
#     def __init__(self):
#         set_up_page("selection", toolbar=False)
#         self.display = PartiesButtonDisplay((screen_width / 4, screen_height * 2 / 5),
#                        (screen_width / 3, screen_height * 2 / 3), logic.parties, align=CENTER)
#         self.display.show()
#         select_button = Button((screen_width / 4, screen_height * 7 / 8),
#                                align=CENTER, label="Select")
#         select_button.callback(self.set_up)
#         select_button.show()
#
#     def set_up(self):
#         for b in self.display.components:
#             if b.state is SELECT_STATE:
#                 set_up_first_page()
#                 break


class PageSettings:

    def __init__(self):
        self.title = None
        pages['settings'] = self

    def open_page(self):
        set_up_page("settings")
        self.title = Text("Settings", (screen_width / 2, screen_height / 8 + ToolBar.instance.rect.h), TITLE_SIZE)
        self.title.show()
        buttons = ["resume", "save", "load", "credits", "menu", "quit"]
        button_functions = {
            "resume": call_last_page,
            "save": SavePopUp,
            "load": LoadPopUp,
            "credits": make_credits_pop_up,
            "menu": return_to_menu,
            "quit": terminate
        }
        button_labels = {
            "resume": "Resume",
            "save": "Save",
            "load": "Load Save",
            "credits": "Credits",
            "menu": "Return to Menu",
            "quit": "Quit",
            "new game": "New Game",
        }
        for i, button in enumerate(buttons):
            b = Button((screen_width / 2, screen_height / 8 * 2 + ToolBar.instance.rect.h + i *
                        Button.default_height * 3 / 2),
                       align=CENTER, label=button_labels[button])
            if button_functions[button] is not None:
                b.callback(button_functions[button])
            b.show()
        Music.channel.show_widget(screen_width / 4, screen_height / 2)


class PageWIP:

    def __init__(self, page):
        self.loc = None
        self.page = page
        pages[page] = self

    def open_page(self, toolbar=True, loc=None):
        set_up_page(self.page, toolbar=toolbar)
        self.loc = loc
        msg = Text("Page is Work-in-Progress", screen_center, TITLE_SIZE)
        msg.show()


class PartyCard(Widget):
    area = (screen_width / 3, screen_height / 2)
    pos = (screen_width, 0)
    align = TOPRIGHT
    instance = None

    def __init__(self, party):
        self.party_tag = party
        self.party = logic.parties[self.party_tag]
        self.name = self.party.name
        self.seats = self.party.seats
        self.colour = data.colours[self.party_tag]

        # self.support = support
        # self.leader = leader
        # self.ideology = ideology
        # self.desc = desc

        super().__init__(self.pos, self.area, align=self.align)
        self.surface.fill(light_grey)

        self.components.append(Text(self.name, (self.rect.x + self.rect.w / 10, self.rect.y + self.rect.h / 10),
                                    align=TOPLEFT))
        PartyCard.instance = self
        self.show()


class ToolBar(Widget):
    instance = None

    width = screen_width
    height = screen_height / 12
    unit_size = height * 2 / 3

    def __init__(self):
        super().__init__((0, 0), (self.width, self.height), default_alpha=255)
        if data.settings["graphics"] == 0:
            self.surface.fill(light_grey)
        elif data.settings["graphics"] == 1:
            self.surface.fill(black)
            self.surface.set_alpha(32)

        self.components = []
        self.select_buttons = []

        self.utilities = ["parliament", "policy", "bills", "cabinet", "budget", "data", "parties", "promises",
                          "ridings", "ballot", "events", "settings"]
        self.utilities.reverse()

        images = {
            "parliament": "images/parliament.png",
            "data": "images/graph.png",
            "budget": "images/coins.png",
            "policy": "images/scales.png",
            "cabinet": "images/cabinet.png",
            "list": "images/list.png",
            "ballot": "images/ballot.png",
            "settings": "images/settings.png",
            "parties": "images/hierarchy.png",
            "promises": "images/promise.png",
            "events": "images/event.png",
            "bills": "images/policy.png",
            "ridings": "images/map.png"
        }

        tooltips = {
            "parliament": "House of Commons",
            "data": "Statistics",
            "budget": "Public Finances",
            "policy": "Laws",
            "cabinet": "Cabinet",
            "list": "Persons",
            "parties": "Political Parties",
            "ballot": "Elections",
            "settings": "Settings",
            "promises": "Promises",
            "events": "Events",
            "bills": "Drafted Legislation",
            "ridings": "Electoral Districts"
        }

        self.back_button = Button((3 / 2 * self.unit_size, self.height / 2), (self.unit_size, self.unit_size),
                                  align=CENTER, parent=self)
        img = Image(self.back_button.rect.center,
                    (self.back_button.rect.width * 3 / 4, self.back_button.rect.height * 3 / 4),
                    "images/arrow.png")
        img.surface = pygame.transform.rotate(img.surface, 270)
        self.back_button.components.append(img)
        self.back_button.callback(call_last_page)
        self.back_button.set_tooltip("Return to previous page")
        self.components.append(self.back_button)

        self.forw_button = Button((3 * self.unit_size, self.height / 2), (self.unit_size, self.unit_size), align=CENTER,
                           parent=self)
        img = Image(self.forw_button.rect.center,
                    (self.forw_button.rect.width * 3 / 4, self.forw_button.rect.height * 3 / 4),
                    "images/arrow.png")
        img.surface = pygame.transform.rotate(img.surface, 90)
        self.forw_button.components.append(img)
        self.forw_button.callback(call_next_page)
        self.forw_button.set_tooltip("Return to next page")
        self.components.append(self.forw_button)

        self.turn_txt = Text("Turn: " + str(data.game_state["turn"]),
                             (9 / 2 * self.unit_size, self.forw_button.rect.top),
                             int(BASE_FONT_SIZE * 1.5), background_colour=light_grey, parent=self, align=TOPLEFT)
        self.components.append(self.turn_txt)

        self.date_txt = Text(data.game_state["date"].__repr__(),
                             (self.turn_txt.rect.left, self.forw_button.rect.bottom),
                             align=BOTTOMLEFT, parent=self, background_colour=light_grey,
                             font_size=int(BASE_FONT_SIZE * 1.2))
        self.components.append(self.date_txt)

        self.turn_button = Button((self.width - 3 / 2 * self.unit_size, self.height / 2),
                                  (self.unit_size, self.unit_size), align=CENTER, parent=self)
        img = Image(self.turn_button.rect.center, (self.turn_button.rect.width, self.turn_button.rect.height),
                    "images/forward.png")
        self.turn_button.components.append(img)
        self.turn_button.callback(functools.partial(LoadingScreen, end_turn,
                                  threading.Thread(target=logic.end_turn, daemon=True)))
        self.turn_button.set_tooltip("End Turn")
        self.components.append(self.turn_button)

        for i in range(len(self.utilities)):
            utility = self.utilities[i]
            b = SelectButton((self.width - 3 / 2 * self.unit_size * (i + 2), self.height / 2),
               (self.unit_size, self.unit_size),
               align=CENTER, parent=self, deselectable=False)
            img = Image(b.rect.center, (b.rect.width * 3 / 4, b.rect.height * 3 / 4), images[utility])
            b.components.append(img)
            b.callback(functools.partial(get_page, utility))
            b.set_tooltip(tooltips[utility])
            self.select_buttons.append(b)
        self.components.extend(self.select_buttons)

    def on_page(self):
        for i, b in enumerate(self.select_buttons):
            if current_page == self.utilities[i]:
                b.state = SELECT_STATE
                b.update()
                for other in self.select_buttons:
                    if other is not b and other.state == SELECT_STATE:
                        other.state = NORMAL_STATE
                        other.update()
                break
        self.update()

    def update(self):
        if page_index == -1 and self.forw_button.state is not DISABLE_STATE:
            self.forw_button.disable()
        elif page_index != -1:
            self.forw_button.enable()
        if abs(page_index) == len(data.page_history) and self.back_button.state is not DISABLE_STATE:
            self.back_button.disable()
        elif abs(page_index) != len(data.page_history):
            self.back_button.enable()

    def end_turn(self):
        self.turn_txt.update("Turn: " + str(data.game_state["turn"]))
        self.date_txt.update(data.game_state["date"].__repr__())
        self.turn_button.reset_callbacks()
        self.turn_button.callback(functools.partial(LoadingScreen, end_turn,
                                  threading.Thread(target=logic.end_turn, daemon=True)))


class LoadingScreen(Widget):
    alpha_rate = 20
    instances = []

    def __init__(self, func, thread=None):
        self.func = func
        self.thread = thread
        if self.thread is not None:
            self.thread.start()
        super().__init__((0, 0), (screen_width, screen_height), surface=background.copy(), appearing=True)

        # loading = Text("Loading...", screen_center, 20)
        # self.surface.blit(loading.surface, loading.rect)
        self.show()

    def animate(self):
        if self.surface.get_alpha() == 255:
            if self.thread is not None:
                self.thread.join()
            self.func()
            self.disappearing = True
        super().animate()

    def handle(self, event, mouse):
        return True

    def show(self):
        LoadingScreen.instances.append(self)

    def hide(self):
        LoadingScreen.instances.remove(self)


def make_background():
    surface = pygame.Surface((screen_width, screen_height))
    surface.fill(whitish)
    r = 50
    for y in range(int(screen_height / r)):
        for x in range(int(screen_width / r)):
            pygame.gfxdraw.aacircle(surface, 2 * r * x + -1 ** y * r * y, 2 * r * y, r, white)
            pygame.gfxdraw.filled_circle(surface, 2 * r * x + -1 ** y * r * y, 2 * r * y, r, white)
    return surface


def memoize_page(page, page_index):
    try:
        data.page_history[page_index][1] = pages[page].loc
    except AttributeError:
        pass


def call_last_page():
    global current_page, page_index
    if len(data.page_history) + page_index > 0:
        memoize_page(current_page, page_index)
        widgets.clear()
        page_index -= 1
        current_page = data.page_history[page_index][0]
        get_page(data.page_history[page_index][0], data.page_history[page_index][1])


def call_next_page():
    global current_page, page_index
    if page_index < -1:
        widgets.clear()
        page_index += 1
        current_page = data.page_history[page_index][0]
        get_page(data.page_history[page_index][0], data.page_history[page_index][1])


def set_up_page(set_page, toolbar=True):
    global current_page, page_index
    widgets.clear()
    if current_page != set_page:
        current_page = set_page
        recalled = False
    else:
        recalled = True
    if toolbar:
        if not recalled:
            if len(data.page_history) + page_index > -1:
                memoize_page(data.page_history[page_index][0], page_index)
            if page_index < -1:
                data.page_history = data.page_history[:page_index + 1]
                page_index = -1
            data.page_history.append([current_page, None])
        ToolBar.instance.show()
        ToolBar.instance.on_page()


def make_credits_pop_up():
    width = screen_width / 3
    height = screen_height / 2
    surf = pygame.Surface((width, height))
    surf.fill(black)
    credit = data.credit
    popup = PopUp(screen_center, (width, height), surface=surf, kind="credits", unique=True)
    title = Text("Credits", (popup.rect.center[0], popup.rect.y + popup.rect.height / 16),
                 font_size=TITLE_SIZE, parent=popup, colour=white, background_colour=black,
                 align=TOP)
    popup.components.append(title)
    width = popup.rect.width * 3 / 4
    contents = Text(credit, (popup.rect.center[0], popup.rect.y + popup.rect.height / 8 + text_size(TITLE_SIZE)[1]),
                    width=width, parent=popup, multiline=True, colour=white,
                    background_colour=black, align=TOP, catchable=True)
    display = ScrollDisplay([contents], contents.rect.topleft,
                            (width, popup.rect.height * 3 / 4 - text_size(TITLE_SIZE)[1]),
                            total_size=contents.rect.h, parent=popup)
    popup.components.append(display)


def set_up_new_game():
    set_up_first_page()


def end_turn():
    data.page_history.clear()
    pages['parliament'].open_page()
    ToolBar.instance.end_turn()


def set_up_first_page():
    ToolBar.instance = ToolBar()
    PageParliament()
    PageBills()
    PageStatistics()
    PagePolicy()
    PageRidings()
    pages['parliament'].open_page()


def return_to_menu():
    data.page_history.clear()
    pages['title'].open_page()


def terminate():
    pygame.quit()
    raise SystemExit


def game_start():
    data.init()
    logic.all_data.extend(data.containers)
    set_cursor(0)
    pygame.display.set_caption(data.game_title)
    Music(list(data.soundtrack.keys()))
    PageTitle()
    PageSettings()
    get_page('title')
    game_loop()


def game_loop():
    global background

    def get_all_wids():
        return widgets + PopUp.instances + BaseToolTip.instances + LoadingScreen.instances + [fps]

    background = make_background()

    old_mouse = pygame.mouse.get_pos()
    frame = 0
    t = time.time()
    fps = Text('', (0, 0), align=TOPLEFT)
    while True:
        mouse = pygame.mouse.get_pos()

        # handle events
        all_wids = get_all_wids()
        for event in pygame.event.get():
            try:
                isdebug = data.settings['debug']
            except AttributeError:
                isdebug = True
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE and isdebug):
                terminate()
            elif event.type == pygame.USEREVENT:
                Music.channel.new_track()
            elif event.type == pygame.KEYDOWN and len(text_capture) > 0:
                for i in range(len(text_capture)):
                    if text_capture[-(i + 1)].handle(event, pygame.mouse.get_pos()):
                        break
            else:
                for i in range(len(all_wids)):
                    if len(all_wids) > i:
                        w = all_wids[-(i + 1)]
                        if w.handle(event, mouse):
                            break

        # animate
        all_wids = get_all_wids()
        for widget in all_wids:
            widget.animate()

        # catch mouse
        all_wids = get_all_wids()
        if mouse != old_mouse or Widget.change:
            for i in range(len(all_wids)):
                if len(all_wids) > i:
                    w = all_wids[-(i + 1)]
                    if w.catch(mouse):
                        break
            else:
                for w in set(widgets):
                    w.no_focus()
                if Button.focus is not None:
                    Button.focus.no_focus()
                Widget.new_cursor_type = 0

        # check cursor type
        if Widget.cursor_type != Widget.new_cursor_type:
            Widget.cursor_type = Widget.new_cursor_type
            if Widget.cursor_type == 0:
                set_cursor(0)
            elif Widget.cursor_type == 1:
                set_cursor(1)

        # display
        all_wids = get_all_wids()
        if Widget.change:
            screen.blit(background, (0, 0))
            for widget in all_wids:
                widget.display()
            pygame.display.update()
            Widget.change = False
        old_mouse = mouse

        frame += 1
        nt = time.time()
        dif = nt - t
        if dif >= 1:
            fps.update(str(round(frame / dif)) + ' ' + 'FPS', align=BOTTOMRIGHT, pos=screen_rect.bottomright)
            t = nt
            frame = 0

        clock.tick(60)


def get_page(page, loc=None):
    if page not in pages:
        PageWIP(page)
    if loc is not None:
        pages[page].open_page(loc)
    else:
        pages[page].open_page()


current_page = None
page_index = -1
pages = {}
background = make_background()

if __name__ == "__main__":
    game_loop()
    terminate()
