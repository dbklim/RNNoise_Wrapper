#!/usr/bin/python3
# -*- coding: utf-8 -*-
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#       OS : GNU/Linux Ubuntu 16.04 or 18.04
# LANGUAGE : Python 3.5.2 or later
#   AUTHOR : Klim V. O.
#     DATE : 14.10.2019
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

'''
Интерфейс командной строки для rnnoise_wrapper.RNNoise().
'''

import os
import sys
from rnnoise_wrapper import RNNoise


def print_help():
    print('\nИспользование: rnnoise_wrapper.py input.wav output.wav')
    print('\tinput.wav - имя исходной .wav аудиозаписи')
    print('\toutput.wav - имя .wav аудиофайла, в который будет сохранена исходная аудиозапись после шумоподавления\n')
    os._exit(0)


def cli():
    if len(sys.argv) > 2 and sys.argv[1].rfind('.wav') != -1 and os.path.exists(sys.argv[1]):
        denoiser = RNNoise()
        audio = denoiser.read_wav(sys.argv[1])
        filtered_audio = denoiser.filter(audio)
        if sys.argv[2].rfind('.wav') == -1:
            f_name_denoised_audio = sys.argv[2] + '.wav'
        else:
            f_name_denoised_audio = sys.argv[2]
        print('Сохранение %s' % (f_name_denoised_audio))
        denoiser.write_wav(f_name_denoised_audio, filtered_audio)
    else:
        print_help()


if __name__ == '__main__':
    cli()