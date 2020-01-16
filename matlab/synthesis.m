clear
fs = 44100;
f = 220;
time = 1;
t = 0:1/fs:time;
N = 4096;
y = sin(2 * pi * f * t) + 0.2 * sin(2 * pi * 2 * f * t) + 0.3 * sin(2 * pi * 3 * f * t);

Y = fft(y, N);
x = [0:1:N - 1] * fs / N;

subplot(211);
plot(x, abs(Y));
title('Bilateral Spectrum');
xlabel('f(Hz)');
ylabel('FFT Amplitude');
subplot(212);
plot(x(1:N / 2), abs(Y(1:N / 2)));
title('Unilateral Spectrum');
xlabel('f(Hz)');
ylabel('FFT Amplitude');