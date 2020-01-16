import pygame
import queue
import threading
import numpy as np
from os import path
import wave
import time

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
pygame.font.init()
KEY_LIST = [pygame.K_TAB,
            pygame.K_q,
            pygame.K_w,
            pygame.K_e,
            pygame.K_r,
            pygame.K_t,
            pygame.K_y,
            pygame.K_u,
            pygame.K_i,
            pygame.K_o,
            pygame.K_p,
            pygame.K_LEFTBRACKET,
            pygame.K_RIGHTBRACKET,
            pygame.K_BACKSLASH]


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
            compose_mode=False
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
        self.compose_mode = compose_mode

        font_family = pygame.font.match_font(font_family)
        self.font_object = pygame.font.Font(font_family, font_size)

        self.surface = pygame.Surface((max_width, max_height))
        self.cursor_surface = pygame.Surface((int(font_size / 20 + 1), font_size))
        self.cursor_position = len(self.input_string)
        self.cursor_visible = True
        self.cursor_row = self.cursor_column = 0

        self.key_status = {}
        self.rest_status = pygame.time.get_ticks()
        self.f_start_input = False
        self.note_status = {}

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
            if key == pygame.K_TAB and self.compose_mode:
                self.input_string = self.input_string[:self.cursor_position] + 'tab' + \
                                    self.input_string[self.cursor_position:]
                self.cursor_position += 3
            else:
                if self.compose_mode and not (pygame.K_0 <= key <= pygame.K_9 or key in KEY_LIST):
                    return
                else:
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
                    elif pygame.K_SPACE <= key <= ord('~') or key in KEY_LIST:
                        if self.compose_mode:
                            return
                        else:
                            self.character(key)
                    self.key_status[key][1] %= self.keyboard_interval
        except:
            pass

    def key_init(self, key):
        if not self.compose_mode:
            self.key_status[key] = [True, -200]
        else:
            self.key_status[key] = [True, 0]
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
        elif pygame.K_SPACE <= key <= ord('~') or key == pygame.K_TAB:
            if self.compose_mode:
                if self.f_start_input and key in KEY_LIST:
                    self.rest_status = pygame.time.get_ticks() - self.rest_status
                    self.input_string = self.input_string[:self.cursor_position] + ',' + str(self.rest_status) \
                                        + ' ' + self.input_string[self.cursor_position:]
                    self.cursor_position += len(',' + str(self.rest_status) + ' ')
                self.note_status[key] = pygame.time.get_ticks()
                self.f_start_input = True
            self.character(key)
        self.key_init(key)
        pygame.event.set_blocked(pygame.KEYDOWN)

    def release_key(self, key):
        if self.compose_mode and key in KEY_LIST:
            self.note_status[key] = pygame.time.get_ticks() - self.note_status[key]
            self.input_string = self.input_string[:self.cursor_position] + ',' + str(self.note_status[key]) \
                                + ' ' + self.input_string[self.cursor_position:]
            self.cursor_position += len(',' + str(self.note_status[key]) + ' ')
            self.rest_status = pygame.time.get_ticks()
            self.input_string = self.input_string[:self.cursor_position] + 'rest' + self.input_string[self.cursor_position:]
            self.cursor_position += len('rest')
        self.key_status[key] = [False, 0]
        self.clock.tick()
        pygame.event.set_allowed(pygame.KEYDOWN)

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


class ScriptGenerator:
    def generate_script(self, original_script, script_name):
        if original_script[-4:] == "rest":
            original_script += ",0"
        with open(script_name + ".txt", 'w') as f:
            f.write(original_script)


class PlayerTh(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.queue = queue.Queue()
        self.start()

    def run(self):
        while True:
            func, *args = self.queue.get()
            func(*args)
            self.queue.task_done()

    def apply_async(self, func_item):
        self.queue.put(func_item)

    def join(self):
        self.queue.join()


if __name__ == '__main__':
    pygame.init()
    text_input = TextInput(font_family="arial")
    screen = pygame.display.set_mode((600, 480))

    while 1:
        screen.fill(WHITE)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()

        text_input.update(events)
        screen.blit(text_input.get_surface(), (10, 10))
        pygame.display.flip()


class KS(object):

    def __init__(self, sample_rate=44100, freq=220.):
        self.sample_rate = sample_rate
        self.period = int(sample_rate / freq)
        self.chunk = np.random.rand(self.period)
        self.chunk = self.chunk - np.mean(self.chunk)
        self.block = self.chunk
        self.total_len = 0
        self.factor = 1

    def set_factor(self, f):
        self.factor = f

    def __buffer(self):
        for i in range(self.period):
            prob = np.random.rand()
            if self.factor >= prob:
                self.chunk[i] = (self.chunk[i - 1] + self.chunk[i]) * 0.5
            else:
                self.chunk[i] = -(self.chunk[i - 1] + self.chunk[i]) * 0.5

    def generator(self, length=500):
        print('Generating...')
        self.block = self.chunk
        self.total_len = length * self.period + len(self.chunk)
        for i in range(length - 1):
            self.__buffer()
            self.block = np.append(self.block, self.chunk)
        self.__convert_to_int16()
        print('Done. %s frames for total.' % self.total_len)
        return self.block

    def __convert_to_int16(self):
        self.block = self.block * (2 ** 16 - 1)
        self.block = self.block.astype(np.int16)

    def save_to_file(self, fname):
        f = wave.open(fname, 'wb')
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(self.sample_rate)
        f.writeframes(self.block)
        f.close()


def generate_pitch():
    ratio = 2 ** (1 / 12)
    note_dic = {}
    for index, key in enumerate(KEY_LIST):
        note_dic[key] = 220 * (ratio ** index)
    return note_dic


def generate_scale(factor=1):
    note_dic = generate_pitch()
    coefficient = 2 ** (1 / 12)
    a = coefficient
    dir = path.join(path.dirname(__file__), "sound")
    pygame.init()
    i = 1
    for key, value in note_dic.items():
        k = KS(44100, value)
        k.set_factor(factor)
        k.generator(int(1000 * a))
        a *= coefficient
        k.save_to_file(path.join(dir, "{}.wav".format(key)))
        yield i
        i += 1

class Note:
    def __init__(self, key, start, end, duration, source):
        self.key = key
        self.start = start
        self.end = end
        self.duration = duration
        self.source = source

    def play_note(self):
        chan = pygame.mixer.find_channel()
        chan.play(self.source)
        time.sleep((self.duration - 200)/ 100)
        chan.fadeout(200)

    def play(self):
        th = threading.Thread(target=self.play_note)
        th.start()



