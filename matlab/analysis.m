N = 500;
ACCURACY = 0.1;
[y, fs] = audioread("D:\MyPython\game\project\sound\note (33).wav");
Y = fft(y(500:1000, :), N);
s = abs(Y);
s = s ./ max(s);
s_half = s(1:N / 2, :);
x = (0:(N - 1)) * fs / N;
x_half = x(1:(N / 2));
subplot(311);
plot(x_half, s_half)
title("Unilateral Spectrum of Natural Note");
xlabel("f(Hz)");
ylabel("FFT Amplitude");

time = 1;
note = zeros(fs * time, 2);
t = 1/fs:1/fs:time;
for i = 1:(N/2)
    if s_half(i, 1) > ACCURACY
        note(:, 1) = note(:, 1) + (s_half(i, 1) .* sin(2 .* pi .* x_half(i) .* t))';
    end
    if s_half(i, 2) > ACCURACY
        note(:, 2) = note(:, 2) + (s_half(i, 2) .* sin(2 .* pi .* x_half(i) .* t))';
    end
end
note_Y = abs(fft(note, N));
note_Y = note_Y ./ max(note_Y);
note_Y_half = note_Y(1:N / 2, :);
subplot(312);
plot(x_half, note_Y_half);
title("Unilateral Spectrum of Synthesized Note: Using the maximum amplitude frequences");
xlabel("f(Hz)");
ylabel("FFT Amplitude");
note_1 = note * 0.2;
% sound(note_1);

note = 0;
base_frequency = 0;
index = 0;
s_half = sum(s_half, 2);
for i = 1:2048
    if s_half(i, 1) > 0.3
        base_frequency = x_half(i);
        index = i;
        break;
    end
end
for i = 1:10
    note = note + s_half(index * i) * sin(2 * pi * base_frequency * i * t);
end
note_Y = abs(fft(note, N));
note_Y = note_Y ./ max(note_Y);
note_Y_half = note_Y(1:N / 2);
subplot(313);
plot(x_half, note_Y_half);
title("Unilateral Spectrum of Synthesized Note: Using first 15 Co-frequency");
xlabel("f(Hz)");
ylabel("FFT Amplitude");
note_2 = 0.25 * note;
% sound(note_2);



