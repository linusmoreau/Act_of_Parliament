from typing import List, Any

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import pygame.gfxdraw
import string
import math
import functools
import date_translator
import ctypes

CENTER = 0
TOPLEFT = 1
RIGHT = 2
TOP = 3
BOTTOM = 4
TOPRIGHT = 5
BOTTOMLEFT = 6
LEFT = 7
BOTTOMRIGHT = 8

NORMAL_STATE = 0
HIGHLIGHT_STATE = 1
PRESS_STATE = 2
SELECT_STATE = 3
DISABLE_STATE = 4

black = (0, 0, 0)
white = (255, 255, 255)
grey = (200, 200, 200)
light_grey = (220, 220, 220)
dark_grey = (180, 180, 180)
whitish = (250, 250, 250)
gold = (212, 175, 55)
green = (20, 200, 20)
red = (255, 80, 80)
colour_ratio = 1.15
faded_text = 150

widgets = []
faded_colours = {}
text_capture = []

os.environ['SDL_VIDEO_WINDOW_POS'] = '1'
pygame.init()
monitor_info = pygame.display.Info()
scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
screen_width = int(monitor_info.current_w / scale_factor)
screen_height = int(monitor_info.current_h / scale_factor)
screen_dimensions = (screen_width, screen_height)
screen_dimension_ratio = screen_width / screen_height
screen_center = (screen_width / 2, screen_height / 2)
screen_rect = pygame.Rect((0, 0), screen_dimensions)
pygame.display.set_icon(pygame.transform.scale((pygame.image.load("images/ballot.png")), (32, 32)))

screen = pygame.display.set_mode(screen_dimensions, pygame.NOFRAME)
clock = pygame.time.Clock()

BUTTON_SCROLL = 1
SCROLL_SPEED = 5
SCROLL_SENSITIVITY = int(screen_height / 64)
SCROLL_RESISTANCE = 0.92
DEFAULT_EDGE = int(screen_width / 128)
FONT_ASPECT = 0.42
TOOLTIP_OFFSET = int(screen_width / 64)
BASE_FONT_SIZE = int(screen_width / 96)
TITLE_SIZE = BASE_FONT_SIZE * 2
SHADOW = round(screen_height / 432) + 1
DEFAULT_FONT = 'mongolianbaiti'


class Widget:
    change = False
    alpha_rate = 5

    def __init__(self, position, area, align=TOPLEFT, surface=None, default_alpha=255, appearing=False, parent=None,
                 catchable=True):
        self.parent = parent
        if surface is None:
            self.surface = pygame.Surface(area)
        else:
            self.surface = surface
        self.default_alpha = default_alpha
        self.fading = appearing
        self.appearing = appearing
        self.catchable = catchable
        self.disappearing = False
        self.rect = self.surface.get_rect()
        self.alignment = align
        self.align(align, position)
        self.contain_rect = self.rect.copy()
        self.components = []
        self.extensions = []
        self.transparency()
        Widget.change = True

    def align(self, align, position):
        if align == CENTER:
            self.rect.center = position
        elif align == TOPLEFT:
            self.rect.topleft = position
        elif align == RIGHT:
            self.rect.midright = position
        elif align == TOP:
            self.rect.midtop = position
        elif align == BOTTOM:
            self.rect.midbottom = position
        elif align == TOPRIGHT:
            self.rect.topright = position
        elif align == BOTTOMLEFT:
            self.rect.bottomleft = position
        elif align == LEFT:
            self.rect.midleft = position
        elif align == BOTTOMRIGHT:
            self.rect.bottomright = position

    def handle(self, event, mouse):
        if self.in_container(mouse):
            for c in self.components:
                c.handle(event, mouse)
        for e in self.components:
            e.handle(event, mouse)
        return False

    def catch(self, mouse):
        if self.catchable:
            if self.on_top(mouse):
                if self.in_container(mouse):
                    for i in range(len(self.components)):
                        if self.components[-(i + 1)].catch(mouse):
                            return True
                for i in range(len(self.extensions)):
                    if self.extensions[-(i + 1)].catch(mouse):
                        return True
                for b in Button.buttons:
                    b.no_focus()
                return True
            else:
                for i in range(len(self.extensions)):
                    if self.extensions[-(i + 1)].catch(mouse):
                        return True
        return False

    def no_focus(self):
        pass

    def get_surface(self):
        return self.surface

    def display(self, container=screen_rect):
        contain = self.contain_rect
        seen = True
        surface = self.get_surface()
        if container is screen_rect or container.contains(self.rect):
            screen.blit(surface, self.rect)
        elif container.colliderect(self.rect):
            visible = pygame.Rect((0, 0), (self.rect.w, self.rect.h))
            temp = self.rect.copy()
            if self.rect.bottom > container.bottom:
                visible.h = container.bottom - self.rect.top
            if self.rect.top < container.top:
                temp.h = temp.bottom - container.top - (self.rect.height - visible.height)
                temp.bottom = self.rect.bottom - (self.rect.height - visible.height)
                visible.h = temp.h
                visible.top = container.top - self.rect.top
            if self.rect.right > container.right:
                visible.width = container.right - self.rect.left
            if self.rect.left < container.left:
                temp.width = temp.right - container.left - (self.rect.width - visible.width)
                temp.right = self.rect.right - (self.rect.width - visible.width)
                visible.width = temp.width
                visible.left = container.left - self.rect.left
            screen.blit(surface, temp, visible)
            contain = pygame.Rect(temp.topleft, visible.size)
        else:
            seen = False
        actual = self.actual_container()
        if actual is not None:
            for e in self.extensions:
                e.display(actual)
        if seen:
            for c in self.components:
                c.display(contain)

    def actual_container(self, container=screen_rect):
        if self.parent is not None:
            try:
                limit = self.parent.contain_rect
            except AttributeError:
                return container
            if limit.contains(container):
                return self.parent.actual_container(container)
            elif container.contains(limit) or container.colliderect(limit):
                if limit.bottom < container.bottom:
                    bottom = limit.bottom
                else:
                    bottom = container.bottom
                if limit.top > container.top:
                    top = limit.top
                else:
                    top = container.top
                if limit.right < container.right:
                    right = limit.right
                else:
                    right = container.right
                if limit.left > container.left:
                    left = limit.left
                else:
                    left = container.left
                return self.parent.actual_container(pygame.Rect((left, top), (right - left, bottom - top)))
            else:
                return None
        else:
            return container

    def animate(self):
        alpha_ratio = self.alpha_rate / self.default_alpha
        if self.appearing:
            self.appear(alpha_ratio)
        elif self.disappearing:
            self.disappear(alpha_ratio)
        for c in self.components + self.extensions:
            c.animate()

    def appear(self, alpha_ratio, first=True):
        Widget.change = True
        alpha_rate = alpha_ratio * self.default_alpha
        if first and self.default_alpha - self.surface.get_alpha() <= alpha_rate:
            self.change_alpha(self.default_alpha)
            for c in self.components + self.extensions:
                c.surface.set_alpha(c.default_alpha)
            self.appearing = False
        else:
            self.change_alpha(self.surface.get_alpha() + alpha_rate)
            for c in self.components + self.extensions:
                c.appear(alpha_ratio, first=False)

    def disappear(self, alpha_ratio, first=True):
        Widget.change = True
        alpha_rate = alpha_ratio * self.default_alpha
        if first and self.surface.get_alpha() - alpha_rate <= 0:
            self.hide()
            del self
            return
        else:
            self.surface.set_alpha(self.surface.get_alpha() - alpha_rate)
            for c in self.components + self.extensions:
                c.disappear(alpha_ratio, first=False)

    def change_alpha(self, alpha):
        self.surface.set_alpha(alpha)

    def transparency(self):
        if self.appearing:
            self.transparent()
        else:
            self.surface.set_alpha(self.default_alpha)

    def transparent(self):
        self.surface.set_alpha(0)
        for c in self.components + self.extensions:
            c.transparent()

    def appeared(self):
        self.surface.set_alpha(self.default_alpha)
        for c in self.components + self.extensions:
            c.appeared()

    def on_top(self, pos):
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.w and self.rect.y <= pos[1] <= self.rect.y + self.rect.h:
            return True
        else:
            return False

    def in_container(self, pos):
        if self.contain_rect.x <= pos[0] <= self.contain_rect.x + self.contain_rect.w and \
                self.contain_rect.y <= pos[1] <= self.contain_rect.y + self.contain_rect.h:
            return True
        else:
            return False

    def draw_borders(self, thickness=1, color=black):
        pygame.draw.rect(self.surface, color, (0, 0, thickness, self.rect.h))
        pygame.draw.rect(self.surface, color, (self.rect.w - thickness, 0, thickness, self.rect.h))
        pygame.draw.rect(self.surface, color, (0, 0, self.rect.w, thickness))
        pygame.draw.rect(self.surface, color, (0, self.rect.h - thickness, self.rect.w, thickness))

    def scroll(self, velocity):
        if velocity != 0:
            Widget.change = True
            for c in self.components:
                c.rect.y -= velocity
                c.contain_rect.y -= velocity
                c.scroll(velocity)

    def show(self):
        widgets.append(self)
        self.transparency()
        Widget.change = True

    def hide(self):
        widgets.remove(self)
        Widget.change = True

    def move_to(self, pos, align=TOPLEFT):
        rel_pos = []
        dif: List[Any] = [self.contain_rect.left - self.rect.left, self.contain_rect.top - self.rect.top]
        for component in self.components + self.extensions:
            rel_pos.append([component.rect.left - self.rect.left, component.rect.top - self.rect.top])
        self.align(align, pos)
        self.contain_rect.left = self.rect.left + dif[0]
        self.contain_rect.top = self.rect.top + dif[1]
        for i, component in enumerate(self.components + self.extensions):
            component.move_to([pos[0] + rel_pos[i][0], pos[1] + rel_pos[i][1]])
        Widget.change = True

    def move(self, x=0, y=0):
        self.rect.x += x
        self.rect.y += y
        self.contain_rect.x += x
        self.contain_rect.y += y
        for c in self.components:
            c.move(x, y)
        for e in self.extensions:
            e.move(x, y)
        Widget.change = True


