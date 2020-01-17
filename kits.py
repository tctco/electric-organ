import queue
import threading
import time
from constants import *
from ksMethod import KS


class ScriptGenerator:
    def generate_script(self, original_script, script_name):
        p = path.join(scripts_dir, script_name + ".txt")
        with open(p, 'w') as f:
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


def load_sounds():
    note_dic = {}
    for i in range(9, 122):
        try:
            note_dic[i] = pygame.mixer.Sound(path.join(sound_dir, "{}.wav".format(i)))
        except:
            pass
    return note_dic


class Note:
    def __init__(self, key, start, duration, source):
        self.key = key
        self.start = start
        self.duration = duration
        self.source = source

    def play_note(self):
        chan = pygame.mixer.find_channel()
        chan.play(self.source)
        time.sleep(self.duration / 1000)
        chan.fadeout(200)
        time.sleep(200)

    def play(self):
        th = threading.Thread(target=self.play_note)
        th.setDaemon(True)
        th.start()
