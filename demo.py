import time
from os import path
import pygame
from kits import TextInput, ScriptGenerator, generate_scale
from threading import Thread

WIDTH = 500
HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BAR_SIZE = (200, 20)
BAR_POS = ((WIDTH - BAR_SIZE[0]) / 2, (HEIGHT - BAR_SIZE[1]) / 2)
BORDER_COLOR = (50, 50, 50)
BAR_COLOR = (0, 128, 0)
DEFAULT_PIECE_NAME = "script"
UI_FONT = "consolas"
UI_FONT_SIZE = 20
KEY_NUM = 14
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

pygame.mixer.pre_init(44100, -16, 1, 2048)
pygame.mixer.init()
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Piano Demo")
clock = pygame.time.Clock()

sound_dir = path.join(path.dirname(__file__), "sound")
img_dir = path.join(path.dirname(__file__), "img")
piano_sound_track_pack = []
switch_sound = pygame.mixer.Sound(path.join(sound_dir, "switch.ogg"))

key_dic = {}


def draw_text(text, font_size, color, x, y):
    font_name = pygame.font.match_font(UI_FONT)
    font = pygame.font.Font(font_name, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)


class UI:
    def __init__(self, selected=1):
        self.selected = selected
        self.piece = DEFAULT_PIECE_NAME

    def draw(self):
        screen.fill(WHITE)
        background_dir = path.join(img_dir, "background.jpg")
        background_img = pygame.image.load(background_dir)
        background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
        background_img.set_alpha(100)
        background_rect = background_img.get_rect()
        screen.blit(background_img, background_rect)
        if self.selected == 1:
            draw_text(">>>Press a to z to play music<<<", UI_FONT_SIZE, BLACK, WIDTH / 2, 100)
        elif self.selected == 2:
            draw_text(">>>Play {}<<<".format(self.piece), UI_FONT_SIZE, BLACK, WIDTH / 2, 200)
        elif self.selected == 3:
            draw_text(">>>Choose a script<<<", UI_FONT_SIZE, BLACK, WIDTH / 2, 300)
        elif self.selected == 4:
            draw_text(">>>I want to compose<<<", UI_FONT_SIZE, BLACK, WIDTH / 2, 400)
        draw_text("Press a to z to play music", UI_FONT_SIZE, BLACK, WIDTH / 2, 100)
        draw_text("Play {}".format(self.piece), UI_FONT_SIZE, BLACK, WIDTH / 2, 200)
        draw_text("Choose a script", UI_FONT_SIZE, BLACK, WIDTH / 2, 300)
        draw_text("I want to compose", UI_FONT_SIZE, BLACK, WIDTH / 2, 400)

    def draw_bar(self, pos, size, borderC, barC, progress):
        pygame.draw.rect(screen, borderC, (*pos, *size), 1)
        innerPos = (pos[0] + 3, pos[1] + 3)
        innerSize = ((size[0] - 6) * progress, size[1] - 6)
        pygame.draw.rect(screen, barC, (*innerPos, *innerSize))

    def function(self):
        if self.selected == 2:
            self.player_stop = False
            player = Thread(target=self.play_piece, args=(self.piece, lambda: self.player_stop))
            player.daemon = True
            player.start()
        elif self.selected == 3:
            self.piece = get_input()
            self.draw()
        elif self.selected == 4:
            self.get_script()

    def key_pressed(self, key):
        self.player_stop = True
        if key == pygame.K_ESCAPE:
            pygame.quit()
        elif self.selected > 1 and key == pygame.K_UP:
            switch_sound.play()
            self.selected -= 1
        elif self.selected < 4 and key == pygame.K_DOWN:
            switch_sound.play()
            self.selected += 1
        elif key == pygame.K_RETURN:
            self.function()
        self.draw()

    def edit(self, initial_string, play=False, compose_mode=False):
        textbox = TextInput(initial_string=initial_string, max_width=480, max_height=580, compose_mode=compose_mode)
        textbox.clock.tick()
        while True:
            box_surface = textbox.get_surface()
            screen.fill(WHITE)
            events = pygame.event.get()
            for event in events:
                if play:
                    self.play_note(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if play:
                        if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                            chan = pygame.mixer.find_channel()
                            line = textbox.get_string()
                            if line[-1] >= '9' or line[-1] < '0':
                                line = line + ',0'
                            item_list = line.split()
                            print(item_list)
                            for item in item_list:
                                note, duration = item.split(',')
                                if note != 'rest':
                                    if note == 'tab':
                                        note = 9
                                    else:
                                        note = ord(note)
                                    chan.queue(note_dic[note])
                                time.sleep(int(duration) / 1000)
                                chan.fadeout(200)
                    if event.key == pygame.K_RETURN:
                        return textbox.get_string()
                    elif event.key == pygame.K_ESCAPE:
                        return

            textbox.update(events)
            screen.blit(box_surface, (10, 10))
            pygame.display.flip()

    def get_script(self):
        original_script = self.edit("do re mi fa so la xi", play=True, compose_mode=True)
        if not original_script:
            return
        script_name = self.edit("new script")
        if not script_name:
            return
        generator = ScriptGenerator()
        try:
            generator.generate_script(original_script, script_name)
            draw_text("Script generated", UI_FONT_SIZE, GREEN, WIDTH / 2, 500)
        except:
            draw_text("Fail to generate script", UI_FONT_SIZE, RED, WIDTH / 2, 500)

    def play_piece(self, piece_name, stop):
        try:
            chan = pygame.mixer.find_channel()
            with open(piece_name + ".txt", "r") as f:
                for line in f.readlines():
                    item_list = line.split()
                    print(item_list)
                    for item in item_list:
                        note, duration = item.split(',')
                        if stop():
                            return
                        if note != 'rest':
                            if note == 'tab':
                                note = 9
                            else:
                                note = ord(note)
                            chan.queue(note_dic[note])
                        time.sleep(int(duration) / 1000)
                        chan.fadeout(int(duration))
        except Exception as e:
            print(e)
            draw_text("Cannot play script!", UI_FONT_SIZE, RED, WIDTH / 2, 500)

    def play_note(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_LIST:
                key_channel_dic[event.key] = pygame.mixer.find_channel()
                key_channel_dic[event.key].play(note_dic[event.key])
        elif event.type == pygame.KEYUP:
            try:
                if event.key in KEY_LIST:
                    key_channel_dic[event.key].fadeout(200)
            except:
                pass


def get_input():
    message = []
    screen.fill(WHITE)
    draw_text("enter the piece you want to play", UI_FONT_SIZE, BLACK, WIDTH / 2, 100)
    while True:
        input_event_list = pygame.event.get()
        for input_event in input_event_list:
            if input_event.type == pygame.QUIT:
                pygame.quit()
            elif input_event.type == pygame.KEYDOWN:
                if pygame.K_SPACE <= input_event.key <= ord('~'):
                    message.append(chr(input_event.key))
                elif input_event.key == pygame.K_BACKSPACE:
                    message.pop()
                elif input_event.key == pygame.K_ESCAPE:
                    return ''
                elif input_event.key == pygame.K_RETURN:
                    return ''.join(message)
            text = ''.join(message)
            screen.fill(WHITE)
            draw_text(text, UI_FONT_SIZE, BLACK, WIDTH / 2, HEIGHT / 2)
            draw_text("enter the piece you want to play", UI_FONT_SIZE, BLACK, WIDTH / 2, 100)
            pygame.display.flip()


def load_sound_pack():
    for i in range(0, 68):
        piano_sound_track_pack.append(pygame.mixer.Sound(path.join(sound_dir, "note ({}).wav".format(i + 1))))


def generate_pitch():
    note_dic = {}
    for i in range(9, 122):
        try:
            note_dic[i] = pygame.mixer.Sound(path.join(sound_dir, "{}.wav".format(i)))
        except:
            pass
    return note_dic


note_dic = generate_pitch()
key_channel_dic = {}


def main():
    load_sound_pack()
    pygame.mixer.set_num_channels(14)
    ui = UI(1)
    # scale_generator = generate_scale()
    # for progress in range(KEY_NUM):
    #     next(scale_generator)
    #     ui.draw_bar(BAR_POS, BAR_SIZE, BORDER_COLOR, BAR_COLOR, (progress + 1) / 14)
    #     pygame.display.flip()

    ui.draw()
    while 1:
        clock.tick(100)
        event_list = pygame.event.get()
        for event in event_list:
            if ui.selected == 1 or ui.selected == 3:
                ui.play_note(event)
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                ui.key_pressed(event.key)
        pygame.display.flip()


if __name__ == '__main__':
    main()
