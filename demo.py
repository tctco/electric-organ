from kits import ScriptGenerator, generate_scale, load_sounds, Note
from inputMethod import TextInput
from threading import Thread
from constants import *
import pygame

pygame.mixer.pre_init(44100, -16, 1, 2048)
pygame.mixer.init()
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Piano Demo")
clock = pygame.time.Clock()

switch_sound = pygame.mixer.Sound(path.join(sound_dir, "switch.ogg"))
key_channel_dic = {}


def draw_text(text, font_size, color, x, y):
    font_name = pygame.font.match_font(UI_FONT)
    font = pygame.font.Font(font_name, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)


class Composer(TextInput):

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
        super().__init__(initial_string,
                         font_size,
                         font_family,
                         antialias,
                         text_color,
                         cursor_color,
                         max_string_length,
                         cursor_blink_interval,
                         keyboard_interval,
                         max_width,
                         max_height)
        self.note_list = []
        self.begin_to_input = False
        self.is_input_paused = False
        self.pause_duration = 0

    def notes(self, key):
        if not self.begin_to_input:
            self.begin_to_input = True
            self.start_time = pygame.time.get_ticks()
        if (len(self.input_string) < self.max_string_length or self.max_string_length == -1) and key in KEY_LIST:
            note = Note(key, pygame.time.get_ticks() - self.start_time - self.pause_duration, None, note_dic[key])
            self.note_list.append(note)

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
                    self.key_status[key][1] %= self.keyboard_interval
        except:
            pass

    def release_key(self, key):
        if key in KEY_LIST:
            for i in range(-1, -len(self.note_list) - 1, -1):
                if self.note_list[i].key == key:
                    note = self.note_list[i]
                    note.duration = pygame.time.get_ticks() - self.start_time - note.start - self.pause_duration
                    self.note_list.sort(key=lambda note: note.start)
                    self.input_string = ""
                    self.cursor_position = 0
                    for note in self.note_list:
                        if note.key == pygame.K_TAB:
                            k = 'tab'
                        else:
                            k = chr(note.key)
                        s = "{},{},{} ".format(k, str(note.start), str(note.duration))
                        self.input_string += s
                        self.cursor_position += len(s)
                    return
        self.key_status[key] = [False, 0]
        self.clock.tick()

    def pause(self):
        if not self.is_input_paused:
            self.is_input_paused = True
            self.paused_time = pygame.time.get_ticks()

    def resume(self):
        if self.is_input_paused and self.cursor_position == len(self.input_string):
            self.is_input_paused = False
            self.pause_duration += pygame.time.get_ticks() - self.paused_time

    def press_key(self, key):
        if key == pygame.K_LEFT:
            self.pause()
            self.left()
        elif key == pygame.K_RIGHT:
            self.pause()
            self.right()
        elif key == pygame.K_BACKSPACE:
            self.pause()
            self.backspace()
        elif key == pygame.K_DELETE:
            self.pause()
            self.delete()
        elif key in KEY_LIST:
            self.resume()
            self.notes(key)
            return
        elif key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.pause()
            self.audition()
            return
        elif pygame.K_0 <= key <= pygame.K_9 or key == pygame.K_COMMA:
            self.pause()
            self.character(key)
        self.key_init(key)

    def audition(self):
        self.clock.tick()
        timer = 0
        index = 0
        while index < len(self.note_list):
            timer += self.clock.tick()
            if timer > self.note_list[index].start:
                self.note_list[index].play()
                index += 1