class Button(Widget):
    buttons = []
    default_height = int(screen_height / 14)
    default_width = int(screen_width / 9)

    def __init__(self, position, area=None, align=TOPLEFT, label=None, label_size=BASE_FONT_SIZE, parent=None,
                 border_thickness=1, border_colour=black, colour=grey, threed=True):
        if area is None:
            area = (self.default_width, self.default_height)
        self.surface = pygame.Surface(area)
        super().__init__(position, area, align, self.surface, parent=parent)
        if border_thickness == 0:
            self.borders = False
        else:
            self.borders = True
        self.border_thickness = border_thickness
        self.border_colour = border_colour

        self.state = NORMAL_STATE

        self.colours = []
        self.normal_colour = colour
        self.press_colour = None
        self.highlight_colour = None

        self.current_label = None
        self.label_size = label_size
        if label is not None:
            self.label(label)
        self.threed = threed
        self.pressed = False
        if self.threed:
            self.shadow = Widget(self.rect.bottomleft, (self.rect.w, SHADOW))
            self.shadow.surface.fill(black)
            self.shadow.surface.set_alpha(200)
            self.extensions.append(self.shadow)

        self.funcs = []
        self.tooltip = None
        self.tooltip_display = None

        self.sheet = Widget(self.rect.topleft, self.rect.size, parent=self, default_alpha=150, catchable=False)
        self.sheet.surface.fill(grey)

        self.update()
        Button.buttons.append(self)

    def handle(self, event, mouse):
        state = self.state
        if self.on_top(mouse):
            if self.state is not DISABLE_STATE:
                for c in self.components:
                    if c.handle(event, mouse):
                        break
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                        self.state = PRESS_STATE
                    elif event.type == pygame.MOUSEBUTTONUP and self.state is PRESS_STATE and \
                            not pygame.mouse.get_pressed()[0]:
                        self.state = HIGHLIGHT_STATE
                        self.call_funcs()
                    if state != self.state:
                        self.update()
            return True
        else:
            return False

    def call_funcs(self):
        for func in self.funcs:
            func()

    def callback(self, func, returns=False):
        if returns:
            self.funcs.append(functools.partial(func, self))
        else:
            self.funcs.append(func)

    def reset_callbacks(self):
        self.funcs.clear()

    def catch(self, mouse):
        if self.on_top(mouse):
            for c in self.components:
                if c.catch(mouse):
                    break
            else:
                if self.tooltip is not None:
                    if self.tooltip_display is None:
                        self.tooltip_display = ToolTip(self.tooltip, (mouse[0], mouse[1] + TOOLTIP_OFFSET))
                        self.tooltip_display.show()
                    else:
                        self.tooltip_display.update(mouse)
                for b in Button.buttons:
                    if b is not self:
                        b.no_focus()
                if self.state is NORMAL_STATE:
                    self.state = HIGHLIGHT_STATE
                    self.update()
            return True
        else:
            return False

    def no_focus(self):
        if self.state in [HIGHLIGHT_STATE, PRESS_STATE]:
            self.state = NORMAL_STATE
            self.update()
        if self.tooltip_display is not None:
            self.tooltip_display.hide()
            self.tooltip_display = None

    def update(self):
        self.update_colours()

        if self.state is DISABLE_STATE:
            self.surface.fill(self.colours[NORMAL_STATE])
        else:
            self.surface.fill(self.colours[self.state])

        if self.state in [PRESS_STATE, SELECT_STATE, DISABLE_STATE] and not self.pressed and self.threed:
            self.move(y=SHADOW)
            self.pressed = True
            self.extensions.remove(self.shadow)
        elif self.state not in [PRESS_STATE, SELECT_STATE] and self.pressed and self.threed:
            self.move(y=-SHADOW)
            self.pressed = False
            self.shadow.rect.topleft = self.rect.bottomleft
            self.extensions.append(self.shadow)

        if self.borders:
            self.draw_borders(self.border_thickness)

        if self.tooltip_display is not None and not self.on_top(pygame.mouse.get_pos()):
            self.tooltip_display.hide()
            self.tooltip_display = None

        Widget.change = True

    def disable(self):
        if self.state is not DISABLE_STATE:
            self.state = DISABLE_STATE
            self.update()
            self.sheet.rect.topleft = self.rect.topleft
            self.components.append(self.sheet)

    def enable(self):
        if self.state is DISABLE_STATE:
            self.state = NORMAL_STATE
            self.update()
            self.components.remove(self.sheet)

    def update_colours(self):
        self.highlight_colour = tuple(map(set_highlight_colour, self.normal_colour))
        self.press_colour = tuple(map(set_press_colour, self.normal_colour))
        self.colours = [self.normal_colour, self.highlight_colour, self.press_colour, self.highlight_colour]

    def label(self, text, size=None, colour=None):
        if size is None:
            size = self.label_size
        else:
            self.label_size = size
        if colour is None:
            colour = black
        if self.current_label is not None:
            self.components.remove(self.current_label)
        self.current_label = Text(text, self.rect.center, font_size=size, colour=colour,
                                  background_colour=self.normal_colour)
        self.components.append(self.current_label)

    def draw_borders(self, thickness=1, color=None):
        if color is None:
            color = self.border_colour
        pygame.draw.rect(self.surface, color, (0, 0, thickness, self.rect.h))
        pygame.draw.rect(self.surface, color, (self.rect.w - thickness, 0, thickness, self.rect.h))
        pygame.draw.rect(self.surface, color, (0, 0, self.rect.w, thickness))
        if not self.threed or self.pressed:
            pygame.draw.rect(self.surface, color, (0, self.rect.h - thickness, self.rect.w, thickness))

    def expand(self):
        self.parent.expand(self)

    def scroll(self, velocity):
        if velocity != 0:
            for c in self.extensions:
                c.rect.y -= velocity
                c.contain_rect.y -= velocity
                c.scroll(velocity)
        super().scroll(velocity)

    def hide(self):
        if self.tooltip_display in BaseToolTip.instances:
            self.tooltip_display.hide()
            self.tooltip_display = None
        super().hide()

    def set_tooltip(self, tip=None):
        self.tooltip = tip


