#! /usr/bin/env python

import numpy as np
import pyaudio
from pynput.keyboard import Key, Controller


NOTE_MIN = 60  # C4
NOTE_MAX = 69  # A4
FSAMP = 22050  # Sampling frequency in Hz
FRAME_SIZE = 2048  # How many samples per frame?
FRAMES_PER_FFT = 16  # FFT takes average across how many frames?

SAMPLES_PER_FFT = FRAME_SIZE * FRAMES_PER_FFT
FREQ_STEP = FSAMP / SAMPLES_PER_FFT

NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()
NOTA_A_TECLA = {'B3': Key.up, 'E4': Key.down, 'D4': Key.left, 'G4': Key.right}


def freq_to_number(f):
    return 69 + 12 * np.log2(f / 440)


def number_to_freq(n):
    return 440 * 2 ** ((n-69) / 12)


def note_name(n):
    return NOTE_NAMES[n % 12] + str(n / 12 - 1)


def note_to_fftbin(n):
    return number_to_freq(n) / FREQ_STEP


imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))
buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
num_frames = 0

stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                channels=1,
                                rate=FSAMP,
                                input=True,
                                frames_per_buffer=FRAME_SIZE)

stream.start_stream()
keyboard = Controller()

window = 0.5 * (1 - np.cos(np.linspace(0, 2 * np.pi, SAMPLES_PER_FFT, False)))

print('sampling at', FSAMP, 'Hz with max resolution of', FREQ_STEP, 'Hz')

tecla_anterior = None
while stream.is_active():
    buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
    frame_info = np.fromstring(stream.read(FRAME_SIZE), np.int16)
    buf[-FRAME_SIZE:] = frame_info
    amplitud = frame_info.max() - frame_info.min()

    fft = np.fft.rfft(buf * window)

    freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP

    n = freq_to_number(freq)
    n0 = int(round(n))

    num_frames += 1

    if amplitud > 12000:
        print("========= amplitud", amplitud)

        print("======= nota", note_name(n0))

        nombre = note_name(n0).split('.')[0]
        if nombre in NOTA_A_TECLA:
            tecla_nueva = NOTA_A_TECLA[nombre]
            print("tecla nueva:", tecla_nueva)

            if tecla_nueva != tecla_anterior:
                print("APRETANDO", tecla_nueva)
                keyboard.press(tecla_nueva)
                keyboard.release(tecla_nueva)
                tecla_anterior = tecla_nueva
        else:
            tecla_anterior = None
    if amplitud < 2000:
        tecla_anterior = None
