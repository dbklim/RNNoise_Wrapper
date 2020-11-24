#!/usr/bin/python3
# -*- coding: utf-8 -*-
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#       OS : GNU/Linux Ubuntu 16.04 or later
# LANGUAGE : Python 3.5.2 or later
#   AUTHOR : Klim V. O.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

'''
Simple CLI for rnnoise_wrapper.RNNoise().
'''

import os
import sys
import time
import argparse
from rnnoise_wrapper import RNNoise


def denoise():
    parser = argparse.ArgumentParser(description='Simple CLI for audio noise reduction using RNNoise_Wrapper.')
    parser.add_argument('-i', '--source_audio', type=str, required=True,
                        help='Name .wav audio for noise reduction (for example, "test_audio/source/test_3.wav")')
    parser.add_argument('-o', '--denoised_audio', type=str, required=True,
                        help='Name .wav audio for result (for example, "test_audio/test_3_denoised.wav")')
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    f_name_audio = args.source_audio
    f_name_denoised_audio = args.denoised_audio

    if f_name_audio.rfind('.wav') == -1:
        f_name_audio += '.wav'
    if f_name_denoised_audio.rfind('.wav') == -1:
        f_name_denoised_audio += '.wav'


    denoiser = RNNoise()

    print("[i] Loading '{}'...".format(f_name_audio))
    audio = denoiser.read_wav(f_name_audio)

    start_time = time.time()
    denoised_audio = denoiser.filter(audio)
    elapsed_time = time.time() - start_time

    print("[i] Saving '{}'...".format(f_name_denoised_audio))
    denoiser.write_wav(f_name_denoised_audio, denoised_audio)

    print('[i] Audio length: {:.2f} s, processing time: {:.2f} s, processing speed: {:.1f} RT'.format(
        len(audio)/1000, elapsed_time, len(audio)/1000/elapsed_time))


if __name__ == '__main__':
    denoise()