class SelectButton(Button):

    def __init__(self, position, area, align=TOPLEFT, label=None, label_size=BASE_FONT_SIZE,
                 parent=None, border_thickness=1, colour=grey,
                 threed=True, deselectable=True, select_thic=2, exclusive=True):
        super().__init__(position, area, align=align, label=label, label_size=label_size,
                         parent=parent, border_thickness=border_thickness, colour=colour, threed=threed)
        self.deselectable = deselectable
        self.select_thic = select_thic
        self.exclusive = exclusive
        if self.deselectable:
            self.release_funcs = {}

    def handle(self, event, mouse):
        state = self.state
        if self.on_top(mouse):
            if self.state is not DISABLE_STATE:
                for c in self.components:
                    if c.handle(event, mouse):
                        break
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                        if self.state is not SELECT_STATE:
                            if self.parent is not None and self.exclusive:
                                for comp in self.parent.select_buttons:
                                    if comp is not self:
                                        comp.state = NORMAL_STATE
                                        comp.update()
                            self.state = SELECT_STATE
                            self.call_funcs()
                        elif self.deselectable:
                            self.state = HIGHLIGHT_STATE
                            self.call_release_funcs()
                    if self.state is not SELECT_STATE:
                        self.state = HIGHLIGHT_STATE
                    if state != self.state:
                        self.update()
            return True
        else:
            return False

    def update(self):
        super().update()
        if self.state == SELECT_STATE:
            self.draw_borders(thickness=self.select_thic, color=gold)

    def release_callback(self, func, returns=False):
        self.release_funcs[func] = returns

    def call_release_funcs(self):
        for func in self.release_funcs:
            if self.release_funcs[func]:
                func(self)
            else:
                func()


class ScrollBar(Widget):

    def __init__(self, position, area, parent, align=TOPLEFT):
        super().__init__(position, area, align=align, parent=parent)
        self.surface.fill((230, 230, 230))
        self.marg = self.rect.w
        c_range = self.rect.h - 2 * self.marg
        self.scale = c_range / self.parent.total_size
        cursor_height = round(self.scale * self.parent.contain_rect.h)
        min_height = int(screen_height / 48)
        if cursor_height < min_height:
            self.scale = self.scale * (c_range - min_height) / (c_range - cursor_height)
            cursor_height = min_height
        self.cursor = ScrollCursor((self.rect.x, self.rect.y + self.marg), (self.rect.w, cursor_height),
                                   parent=self)
        self.components.append(self.cursor)

        top = Button(self.rect.topleft, (self.marg, self.marg), align=TOPLEFT, threed=False)
        img = Image(top.rect.center, (top.rect.w, top.rect.h), "images/play.png")
        img.surface = pygame.transform.rotate(img.surface, 90)
        top.components.append(img)
        self.top = top
        self.components.append(self.top)

        bottom = Button(self.rect.bottomleft, (self.marg, self.marg), align=BOTTOMLEFT, threed=False)
        img = Image(bottom.rect.center, (bottom.rect.w, bottom.rect.h), "images/play.png")
        img.surface = pygame.transform.rotate(img.surface, 270)
        bottom.components.append(img)
        self.bottom = bottom
        self.components.append(self.bottom)

    def handle(self, event, mouse):
        if self.on_top(mouse):
            for c in self.components:
                if c.handle(event, mouse):
                    break
            return True
        return False

    def catch(self, mouse):
        if self.bottom.state is PRESS_STATE:
            self.cursor.animate(BUTTON_SCROLL)
        elif self.top.state is PRESS_STATE:
            self.cursor.animate(-BUTTON_SCROLL)
        return super().catch(mouse)


class ScrollCursor(Button):

    def __init__(self, position, area, align=TOPLEFT, parent=None, border_thickness=0):
        super().__init__(position, area, align, parent=parent, border_thickness=border_thickness,
                         threed=False)
        self.y_loc = None
        self.subject = self.parent.parent
        self.loc = 0
        self.normal_colour = dark_grey
        self.update()

    def update_colours(self):
        self.highlight_colour = tuple(map(set_press_colour, self.normal_colour))
        self.press_colour = tuple(map(set_press_colour, self.highlight_colour))
        self.colours = [self.normal_colour, self.highlight_colour, self.press_colour, self.highlight_colour]

    def handle(self, event, mouse):
        state = self.state
        if self.on_top(mouse):
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and self.state is not PRESS_STATE:
                self.state = PRESS_STATE
                self.y_loc = mouse[1]
            elif event.type == pygame.MOUSEBUTTONUP and self.state is PRESS_STATE and \
                    not pygame.mouse.get_pressed()[0]:
                self.state = HIGHLIGHT_STATE
            if self.state is NORMAL_STATE:
                self.state = HIGHLIGHT_STATE
            if state != self.state:
                self.update()
            return True
        else:
            if self.state not in [PRESS_STATE, NORMAL_STATE]:
                self.state = NORMAL_STATE
            self.update()
            return False

    def animate(self, move=0):
        mouse = pygame.mouse.get_pos()
        if self.y_loc is not None and self.state is PRESS_STATE:
            if not pygame.mouse.get_pressed()[0]:
                self.state = NORMAL_STATE
                self.update()
            move += (mouse[1] - self.y_loc) / (self.parent.rect.h - 2 * self.parent.marg - self.rect.h) * \
                    (self.subject.total_size - self.subject.contain_rect.h)
            self.subject.scrolling(move)
            self.y_loc = mouse[1]
        elif move != 0:
            self.subject.scrolling(move)
        should = round(self.parent.rect.top + self.parent.scale * self.subject.scroll_pos + self.parent.marg)
        if self.rect.y != should:
            self.rect.y = should
            Widget.change = True
        super().animate()

    def no_focus(self):
        if self.state is HIGHLIGHT_STATE:
            self.state = NORMAL_STATE
            self.update()


class Slider(Widget):

    def __init__(self, pos, area, effect, point, align=CENTER, parent=None, minimum=0, maximum=1, log=False):
        super().__init__(pos, area, align=align, parent=parent)
        self.surface.fill((230, 230, 230))
        self.effect = effect
        self.log = log
        if self.log:
            self.min = math.log10(minimum)
            self.max = math.log10(maximum)
            self.point = math.log10(point)
        else:
            self.min = minimum
            self.max = maximum
            self.point = point
        r = int(self.rect.h / 2)
        self.slider = SliderButton((0, self.rect.centery), r, parent=self)
        self.set_value(point)
        self.components.append(self.slider)

        right = Button(self.rect.topright, (self.rect.h, self.rect.h), align=TOPRIGHT, threed=False)
        img = Image(right.rect.center, right.rect.size, "images/play.png")
        right.components.append(img)
        self.right = right
        self.components.append(self.right)

        left = Button(self.rect.topleft, (self.rect.h, self.rect.h), align=TOPLEFT, threed=False)
        img = Image(left.rect.center, left.rect.size, "images/play.png")
        img.surface = pygame.transform.flip(img.surface, True, False)
        left.components.append(img)
        self.left = left
        self.components.append(self.left)

    def get_value(self):
        v = ((self.slider.loc - self.slider.min) / (self.slider.max - self.slider.min)
             * (self.max - self.min) + self.min)
        if self.log:
            v = 10 ** v
        return v

    def set_value(self, v):
        if self.log:
            v = math.log10(v)
        slider_loc = (v - self.min) / (self.max - self.min) * (self.slider.max - self.slider.min) + self.slider.min
        self.slider.set_loc(slider_loc)

    def handle(self, event, mouse):
        if self.on_top(mouse):
            for c in self.components:
                if c.handle(event, mouse):
                    break
            return True
        return False

    def catch(self, mouse):
        if self.left.state is PRESS_STATE:
            self.slider.animate(-BUTTON_SCROLL)
        elif self.right.state is PRESS_STATE:
            self.slider.animate(BUTTON_SCROLL)
        return super().catch(mouse)


