from constants import *
from kits import Note
import pygame


class TextInput:
    def __init__(
            self,
            initial_string='',
            font_size=20,
            font_family='microsoftyaheimicrosoftyaheiui',
            antialias=True,
            text_color=BLACK,
            cursor_color=BLACK,
            max_string_length=-1,
            cursor_blink_interval=500,
            keyboard_interval=50,
            max_width=480,
            max_height=600,
    ):
        self.input_string = initial_string
        self.text_color = text_color
        self.cursor_color = cursor_color
        self.antialias = antialias
        self.font_size = 35
        self.max_string_length = max_string_length
        self.clock = pygame.time.Clock()
        self.ms_accumulator = 0
        self.cursor_blink_interval = cursor_blink_interval
        self.keyboard_interval = keyboard_interval
        self.max_width = max_width
        self.max_height = max_height

        font_family = pygame.font.match_font(font_family)
        self.font_object = pygame.font.Font(font_family, font_size)

        self.surface = pygame.Surface((max_width, max_height))
        self.cursor_surface = pygame.Surface((int(font_size / 20 + 1), font_size))
        self.cursor_position = len(self.input_string)
        self.cursor_visible = True
        self.cursor_row = self.cursor_column = 0

        self.key_status = {}

    def backspace(self):
        if self.cursor_position > 0:
            self.cursor_visible = True
            self.input_string = self.input_string[:self.cursor_position - 1] + \
                                self.input_string[self.cursor_position:]
            self.cursor_position -= 1

    def delete(self):
        if self.cursor_position < len(self.input_string):
            self.cursor_visible = True
            self.input_string = self.input_string[:self.cursor_position] + \
                                self.input_string[self.cursor_position + 1:]

    def left(self):
        if self.cursor_position > 0:
            self.cursor_visible = True
            self.cursor_position -= 1

    def right(self):
        if self.cursor_position < len(self.input_string):
            self.cursor_visible = True
            self.cursor_position += 1

    def character(self, key):
        if len(self.input_string) < self.max_string_length or self.max_string_length == -1:
            self.input_string = self.input_string[:self.cursor_position] + chr(key) + \
                                self.input_string[self.cursor_position:]
            self.cursor_position += 1

    def status_check(self, key):
        try:
            if self.key_status[key][0]:
                self.key_status[key][1] += self.clock.tick()
                if self.key_status[key][1] > self.keyboard_interval:
                    if key == pygame.K_BACKSPACE:
                        self.backspace()
                    elif key == pygame.K_DELETE:
                        self.delete()
                    elif key == pygame.K_RIGHT:
                        self.right()
                    elif key == pygame.K_LEFT:
                        self.left()
                    elif pygame.K_SPACE <= key <= ord('~'):
                        self.character(key)
                    self.key_status[key][1] %= self.keyboard_interval
        except:
            pass

    def key_init(self, key):
        self.key_status[key] = [True, -200]
        self.clock.tick()

    def press_key(self, key):
        if key == pygame.K_LEFT:
            self.left()
        elif key == pygame.K_RIGHT:
            self.right()
        elif key == pygame.K_BACKSPACE:
            self.backspace()
        elif key == pygame.K_DELETE:
            self.delete()
        elif pygame.K_SPACE <= key <= ord('~'):
            self.character(key)
        self.key_init(key)

    def release_key(self, key):
        self.key_status[key] = [False, 0]
        self.clock.tick()

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.press_key(event.key)
            elif event.type == pygame.KEYUP:
                self.release_key(event.key)

        keys = [item[0] for item in self.key_status.items() if item[1][0]]
        for key in keys:
            self.status_check(key)

        self.render_text()

        self.ms_accumulator += self.clock.tick()
        if self.ms_accumulator > self.cursor_blink_interval:
            self.cursor_visible = not self.cursor_visible
            self.ms_accumulator = 0

        if self.cursor_visible:
            self.surface.blit(self.cursor_surface, (self.cursor_row, self.cursor_column))

    def render_text(self):
        row, column = 0, 0
        self.surface.fill(WHITE)
        for index, ch in enumerate(self.input_string):
            if index == self.cursor_position:
                self.cursor_row = row
                self.cursor_column = column
            if row + self.font_object.size(ch)[0] > self.max_width:
                row = 0
                column += self.font_object.size(ch)[1]

            if column + self.font_object.size(ch)[1] > self.max_height:
                self.max_string_length = index
                self.input_string = self.input_string[:index]
                print(self.input_string)
                return

            self.surface.blit(self.font_object.render(ch, self.antialias, self.text_color), (row, column))
            row += self.font_object.size(ch)[0]

        if len(self.input_string) == self.cursor_position:
            self.cursor_column = column + self.cursor_surface.get_height() / 5
            self.cursor_row = row + self.cursor_surface.get_width() / 3

    def get_surface(self):
        return self.surface

    def get_string(self):
        return self.input_string
