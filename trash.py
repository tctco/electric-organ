class KS(object):

    def __init__(self, sample_rate=44100, freq=220.):
        self.sample_rate = sample_rate
        self.period = int(sample_rate / freq)
        self.chunk = np.random.rand(self.period)
        self.chunk = self.chunk - np.mean(self.chunk)
        self.block = self.chunk
        self.can_gen = True
        self.can_play = True
        self.factor = 1
        self.playing = False

    def set_factor(self, f):
        self.factor = f

    def __buffer(self):
        for i in range(self.period):
            prob = np.random.rand()
            if self.factor >= prob:
                self.chunk[i] = (self.chunk[i - 1] + self.chunk[i]) * 0.5
            else:
                self.chunk[i] = -(self.chunk[i - 1] + self.chunk[i]) * 0.5

    def gen(self):
        self.block = self.chunk
        while self.can_gen:
            self.__buffer()
            self.block = np.append(self.block, self.chunk)

    @staticmethod
    def __convert(x):
        x = x * (2 ** 16 - 1)
        x = x.astype(np.int16)
        return x

    def __counter(self):
        c = 0
        while True:
            yield c
            c = c + 1

    def player_init(self):
        self.player_buffer = 1024
        self.__player_counter = self.__counter()

    def __player_callback(self, in_data, frame_count, time_info, status):
        c = next(self.__player_counter)
        rdata = self.block[c * self.player_buffer:(c + 1) * self.player_buffer]
        return (self.__convert(rdata), pyaudio.paContinue)

    def play(self):
        self.player_init()
        p = pyaudio.PyAudio()
        s = p.open(format=p.get_format_from_width(2), channels=1, rate=self.sample_rate, output=True,
                   stream_callback=self.__player_callback)
        s.start_stream()
        while self.can_play:
            pass
        s.stop_stream()
        s.close()
        p.terminate()

    def th_play(self):
        if not self.playing:
            self.playing = True
            self.t_gen = threading.Thread(target=self.gen)
            self.t_gen.setDaemon(True)
            self.t_gen.start()
            self.t_play = threading.Thread(target=self.play)
            self.t_play.setDaemon(True)
            self.t_play.start()

    def kill(self):
        self.playing = False
        self.can_gen = False
        self.can_play = False