class SliderButton(Button):

    def __init__(self, pos, radius, parent, align=CENTER):
        self.radius = radius
        super().__init__(pos, (self.radius * 2, self.radius * 2), align,
                         parent=parent, threed=False)
        self.mouse_loc = None
        self.loc = self.rect.centerx
        self.min = self.parent.rect.left + self.radius + self.parent.rect.h
        self.max = self.parent.rect.right - self.radius - self.parent.rect.h
        self.normal_colour = gold
        self.surface.set_colorkey(white)
        self.update()

    def handle(self, event, mouse):
        state = self.state
        if self.on_top(mouse):
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and self.state is not PRESS_STATE:
                self.state = PRESS_STATE
                self.mouse_loc = mouse[0]
                self.loc = self.rect.centerx
            elif event.type == pygame.MOUSEBUTTONUP and self.state is PRESS_STATE and \
                    not pygame.mouse.get_pressed()[0]:
                self.state = HIGHLIGHT_STATE
            if self.state is NORMAL_STATE:
                self.state = HIGHLIGHT_STATE
            if state != self.state:
                self.update()
            return True
        else:
            if self.state not in [PRESS_STATE, NORMAL_STATE]:
                self.state = NORMAL_STATE
            self.update()
            return False

    def set_loc(self, loc):
        self.loc = loc
        self.rect.centerx = loc

    def on_top(self, pos):
        if ((pos[0] - self.rect.centerx) ** 2 + (pos[1] - self.rect.centery) ** 2) ** (1 / 2) < self.radius:
            return True
        else:
            return False

    def update(self):
        self.update_colours()
        self.surface.fill(white)
        r = self.radius - 1
        pygame.gfxdraw.filled_circle(self.surface, r, r, r, self.colours[self.state])
        pygame.gfxdraw.aacircle(self.surface, r, r, r, self.colours[self.state])
        if self.tooltip_display is not None and not self.on_top(pygame.mouse.get_pos()):
            self.tooltip_display.hide()
            self.tooltip_display = None
        Widget.change = True

    def animate(self, move=None):
        mouse = pygame.mouse.get_pos()
        if self.mouse_loc is not None and self.state is PRESS_STATE:
            if not pygame.mouse.get_pressed()[0]:
                self.state = NORMAL_STATE
                self.update()
            if self.min - self.radius <= mouse[0] <= self.max + self.radius:
                move = mouse[0] - self.mouse_loc
        if move is not None:
            if self.loc + move > self.max:
                self.loc = self.max
            elif self.loc + move < self.min:
                self.loc = self.min
            else:
                self.loc += move
            self.rect.centerx = self.loc
            self.mouse_loc = mouse[0]
            self.parent.effect.update_slider()
            Widget.change = True
        super().animate()

    def no_focus(self):
        if self.state is HIGHLIGHT_STATE:
            self.state = NORMAL_STATE
            self.update()


class Text(Widget):

    def __init__(self, text, position, font_size=BASE_FONT_SIZE, font=DEFAULT_FONT, align=CENTER,
                 width=None, height=None,
                 appearing=False, colour=black, background_colour=white, solid_background=False, default_alpha=255,
                 multiline=False, justify=LEFT, parent=None, margin=0, catchable=False, bold=False, italic=False,
                 underline=False):
        self.text = text
        self.font_size = font_size
        self.font = font
        self.colour = colour
        self.multiline = multiline
        self.justify = justify
        self.width = width
        self.height = height
        self.background_colour = background_colour
        self.margin = margin
        self.parent = parent
        self.solid_background = solid_background
        self.bold = bold
        self.italic = italic
        self.underline = underline

        self.char_height = text_size(self.font_size, self.font)[1]

        self.style = pygame.font.SysFont(self.font, self.font_size, bold=self.bold, italic=self.italic)
        self.style.set_underline(self.underline)

        self.make_surface()
        area = (self.surface.get_width(), self.surface.get_height())
        super().__init__(position, area, surface=self.surface, align=align, appearing=appearing,
                         default_alpha=default_alpha, parent=parent, catchable=catchable)

    def make_surface(self):
        if not self.multiline or len(self.text) < 1:
            if "</" in self.text and "/>" in self.text:
                surface = self.multisurface_line(self.text)
            else:
                surface = self.style.render(self.text, True, self.colour, self.background_colour)
        else:
            surface = self.multiline_surface(self.width, self.background_colour)
        self.surface = pygame.Surface((surface.get_width() + self.margin * 2,
                                       surface.get_height() + self.margin * 2))
        self.surface.fill(self.background_colour)
        if not self.solid_background:
            self.surface.set_colorkey(self.background_colour)
        self.surface.blit(surface, (self.margin, self.margin))

    def update(self, text=None, align=None, pos=None):
        if text is not None:
            self.text = text
            self.make_surface()
            if align is not None:
                self.rect = self.surface.get_rect()
                self.contain_rect = self.rect.copy()
                self.align(align, pos)
        if not self.multiline or len(self.text) < 1:
            surface = self.style.render(self.text, True, self.colour)
            if type(self.parent).__name__ == "TextInput":
                self.parent.cursor_row = 0
                self.parent.cursor_col = self.parent.cursor_pos
        else:
            surface = self.multiline_surface(self.width, self.background_colour)
        self.rect.width = surface.get_width()
        self.rect.height = surface.get_height()
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        self.surface.fill(self.background_colour)
        if not self.solid_background:
            self.surface.set_colorkey(self.background_colour)
        self.surface.blit(surface, (0, 0))

    def multisurface_line(self, text, **kwargs):
        font = kwargs.get("font", self.font)
        bold = kwargs.get("bold", self.bold)
        italic = kwargs.get("italic", self.italic)
        colour = kwargs.get("colour", self.colour)
        underline = kwargs.get("underline", self.underline)

        command_secs = []
        # command_secs: [[beg, end], [beg, end], [beg, end], etc.]
        for i in range(len(text) - 1):
            if text[i] + text[i + 1] == "</":
                command_secs.append([i])
            elif text[i] + text[i + 1] == "/>":
                command_secs[-1].append(i + 1)

        # Assembling displayed text and commands to effect to the text
        commands = []   # [{'c': (200, 100, 10), 'i': True}, etc.]
        texts = []      # [0: "Hello", 25: "Bob", etc.]
        point = 0
        order = []
        for sec in command_secs:
            if point != sec[0]:
                texts.append(text[point:sec[0]])
                order.append(0)
            point = sec[0]
            sets = text[sec[0] + 2:sec[1] - 1].split('-')
            comm = {}
            for st in sets:
                if st == '':
                    continue
                elem = st.split()
                for i, el in enumerate(elem):
                    elem[i] = el.lower()
                if elem[0] in ["font", 'f']:
                    elem[0] = 'f'
                    if len(elem) < 2 or elem[1] in ["default", 'd'] or elem[1] not in pygame.font.get_fonts():
                        elem[1] = self.font
                elif elem[0] in ["colour", 'c']:
                    elem[0] = 'c'
                    if len(elem) < 2 or elem[1] in ["default", 'd']:
                        elem[1] = self.colour
                    else:
                        str_colour = ''.join(elem[1][1:-1].split()).split(',')
                        elem[1] = tuple([int(val) for val in str_colour])
                elif elem[0] in ["italic", 'i']:
                    elem[0] = 'i'
                    if len(elem) < 2:
                        elem.append(2)
                    elif elem[1] in ["true", 't']:
                        elem[1] = True
                    elif elem[1] in ["false", 'f']:
                        elem[1] = False
                    elif elem[1] in ["default", 'd']:
                        elem[1] = self.italic
                elif elem[0] in ["bold", 'b']:
                    elem[0] = 'b'
                    if len(elem) < 2:
                        elem.append(2)
                    elif elem[1] in ["true", 't']:
                        elem[1] = True
                    elif elem[1] in ["false", 'f']:
                        elem[1] = False
                    elif elem[1] in ["default", 'd']:
                        elem[1] = self.bold
                elif elem[0] in ["underline", 'u']:
                    elem[0] = 'u'
                    if len(elem) < 2:
                        elem.append(2)
                    elif elem[1] in ["true", 't']:
                        elem[1] = True
                    elif elem[1] in ["false", 'f']:
                        elem[1] = False
                    elif elem[1] in ["default", 'd']:
                        elem[1] = self.underline
                comm[elem[0]] = elem[1]
                point = sec[1] + 1
            commands.append(comm)
            order.append(1)
        texts.append(text[point:])
        order.append(0)

        # Building the surfaces based off the above information
        surfaces = []
        widths = []
        text_point = 0
        comm_point = 0
        for t in order:
            if t == 1:
                command = commands[comm_point]
                for prov in command:
                    change = command[prov]
                    if prov == 'f':
                        font = change
                    elif prov == 'c':
                        colour = change
                    elif prov in 'iub':
                        if change == 2:
                            if prov == 'i':
                                change = (italic is False)
                            elif prov == 'u':
                                change = (underline is False)
                            elif prov == 'b':
                                change = (bold is False)
                        if prov == 'i':
                            italic = change
                        elif prov == 'u':
                            underline = change
                        elif prov == 'b':
                            bold = change
                comm_point += 1
            elif t == 0:
                style = pygame.font.SysFont(font, self.font_size, bold=bold, italic=italic)
                style.set_underline(underline)
                surf = style.render(texts[text_point], True, colour, self.background_colour)
                widths.append(surf.get_width())
                surfaces.append(surf)
                text_point += 1

        # Putting the surfaces together into one
        height = surfaces[0].get_height()
        surface = pygame.Surface((sum(widths), height))
        surface.fill(self.background_colour)
        surface.set_colorkey(self.background_colour)
        point = 0
        for i, surf in enumerate(surfaces):
            surface.blit(surf, (point, 0))
            point += widths[i]
        return surface

    def multiline_surface(self, width, background):
        lines = []
        pos = 0
        line = ''
        line_width = 0
        while pos < len(self.text):
            char = self.text[pos]
            if char == '\n':
                lines.append(line)
                line = ''
                line_width = 0
            else:
                line += char
                line_width += text_size(self.font_size, self.font, txt=char)[0]
                if line_width > width:
                    if char == ' ':
                        line = line[:-1]
                    else:
                        for i in range(len(line) - 1, -1, -1):
                            if line[i] == ' ':
                                pos = pos - (len(line) - (i + 1))
                                line = line[:i + 1]
                                break
                        else:
                            line = line[:-1]
                            pos -= 1
                    lines.append(line)
                    line = ''
                    line_width = 0
            pos += 1
        lines.append(line)
        height = len(lines) * self.char_height
        surface = pygame.Surface((width, height))
        surface.fill(background)
        surface.set_colorkey(background)
        for i, line in enumerate(lines):
            subsurface = self.style.render(line, True, self.colour, self.background_colour)
            if self.justify == CENTER:
                dest_x = (surface.get_width() - subsurface.get_width()) / 2
            elif self.justify == RIGHT:
                dest_x = surface.get_width() - subsurface.get_width()
            else:
                dest_x = 0
            surface.blit(subsurface, (dest_x, i * self.char_height))
        return surface


