#!/usr/bin/python3
# -*- coding: utf-8 -*-
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#       OS : GNU/Linux Ubuntu 16.04 or 18.04
# LANGUAGE : Python 3.5.2 or later
#   AUTHOR : Klim V. O.
#     DATE : 09.10.2019
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

'''
Предназначен для подавления шума в wav аудиозаписи.
Для работы используется RNNoise (https://github.com/xiph/rnnoise). Оригинальная статья https://people.xiph.org/~jm/demo/rnnoise/.

Зависимости: pydub, numpy, scipy.

Сборка и установка RNNoise только для работы с данной обёрткой:
1. sudo apt-get -y install autoconf libtool
2. git clone https://github.com/xiph/rnnoise RNNoise
3. cd RNNoise
5. ./autogen.sh
6. ./configure
7. make
8. cd -
9. mkdir RNNoise_libs
10. mv RNNoise/.libs/* RNNoise_libs
11. rm --rf RNNoise

Использование RNNoise (в папке с RNNoise):
./examples/rnnoise_demo input.raw output.raw

Поддерживаются только моно RAW 16 бит 48кГц!

Код данной обёртки взят из https://github.com/xiph/rnnoise/issues/69.
'''

import platform
import signal
import wave
import os,sys
import ctypes
import contextlib
import numpy as np
from ctypes import util
from scipy.io import wavfile
from pydub import AudioSegment

#lib_path = util.find_library("rnnoise")
#if (not("/" in lib_path)):
#    lib_path = (os.popen('ldconfig -p | grep '+lib_path).read().split('\n')[0].strip().split(" ")[-1] or ("/usr/local/lib/"+lib_path))

# https://github.com/Shb742/rnnoise_python (оригинал не работает, вызывает segmentation fault)

# сделать пример кода для обработки одного фрейма 

class RNNoise(object):
    def __init__(self, lib_path):
        self.lib = ctypes.cdll.LoadLibrary(lib_path)
        self.lib.rnnoise_process_frame.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
        self.lib.rnnoise_process_frame.restype = ctypes.c_float
        self.lib.rnnoise_create.restype = ctypes.c_void_p
        self.lib.rnnoise_destroy.argtypes = [ctypes.c_void_p]

        self.rnnoise_lib = self.lib.rnnoise_create(None)


    def process_frame(self, inbuf):
        outbuf = np.ndarray((480,), 'h', inbuf).astype(ctypes.c_float)
        outbuf_ptr = outbuf.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

        VodProb = self.lib.rnnoise_process_frame(self.rnnoise_lib, outbuf_ptr, outbuf_ptr)
        return (VodProb, outbuf.astype(ctypes.c_short).tobytes())


    def filter(self):
        '''  '''


    def get_frames(self):
        '''  '''


    def read_wav(self):
        '''  '''

    
    def write_wav(self):
        '''  '''


    def destroy(self):
        self.lib.rnnoise_destroy(self.rnnoise_lib)


def read_wave(path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate        
        
      
def frame_generator(frame_duration_ms,
                    audio,
                    sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield audio[offset:offset + n]
        offset += n


# Ни в коем случае не использовать assert в продакшн коде!!! Заменить на raise базовое_исключение('сообщение')
# Проверить следующие моменты, что бы попытаться улучшить качество работы: исходный wav как-нибудь нормализовать.


def main():
    lib_path = 'libs/librnnoise.so.0'
    denoiser = RNNoise(lib_path)
    wav_path = 'test1.wav' # исходный любой .wav, который поддерживается pydub

    TARGET_SR = 48000
    TEMP_FILE = 'temp.wav'

    sound = AudioSegment.from_wav(wav_path)

    # Работает ужасно медленно и толком нет результата, DNNoise лучше
    #from logmmse import logmmse_from_file
    #out = logmmse_from_file(wav_path, initial_noise=9, window_size=0, noise_threshold=0.25)

    #new_sound = AudioSegment(out.tobytes(), sample_width=sound.sample_width, frame_rate=sound.frame_rate, channels=sound.channels)
    #new_sound.export('temp1.wav', format='wav')

    sound = sound.set_frame_rate(TARGET_SR)
    sound = sound.set_channels(1)

    sound.export(TEMP_FILE, format="wav")

    audio, sample_rate = read_wave(TEMP_FILE)
    assert sample_rate == TARGET_SR

    frames = frame_generator(10, audio, TARGET_SR)
    frames = list(frames)

    tups = [denoiser.process_frame(frame) for frame in frames]
    denoised_frames = [tup[1] for tup in tups]

    denoised_wav = np.concatenate([np.frombuffer(frame, dtype=np.int16) for frame in denoised_frames])
    audio_bytes = b''.join(denoised_frames)

    audio = AudioSegment(data=audio_bytes, sample_width=2, frame_rate=48000, channels=1)
    audio.export('result.wav', format='wav')

    wavfile.write(wav_path[:wav_path.rfind('.wav')] + '_denoised.wav', TARGET_SR, denoised_wav) # исходный .wav после шумоподавления


def on_stop(*args):
    print('\n[i] Остановлено')
    os._exit(0)


if __name__ == '__main__':
    # При нажатии комбинаций Ctrl+Z, Ctrl+C либо закрытии терминала будет вызываться функция on_stop() (Работает только на linux системах!)
    if platform.system() == 'Linux':
        for sig in (signal.SIGTSTP, signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, on_stop)
    main()