class UI:
    def __init__(self, selected=1):
        self.selected = selected
        self.piece = DEFAULT_PIECE_NAME
        self.instrument = 1

    def draw(self):
        screen.fill(WHITE)
        background_dir = path.join(img_dir, "background.jpg")
        background_img = pygame.image.load(background_dir)
        background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
        background_img.set_alpha(100)
        background_rect = background_img.get_rect()
        screen.blit(background_img, background_rect)
        if self.instrument == 1:
            instrument = "Guitar"
        elif self.instrument == 0.8:
            instrument = "drum"
        elif self.instrument == 0.99:
            instrument = "Between guitar and drum"

        if self.selected == 1:
            draw_text(">>>{}<<<".format(instrument), UI_FONT_SIZE, BLACK, WIDTH / 2, 100)
        elif self.selected == 2:
            draw_text(">>>Play {}<<<".format(self.piece), UI_FONT_SIZE, BLACK, WIDTH / 2, 200)
        elif self.selected == 3:
            draw_text(">>>Choose a script<<<", UI_FONT_SIZE, BLACK, WIDTH / 2, 300)
        elif self.selected == 4:
            draw_text(">>>I want to compose<<<", UI_FONT_SIZE, BLACK, WIDTH / 2, 400)
        draw_text("{}".format(instrument), UI_FONT_SIZE, BLACK, WIDTH / 2, 100)
        draw_text("Play {}".format(self.piece), UI_FONT_SIZE, BLACK, WIDTH / 2, 200)
        draw_text("Choose a script", UI_FONT_SIZE, BLACK, WIDTH / 2, 300)
        draw_text("I want to compose", UI_FONT_SIZE, BLACK, WIDTH / 2, 400)

    def draw_bar(self, pos, size, borderC, barC, progress):
        pygame.draw.rect(screen, borderC, (*pos, *size), 1)
        inner_pos = (pos[0] + 3, pos[1] + 3)
        inner_size = ((size[0] - 6) * progress, size[1] - 6)
        pygame.draw.rect(screen, barC, (*inner_pos, *inner_size))

    def function(self):
        if self.selected == 1:
            switch_instrument(self.instrument)
            global note_dic
            note_dic = load_sounds()
        elif self.selected == 2:
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
        elif key == pygame.K_RIGHT and self.selected == 1:
            switch_sound.play()
            if self.instrument == 0.8:
                self.instrument = 0.99
            elif self.instrument == 0.99:
                self.instrument = 1
        elif key == pygame.K_LEFT and self.selected == 1:
            switch_sound.play()
            if self.instrument == 1:
                self.instrument = 0.99
            elif self.instrument == 0.99:
                self.instrument = 0.8

        self.draw()

    def compose(self, initial_string):
        composer = Composer(initial_string=initial_string, max_width=480, max_height=580)
        composer.note_list = []
        composer.input_string = ""
        while True:
            composer_surface = composer.get_surface()
            screen.fill(WHITE)
            events = pygame.event.get()
            for event in events:
                self.play_note(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return composer.get_string()
                    elif event.key == pygame.K_ESCAPE:
                        return
            composer.update(events)
            screen.blit(composer_surface, (10, 10))
            pygame.display.flip()

    def edit(self, initial_string):
        textbox = TextInput(initial_string=initial_string, max_width=480, max_height=580)
        textbox.clock.tick()
        while True:
            box_surface = textbox.get_surface()
            screen.fill(WHITE)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return textbox.get_string()
                    elif event.key == pygame.K_ESCAPE:
                        return

            textbox.update(events)
            screen.blit(box_surface, (10, 10))
            pygame.display.flip()

    def get_script(self):
        original_script = self.compose("")
        if not original_script:
            return
        script_name = self.edit("script")
        if not script_name:
            return
        generator = ScriptGenerator()
        try:
            generator.generate_script(original_script, script_name)
            draw_text("Script generated", UI_FONT_SIZE, GREEN, WIDTH / 2, 500)
            pygame.display.flip()
        except Exception as e:
            print(e)
            draw_text("Fail to generate script", UI_FONT_SIZE, RED, WIDTH / 2, 500)
            pygame.display.flip()

    def play_piece(self, piece_name, stop):
        try:
            with open(path.join(scripts_dir, piece_name + ".txt"), "r") as f:
                for line in f.readlines():
                    item_list = line.split()
                    play_list = []
                    print(item_list)
                    for item in item_list:
                        key, start, duration = item.split(',')
                        if key == 'tab':
                            key = 9
                        else:
                            key = ord(key)
                        note = Note(key, int(start), int(duration), note_dic[key])
                        play_list.append(note)
            clock.tick()
            timer = 0
            index = 0
            while index < len(play_list):
                if stop():
                    return
                timer += clock.tick()
                if timer >= play_list[index].start:
                    play_list[index].play()
                    index += 1

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


def switch_instrument(factor):
    scale_generator = generate_scale(factor)
    for progress in range(KEY_NUM):
        screen.fill(BLACK)
        draw_text("generating sounds{}".format('.' * (progress % 3 + 1)), UI_FONT_SIZE, WHITE, WIDTH / 2, HEIGHT * 0.7)
        next(scale_generator)
        ui.draw_bar(BAR_POS, BAR_SIZE, BORDER_COLOR, BAR_COLOR, (progress + 1) / 14)
        pygame.display.flip()


pygame.mixer.set_num_channels(14)
ui = UI(1)
switch_instrument(1)
note_dic = load_sounds()
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