class BaseToolTip(Widget):
    instances = []
    alpha_rate = 10

    def __init__(self, pos, surface, align=LEFT, appearing=True, background_colour=black, tip=True, default_alpha=200):
        area = (surface.get_width(), surface.get_height())
        super().__init__(pos, area, align=align, default_alpha=default_alpha)
        if background_colour is not None:
            self.surface.fill(background_colour)
            self.surface.blit(surface, (0, 0))
        else:
            self.surface = surface
        self.appearing = appearing
        if self.appearing:
            self.surface.set_alpha(0)
        if tip:
            self.update(pygame.mouse.get_pos())

    def update(self, mouse):
        if self.rect.x != mouse[0] or self.rect.y != mouse[1] + TOOLTIP_OFFSET:
            self.rect.x = mouse[0]
            self.rect.y = mouse[1] + TOOLTIP_OFFSET
            if self.rect.right > screen_width:
                self.rect.right = self.rect.left
            if self.rect.bottom > screen_height:
                self.rect.bottom = self.rect.top - 2 * TOOLTIP_OFFSET
            Widget.change = True

    def catch(self, mouse):
        return False

    def show(self):
        BaseToolTip.instances.append(self)
        self.transparency()
        Widget.change = True

    def hide(self):
        BaseToolTip.instances.remove(self)
        Widget.change = True


class ToolTip(BaseToolTip):

    def __init__(self, text, pos, colour=whitish, background_colour=black, align=LEFT, appearing=True, tip=True):
        self.text = text
        if background_colour is None:
            canvas = black
        else:
            canvas = background_colour
        t = Text(self.text, pos, colour=colour, background_colour=canvas, margin=2)
        super().__init__(pos, t.surface, align=align, appearing=appearing, background_colour=background_colour, tip=tip)


class Image(Widget):

    def __init__(self, position, area, img_path, align=CENTER, catchable=False):
        self.img_path = img_path
        self.catchable = catchable

        surface = pygame.image.load(self.img_path)
        width, height = surface.get_size()
        self.cropped_x, self.cropped_y = area

        img_dimension_ratio = width / height
        area_dimension_ratio = self.cropped_x / self.cropped_y
        if img_dimension_ratio >= area_dimension_ratio:
            self.height = self.cropped_y
            self.width = int(self.height / height * width)
        else:
            self.width = self.cropped_x
            self.height = int(self.width / width * height)
        self.dimensions = (int(self.width), int(self.height))

        self.surface = pygame.transform.smoothscale(surface, self.dimensions)
        super().__init__(position, area, align, self.surface, catchable=catchable)


class ScrollDisplayBase(Widget):

    def __init__(self, pos, area, align=TOPLEFT, margin=0, total_size=None, parent=None, catchable=False):
        self.surface = pygame.Surface(area)
        super().__init__(pos, area, align, self.surface, parent=parent, catchable=catchable)
        self.margin = margin
        self.total_size = total_size
        self.contain_rect.top = self.rect.top + self.margin
        self.contain_rect.left = self.rect.left + self.margin
        self.contain_rect.h = self.rect.h - 2 * self.margin
        self.contain_rect.w = self.rect.w - 2 * self.margin

        self.scroll_velocity = 0
        self.scroll_pos = 0
        self.actual_pos = 0
        self.scroll_bar = None
        if self.total_size is not None and self.total_size > self.contain_rect.h:
            self.set_scroll_bar()

    def set_scroll_bar(self):
        scroll_bar = ScrollBar((self.contain_rect.right, self.contain_rect.top),
                               (DEFAULT_EDGE - 1, self.contain_rect.h), self)
        self.extensions.append(scroll_bar)
        self.scroll_bar = scroll_bar

    def handle(self, event, mouse):
        if self.on_top(mouse):
            if self.in_container(mouse):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        self.scroll_up()
                        return True
                    elif event.button == 5:
                        self.scroll_down()
                        return True
                for c in self.components:
                    if c.handle(event, mouse):
                        return True
        for e in self.extensions:
            if e.handle(event, mouse):
                return True
        return False

    def animate(self):
        self.scroll_velocity = self.scroll_velocity * SCROLL_RESISTANCE
        self.scrolling(self.scroll_velocity)
        super().animate()

    def scrolling(self, change):
        self.scroll_pos += change
        v = round(self.scroll_pos - self.actual_pos)
        self.actual_pos += v
        if self.actual_pos < 0:
            self.overshot_up(v)
        elif self.contain_rect.h < self.total_size and self.actual_pos > self.total_size - self.contain_rect.h:
            self.overshot_down(v)
        else:
            self.scroll(v)

    def scroll_up(self):
        if self.actual_pos > 0:
            self.scroll_velocity -= SCROLL_SPEED

    def scroll_down(self):
        if self.actual_pos < self.total_size - self.contain_rect.h:
            self.scroll_velocity += SCROLL_SPEED

    def overshot_up(self, v=0):
        self.scroll(-self.actual_pos + v)
        self.scroll_pos = 0
        self.actual_pos = 0
        self.scroll_velocity = 0

    def overshot_down(self, v=0):
        self.scroll((self.total_size - self.contain_rect.h) - self.actual_pos + v)
        self.scroll_pos = self.total_size - self.contain_rect.h
        self.actual_pos = self.scroll_pos
        self.scroll_velocity = 0


