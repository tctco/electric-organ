import wave
import numpy as np


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