class ScrollButtonDisplay(ScrollDisplayBase):

    def __init__(self, position, area, total_size, align=TOPLEFT, edge=DEFAULT_EDGE, button_size=None,
                 colour=light_grey, parent=None):
        super().__init__(position, area, align, margin=edge, total_size=total_size + SHADOW, parent=parent,
                         catchable=True)
        self.colour = colour
        self.surface.fill(self.colour)
        self.button_size = button_size

        self.select_buttons = []
        self.button_tags = {}

        self.draw_borders()


class ScrollDisplay(ScrollDisplayBase):

    def __init__(self, cont, pos, area, align=TOPLEFT, edge=0, total_size=None, parent=None):
        if total_size is None:
            total_size = cont[0].rect.unionall([c.rect for c in cont]).h
        super().__init__(pos, area, align, margin=edge, total_size=total_size, parent=parent, catchable=True)
        self.components.extend(cont)
        self.surface.fill(white)
        self.surface.set_colorkey(white)


class GraphDisplay(Widget):

    def __init__(self, position, area, dat, x_title=None, y_title=None, align=TOPLEFT,
                 x_min=None, x_max=None, y_min=None, y_max=None, leader=False, title=None, colours=None, time=True,
                 max_y_max=None, turn_length=None, initial_date=None):
        self.time = time
        self.turn_length = turn_length
        self.initial_date = initial_date
        if colours is None:
            colours = {}
        surface = pygame.Surface(area)
        super().__init__(position, area, align, surface)
        self.surface.fill(white)
        self.surface.set_colorkey(white)
        self.dat = dat
        self.x_title = x_title
        self.y_title = y_title
        self.title = title
        self.leader = leader
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.max_y_max = max_y_max
        self.heading_font_size = int(BASE_FONT_SIZE * 3 / 2)
        self.heading_font_width, self.heading_font_height = text_size(self.heading_font_size)
        self.title_font_size = TITLE_SIZE
        self.title_font_width, self.title_font_height = text_size(self.title_font_size)
        self.colours = colours

        self.top_margin = self.rect.h / 12
        self.bottom_margin = self.rect.h / 12
        self.left_margin = self.rect.w / 12
        self.right_margin = self.rect.w / 12
        if self.title is not None:
            self.top_margin += self.title_font_height
        if x_title is not None:
            self.bottom_margin += self.heading_font_height
        if y_title is not None:
            self.left_margin += self.heading_font_height

        self.graph_rect = pygame.Rect((self.left_margin + self.rect.x, self.top_margin + self.rect.y),
                                      (self.rect.w - (self.left_margin + self.right_margin),
                                       self.rect.h - (self.top_margin + self.bottom_margin)))

        # Axis headings and Title
        self.set_titles()

        # Set up mins and maxes
        if self.x_min is None:
            self.x_min = min([min(self.dat[k].keys()) for k in self.dat])
        if self.x_max is None:
            self.x_max = max([max(self.dat[k].keys()) for k in self.dat])  # current date
        x_range = self.x_max - self.x_min

        if self.y_min is None:
            self.y_min = min([min(self.dat[k].values()) for k in self.dat])
        if self.y_max is None:
            self.y_max = max([max(self.dat[k].values()) for k in self.dat])
            if self.max_y_max is not None and self.y_max > self.max_y_max:
                self.y_max = self.max_y_max
        y_range = self.y_max - self.y_min

        # Determine magnitude of difference in the y-variable
        self.y_mag = 0
        size = y_range
        if abs(size) > 10:
            while abs(size) > 10:
                self.y_mag += 1
                size = size / 10.0
        elif abs(size) < 1:
            while abs(size) < 1:
                self.y_mag -= 1
                size = size * 10.0
        self.y_step = 10 ** self.y_mag

        # Update extrema
        if y_min is None:
            self.y_min = (self.y_min / self.y_step - 1) * self.y_step
        if y_max is None:
            self.y_max = (self.y_max / self.y_step + 2) * self.y_step
        y_range = self.y_max - self.y_min

        # Determine scale factors for the sketching of the curves
        if x_range != 0:
            self.x_scale = self.graph_rect.w / x_range
        else:
            self.x_scale = self.graph_rect.w
        if y_range != 0:
            self.y_scale = self.graph_rect.h / y_range
        else:
            self.y_scale = self.graph_rect.h

        # Graph Axes
        self.sketch_axes()

        # Data points and curve connection
        self.sketch_curves()

        self.at_line = None
        self.no_focus()

    def catch(self, mouse):
        if self.on_top(mouse):
            if self.graph_rect.y < mouse[1] < self.graph_rect.y + self.graph_rect.h:
                self.moment(mouse)
                return True
            elif self.at_line in self.components:
                self.components.remove(self.at_line)
                self.at_line = None
            return False

    def no_focus(self):
        # if self.at_line in self.components:
        #     self.components.remove(self.at_line)
        #     self.at_line = None
        self.moment((self.graph_rect.right, 0))
        Widget.change = True

    def handle(self, event, mouse):
        if self.on_top(mouse):
            if self.graph_rect.y < mouse[1] < self.graph_rect.y + self.graph_rect.h:
                return True
        else:
            return False

    def moment(self, pos):
        place = round((pos[0] - self.graph_rect.x) / self.x_scale)
        if place < 0:
            place = 0
        elif place > self.x_max - self.x_min:
            place = self.x_max - self.x_min
        x = self.graph_rect.x + self.x_scale * place
        if self.at_line is None:
            Widget.change = True
            surface = pygame.Surface((1, self.graph_rect.h))
            surface.fill(black)
            self.at_line = Widget((x, self.graph_rect.y), (1, self.graph_rect.h), surface=surface, default_alpha=50)
            self.set_tool_tips(place, x)
            self.components.append(self.at_line)
        else:
            if self.at_line.rect.x != x:
                Widget.change = True
                self.at_line.rect.x = x
                self.at_line.extensions.clear()
                self.set_tool_tips(place, x)
                if self.at_line not in self.components:
                    self.components.append(self.at_line)

    def set_tool_tips(self, place, x):
        x_val = place + self.x_min
        present = []
        for line in self.dat:
            if x_val in self.dat[line]:
                present.append(line)
        order = sorted(present, key=lambda line: self.dat[line][x_val])

        self.show_leader(order, x, x_val)

        if 2 * place + self.x_min <= self.x_max:
            alignment = LEFT
            x_pos = x + 10
        else:
            alignment = RIGHT
            x_pos = x - 10
        tips = []
        for line in order:
            y_pos = self.rect.y + self.rect.h - \
                    ((self.dat[line][x_val] - self.y_min) * self.y_scale + self.bottom_margin)
            if line in self.colours:
                colour = fade_colour(self.colours[line])
            else:
                colour = white
            tip = Text(str(self.dat[line][x_val]), (x_pos, y_pos), align=alignment, colour=black,
                       background_colour=colour, solid_background=True)
            tip.surface.set_alpha(200)
            tips.append(tip)

            r = int(screen_height / 180) + 1
            s = Widget((round(x), round(y_pos)), (2 * r + 1, 2 * r + 1), align=CENTER)
            s.surface.fill(white)
            s.surface.set_colorkey(white)
            pygame.gfxdraw.aacircle(s.surface, r, r, r, colour)
            pygame.gfxdraw.filled_circle(s.surface, r, r, r, colour)
            self.at_line.extensions.append(s)
        while True:
            for i in range(len(tips) - 1):
                dif = tips[i + 1].rect.bottom - tips[i].rect.top
                if dif > 0:
                    tips[i].rect.y += dif / 2
                    tips[i + 1].rect.y -= dif / 2
                    break
            else:
                break
        self.at_line.extensions.extend(tips)

    def show_leader(self, order, x, x_val):
        lead = None
        y_pos = self.rect.y + self.top_margin + self.graph_rect.h / 12
        if self.leader and len(order) >= 2:
            line = order[-1]
            dif = str(round(self.dat[line][x_val] - self.dat[order[-2]][x_val], 2 - self.y_mag))
            if line in self.colours:
                colour = fade_colour(self.colours[line])
            else:
                colour = white
            lead = Text(line + ' +' + dif, (x, y_pos), align=TOP, colour=black, background_colour=colour,
                        solid_background=True, margin=2)
            lead.surface.set_alpha(200)
            self.at_line.extensions.append(lead)
        if self.time:
            txt = date_translator.get_date(x_val * self.turn_length, self.initial_date)
        else:
            txt = str(x_val)
        if lead is not None:
            pos = (lead.rect.centerx, lead.rect.top)
        else:
            pos = (x, y_pos)
        x_pos = Text(txt, pos, align=BOTTOM)
        self.at_line.extensions.append(x_pos)

    def set_titles(self):
        font_size = self.heading_font_size
        if self.x_title is not None:
            heading = Text(self.x_title,
                           (self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h - self.bottom_margin / 4),
                           font_size=font_size)
            self.components.append(heading)
        if self.y_title is not None:
            heading = Text(self.y_title, (self.rect.x + self.left_margin / 2, self.rect.y + self.rect.h / 2),
                           font_size=font_size)
            heading.surface = pygame.transform.rotate(heading.surface, 90)
            x, y = heading.rect.center
            heading.rect = heading.surface.get_rect()
            heading.rect.center = (x, y)
            self.components.append(heading)
        if self.title is not None:
            title = Text(self.title, (self.graph_rect.x, self.rect.y + self.top_margin / 2),
                         font_size=self.title_font_size, align=LEFT)
            self.components.append(title)

    def sketch_axes(self):
        zero_loc = None

        # Draw y-axis
        # pygame.draw.line(self.surface, black,
        #                  (self.x_margin, self.y_margin + self.graph_rect.h),
        #                  (self.x_margin, self.y_margin))

        # Draw y-axis intervals
        font_size = BASE_FONT_SIZE
        num = int((self.y_max - self.y_min) / self.y_step)
        for i in range(num + 1):
            mark = round(self.y_min + self.y_step * i, 4)
            if mark == 0:
                zero_loc = self.graph_rect.bottom - self.graph_rect.h / num * i
            t = Text(str(mark) + ' ',
                     (self.graph_rect.left, self.graph_rect.bottom - self.graph_rect.h / num * i),
                     font_size=font_size, align=RIGHT)
            self.components.append(t)
            pygame.draw.line(self.surface, light_grey,
                             (self.left_margin, self.graph_rect.h + self.top_margin - self.graph_rect.h / num * i),
                             (self.left_margin + self.graph_rect.w,
                              self.graph_rect.h + self.top_margin - self.graph_rect.h / num * i))

        # Draw x-axis
        if self.y_min >= 0:
            zero_loc = self.top_margin + self.graph_rect.h  # Bottom
        elif self.y_max <= 0:
            zero_loc = self.top_margin  # Top
        pygame.draw.line(self.surface, black,
                         (self.left_margin, zero_loc), (self.left_margin + self.graph_rect.w, zero_loc))

        # Draw x-axis intervals
        step = 1
        num = self.x_max - self.x_min
        while num > 12:
            step *= 2
            num = num / 2
        for x in range(int(num) * step, -1, -step):
            if self.y_max <= 0:
                alignment = BOTTOM
            else:
                alignment = TOP
            if self.time:
                txt = date_translator.get_date(self.x_min + x * self.turn_length, self.initial_date)
            else:
                txt = str(self.x_min + x)
            t = Text(txt, (self.graph_rect.left + x * self.x_scale, self.rect.y + zero_loc + 10), font_size=font_size,
                     align=alignment)
            if alignment == BOTTOM:
                t.rect.bottom -= font_size * FONT_ASPECT
            else:
                t.rect.top += font_size * FONT_ASPECT
            self.components.append(t)

    def sketch_curves(self):
        order = sorted(self.dat.keys(), key=lambda line: self.dat[line][max(self.dat[line].keys())])
        for line in order:
            if line in self.colours:
                line_colour = self.colours[line]
            else:
                line_colour = black
            points = []
            for x in self.dat[line].keys():
                point = (int(self.graph_rect.w + self.left_margin - ((self.x_max - x) * self.x_scale)),
                         int(self.rect.h - ((self.dat[line][x] - self.y_min) * self.y_scale + self.bottom_margin)))
                points.append(point)
                # pygame.gfxdraw.aacircle(self.surface, point[0], point[1], 5, line_colour)
                # pygame.gfxdraw.filled_circle(self.surface, point[0], point[1], 5, line_colour)
                # pygame.draw.circle(self.surface, line_colour, point, 0)

            for j in range(len(points) - 1):
                pygame.draw.aaline(self.surface, line_colour, points[j], points[j + 1])

            # pygame.draw.aalines(self.surface, line_colour, False, points)
            # pygame.draw.lines(self.surface, line_colour, False, points, 2)

        self.legend(order)

    def legend(self, order):
        notes = []
        full = Widget((self.graph_rect.right, self.rect.y), (self.right_margin, self.rect.h), align=TOPLEFT)
        full.surface.fill(white)
        full.surface.set_colorkey(white)
        for i, line in enumerate(order):
            if line in self.colours:
                colour = fade_colour(self.colours[line])
            else:
                colour = whitish
            x = 10
            y = full.rect.h - self.bottom_margin
            note = Text(line, (x, y), colour=black, background_colour=colour, solid_background=True, align=LEFT,
                        default_alpha=200, margin=2)
            note.rect.y -= (self.dat[line][max(self.dat[line].keys())] - self.y_min) * self.y_scale
            notes.append(note)
        while True:
            for i in range(len(notes) - 1):
                dif = notes[i + 1].rect.bottom - notes[i].rect.top
                if dif > 0:
                    notes[i].rect.y += dif / 2
                    notes[i + 1].rect.y -= dif / 2
                    break
            else:
                break
        for note in notes:
            full.surface.blit(note.surface, note.rect)
        self.components.append(full)


class TextInput(Widget):

    def __init__(self, text, position, area, font_size=BASE_FONT_SIZE, font="couriernew", align=CENTER,
                 colour=whitish, background_colour=black, default_alpha=255,
                 multiline=False, justify="left"):
        super().__init__(position, area, align=align)
        self.surface.fill(background_colour)
        self.text = text
        self.multiline = multiline
        self.base_surface = self.surface.copy()
        self.cursor_pos = len(self.text)
        self.cursor_row = 0
        self.cursor_col = 0
        self.text_surface = Text(text, position, font_size=font_size, font=font, align=align,
                                 colour=colour, background_colour=background_colour, width=area[0], height=area[1],
                                 default_alpha=default_alpha, multiline=multiline, justify=justify, parent=self,
                                 margin=2)
        self.surface.blit(self.text_surface.surface, (0, 0))
        self.char_width, self.char_height = text_size(font_size, font, 'M')
        self.cursor = Widget((self.contain_rect.x + self.cursor_pos * self.char_width,
                              self.contain_rect.y + self.char_height * (self.cursor_row + 1) - self.char_height * 0.1),
                             (1, self.char_height * 0.8), align=BOTTOM)
        self.displacement = [0, 0]
        self.cursor.surface.fill(colour)
        self.components.append(self.cursor)

    def handle(self, event, mouse):
        if self.on_top(mouse):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self in text_capture:
                    text_capture.remove(self)
                text_capture.append(self)
        if event.type == pygame.KEYDOWN and self in text_capture:
            do_update = True
            if event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    if event.mod == pygame.KMOD_LCTRL or event.mod == pygame.KMOD_RCTRL:
                        if self.text[self.cursor_pos - 1] in string.punctuation:
                            self.move_left()
                        else:
                            while self.cursor_pos > 0 and self.text[self.cursor_pos - 1] in string.whitespace:
                                self.move_left()
                            while self.cursor_pos > 0 and self.text[self.cursor_pos - 1].isalpha():
                                self.move_left()
                    else:
                        self.move_left()
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    if event.mod == pygame.KMOD_LCTRL or event.mod == pygame.KMOD_RCTRL:
                        if self.text[self.cursor_pos] in string.punctuation:
                            self.move_right()
                        else:
                            while self.cursor_pos < len(self.text) and self.text[self.cursor_pos] in string.whitespace:
                                self.move_right()
                            while self.cursor_pos < len(self.text) and self.text[self.cursor_pos].isalpha():
                                self.move_right()
                    else:
                        self.move_right()
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    if event.mod == pygame.KMOD_LCTRL or event.mod == pygame.KMOD_RCTRL:
                        if self.text[self.cursor_pos - 1] in string.punctuation:
                            self.backspace()
                        else:
                            while self.cursor_pos > 0 and self.text[self.cursor_pos - 1] in string.whitespace:
                                self.backspace()
                            while self.cursor_pos > 0 and self.text[self.cursor_pos - 1].isalpha():
                                self.backspace()
                    else:
                        self.backspace()
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    if event.mod == pygame.KMOD_LCTRL or event.mod == pygame.KMOD_RCTRL:
                        if self.text[self.cursor_pos] in string.punctuation:
                            self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                        else:
                            while self.cursor_pos < len(self.text) and self.text[self.cursor_pos] in string.whitespace:
                                self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                            while self.cursor_pos < len(self.text) and self.text[self.cursor_pos].isalpha():
                                self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                    else:
                        self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
            elif event.key == pygame.K_RETURN and self.multiline:
                self.text = self.text[:self.cursor_pos] + '\n' + self.text[self.cursor_pos:]
                self.cursor_pos += 1
            elif event.key == pygame.K_SPACE:
                if self.cursor_pos != 0:
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                    self.cursor_pos += 1
            elif event.unicode in string.printable and event.unicode not in string.whitespace:
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
            else:
                do_update = False
            if do_update:
                self.update()
                Widget.change = True
                return True
        return False

    def update(self):
        self.surface = self.base_surface.copy()
        self.text_surface.text = self.text
        self.text_surface.update()

        if self.multiline:
            if self.text_surface.rect.height > self.contain_rect.height:
                if self.text_surface.rect.height + self.displacement[1] < self.contain_rect.height:
                    self.displacement[1] = self.contain_rect.height - self.text_surface.rect.height
            else:
                self.displacement[1] = 0
        else:
            if self.text_surface.rect.width > self.contain_rect.width:
                if self.text_surface.rect.width + self.displacement[0] < self.contain_rect.width:
                    self.displacement[0] = self.contain_rect.width - self.text_surface.rect.width
            else:
                self.displacement[0] = 0

        self.cursor.rect.x = self.contain_rect.x + self.cursor_col * self.char_width + self.displacement[0]
        self.cursor.rect.bottom = self.contain_rect.y + self.char_height * (self.cursor_row + 1) + self.displacement[
            1] - self.char_height / 10
        if not self.multiline:
            if self.cursor.rect.right > self.contain_rect.x + self.contain_rect.w:
                self.displacement[0] -= (self.cursor.rect.right - (self.contain_rect.x + self.contain_rect.w))
                self.cursor.rect.x = self.contain_rect.x + self.cursor_col * self.char_width + self.displacement[0]
            if self.cursor.rect.left < self.contain_rect.x:
                self.displacement[0] += self.contain_rect.x - self.cursor.rect.left
                self.cursor.rect.x = self.contain_rect.x + self.cursor_col * self.char_width + self.displacement[0]
        else:
            if self.cursor.rect.bottom > self.contain_rect.y + self.contain_rect.h:
                self.displacement[1] -= (self.cursor.rect.bottom - (self.contain_rect.y + self.contain_rect.h))
                self.cursor.rect.bottom = self.contain_rect.y + self.char_height * (self.cursor_row + 1) + \
                    self.displacement[1]
            if self.cursor.rect.top < self.contain_rect.y:
                self.displacement[1] += self.contain_rect.y - self.cursor.rect.top
                self.cursor.rect.bottom = self.contain_rect.y + self.char_height * (self.cursor_row + 1) + \
                    self.displacement[1]

        self.surface.blit(self.text_surface.surface, self.displacement)

    def backspace(self):
        self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
        self.text_surface.text = self.text
        self.cursor_pos -= 1

    def move_right(self):
        self.cursor_pos += 1

    def move_left(self):
        self.cursor_pos -= 1


class PopUp(Widget):
    instances = []
    alpha_rate = 32

    def __init__(self, pos, area, surface=None, close=True, moveable=True, kind=None, unique=False, opacity=220,
                 align=CENTER, appearing=True, borders=True):
        self.kind = kind
        if unique and self.kind is not None and self.kind in [instance.kind for instance in PopUp.instances]:
            for instance in PopUp.instances:
                if instance.kind == self.kind:
                    instance.close()
        self.dragged = False
        self.moveable = moveable
        self.rel = None
        super().__init__(pos, area, surface=surface, align=align, default_alpha=opacity, appearing=appearing)
        if close:
            size = screen_height / 40 + 1
            close_b = Button((self.rect.right, self.rect.top), (size, size), align=TOPRIGHT,
                             colour=(200, 20, 20), border_thickness=2, parent=self, threed=False,
                             border_colour=gold)
            close_b.label('X', colour=whitish, size=int(size * 3 / 4))
            close_b.callback(self.close)
            self.components.append(close_b)
        if borders:
            self.draw_borders(thickness=2, color=gold)
        PopUp.instances.append(self)

    def handle(self, event, mouse):
        if self.dragged:
            x = (mouse[0] - self.rel[0]) - self.rect.x
            y = (mouse[1] - self.rel[1]) - self.rect.y
            if self.rect.left + x < 0:
                x = -self.rect.left
            elif self.rect.right + x > screen_rect.right:
                x = screen_rect.right - self.rect.right
            if self.rect.top + y < 0:
                y = -self.rect.top
            elif self.rect.bottom + y > screen_rect.bottom:
                y = screen_rect.bottom - self.rect.bottom
            self.move(x, y)
        if self.on_top(mouse):
            for c in self.components:
                if c.handle(event, mouse):
                    break
            else:
                if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and not self.dragged and \
                        self.moveable:
                    self.dragged = True
                    if PopUp.instances[-1] != self:
                        PopUp.instances.remove(self)
                        PopUp.instances.append(self)
                        Widget.change = True
                    self.rel = [mouse[0] - self.rect.x, mouse[1] - self.rect.y]
                elif event.type == pygame.MOUSEBUTTONUP and not pygame.mouse.get_pressed()[0] and self.dragged:
                    self.dragged = False
            return True
        else:
            for e in self.extensions:
                if e.handle(event, mouse):
                    return True
            return False

    def close(self):
        if not self.fading:
            PopUp.instances.remove(self)
            del self
        else:
            self.disappearing = True

    def disappear(self, alpha_ratio, first=True):
        Widget.change = True
        alpha_rate = alpha_ratio * self.default_alpha
        if first and self.surface.get_alpha() - alpha_rate <= 0:
            PopUp.instances.remove(self)
            del self
            return
        else:
            self.surface.set_alpha(self.surface.get_alpha() - alpha_rate)
            for c in self.components + self.extensions:
                c.disappear(alpha_ratio, first=False)


def set_highlight_colour(shade):
    shade = shade * colour_ratio
    if shade > 255:
        return 255
    else:
        return shade


def set_press_colour(shade):
    shade = shade / colour_ratio
    if shade < 0:
        return 0
    else:
        return shade


def fade_colour(colour, amount=64):
    if colour not in faded_colours:
        blanket = pygame.Surface((1, 1))
        blanket.fill(whitish)
        blanket.set_alpha(amount)
        paint = pygame.Surface((1, 1))
        paint.fill(colour)
        paint.blit(blanket, (0, 0))
        final = paint.get_at((0, 0))
        faded_colours[colour] = final
    return faded_colours[colour]


text_sizes = {}


def text_size(font_size, font=DEFAULT_FONT, txt='M'):
    if (font, font_size, txt) in text_sizes:
        font_width, font_height = text_sizes[(font, font_size, txt)]
    else:
        font_width, font_height = pygame.font.SysFont(font, font_size).size(txt)
        text_sizes[(font, font_size, txt)] = (font_width, font_height)
    return font_width, font_height


def update():
    for widget in widgets:
        widget.update()
