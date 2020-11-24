#!/usr/bin/python3
# -*- coding: utf-8 -*-
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#       OS : GNU/Linux Ubuntu 16.04 or later
# LANGUAGE : Python 3.5.2 or later
#   AUTHOR : Klim V. O.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

'''
Processing and combining all audio recordings in the dataset for RNNoise training into one large .raw audio.
Performed separately for clean and noise audio sets.
'''

import os
import sys
import time
import platform
import signal
import curses
import wave
import argparse
import pydub


curses.setupterm()

TARGET_SAMPLE_RATE = 48000
TARGET_SAMPLE_WIDTH = 2


def create_and_parse_args(folder_name_clean_speech, folder_name_noise, f_name_big_clean_audio, f_name_big_noise_audio):
    ''' Creating and parsing command line arguments. Returns updated `folder_name_clean_speech`, `folder_name_noise`, `f_name_big_clean_audio`
    and `f_name_big_noise_audio`. '''

    parser = argparse.ArgumentParser(description='Processing and combining all audio recordings in the dataset for RNNoise training into one large ' + \
                                                 '.raw audio. Performed separately for clean and noise audio sets. The source dataset remains unchanged.')
    parser.add_argument('-cf', '--clean_folder', type=str, default=folder_name_clean_speech,
                        help='Folder name with clean speech audio (for example, "training_set_oct30_5h_balanced/clean")')
    parser.add_argument('-nf', '--noise_folder', type=str, default=folder_name_noise,
                        help='Folder name with noise audio (for example, "training_set_oct30_5h_balanced/noise")')
    parser.add_argument('-bca', '--big_clean_audio', type=str, default=f_name_big_clean_audio,
                        help='Name .raw audio for combined clean speech (for example, "training_set_oct30_5h_balanced/all_clean.raw")')
    parser.add_argument('-bna', '--big_noise_audio', type=str, default=f_name_big_noise_audio,
                        help='Name .raw audio for combined noise (for example, "training_set_oct30_5h_balanced/all_noise.raw")')
    args = parser.parse_args()

    folder_name_clean_speech = args.clean_folder + '/' if args.clean_folder[-1] != '/' else args.clean_folder
    folder_name_noise = args.noise_folder + '/' if args.noise_folder[-1] != '/' else args.noise_folder
    f_name_big_clean_audio = args.big_clean_audio
    f_name_big_noise_audio = args.big_noise_audio
    
    return folder_name_clean_speech, folder_name_noise, f_name_big_clean_audio, f_name_big_noise_audio


def search_audio_in_folder(folder_name, name_for_log):
    ''' Searching audio in folder.
    
    1. folder_name - folder name with audio recordings
    2. name_for_log - name for nice logging
    3. returns a list with found audio names  '''

    print("\n[i] Searching for {} audio in '{}'".format(name_for_log, folder_name))

    f_names_audio = sorted(os.listdir(folder_name), key=lambda f_name: int(f_name[f_name.rfind('_')+1:f_name.rfind('.')]))
    f_names_audio = [folder_name+f_name_audio for f_name_audio in f_names_audio]

    print('[i] Found {} {} audio(-s)'.format(len(f_names_audio), name_for_log))
    return f_names_audio


def prepare_audio(f_name_audio):
    ''' Preparing audio with pydub: reading audio, changing sample rate and sample width. Sample rate and sample width values are taken
    from TARGET_SAMPLE_RATE and TARGET_SAMPLE_WIDTH.
    
    1. f_name_audio - target audio name
    2. returns modified pydub.AudioSegment '''

    audio = pydub.AudioSegment.from_wav(f_name_audio)
    audio = audio.set_frame_rate(TARGET_SAMPLE_RATE)
    audio = audio.set_sample_width(TARGET_SAMPLE_WIDTH)
    return audio


def test_preparation(f_name_big_audio, f_names_all_audio, name_for_log):
    ''' Testing the preparation of audio recordings. Reading, processing and combining the first 100 audio in dataset.
    
    1. f_name_big_audio - name of combined .wav audio
    2. f_names_all_audio - list with audio names in dataset
    3. name_for_log - name for nice logging
    4. returns None '''

    print('\n[i] Test preparation of the first 100 audios...')
    f_name_test_audio = f_name_big_audio[:f_name_big_audio.rfind('.')] + '_test.wav'
    test_audio = pydub.AudioSegment.empty()

    if len(f_names_all_audio) >= 100:
        f_names_test_audio = f_names_all_audio[:100]
    else:
        f_names_test_audio = f_names_all_audio

    for f_name_audio in f_names_test_audio:
        test_audio += prepare_audio(f_name_audio)

    print("[i] Saving test {} audio in '{}'".format(name_for_log, f_name_test_audio))
    test_audio.export(f_name_test_audio, format='wav')
    del test_audio


def prepare_all_audio(f_names_all_audio, f_name_big_audio, name_for_log):
    ''' Preparation of all audio recordings in the dataset: reading, processing and combining all audio into one large .raw audio.

    1. f_names_all_audio - list with audio names in dataset
    2. f_name_big_audio - name of combined .raw audio
    3. name_for_log - name for nice logging
    4. returns None '''

    elapsed_time_per_audio = 0.0
    total_start_time = time.time()

    print('\n[i] Loading, preparing and combining {} audio... 0 of {}'.format(name_for_log, len(f_names_all_audio)))
    with open(f_name_big_audio, 'wb') as f_big_audio:
        for i, f_name_audio in enumerate(f_names_all_audio):
            if i % 10 == 0 or i == len(f_names_all_audio) - 1:
                os.write(sys.stdout.fileno(), curses.tigetstr('cuu1'))
                print('[i] Loading, preparing and combining {} audio... {} of {}, {:.1f} ms/audio    '.format(
                        name_for_log, i, len(f_names_all_audio), elapsed_time_per_audio))

            start_time = time.time()
            audio_data_b = prepare_audio(f_name_audio).raw_data
            elapsed_time_per_audio = (time.time() - start_time) * 1000

            f_big_audio.write(audio_data_b)

    total_elapsed_time = time.time() - total_start_time
    print('[i] Total elapsed time: {:.1f} s / {:.1f} min / {:.1f} h'.format(total_elapsed_time, total_elapsed_time/60, total_elapsed_time/60/60))
    print("[i] Big {} audio saved in '{}'".format(name_for_log, f_name_big_audio))


# Note: parallelization doesn't make sense (checked using multiprocessing.Pool). When using SSD, the processing time depends on the processing time
# of 1 audio recording and the speed of reading/writing to disk.
# When using multiprocessing, RAM consumption increases and additional costs for servicing child processes appear, as a result of which the increase 
# in processing speed is 5-10% at best.


def main():
    folder_name_clean_speech = 'training_set_oct30_5h_balanced/clean/'
    folder_name_noise = 'training_set_oct30_5h_balanced/noise/'

    f_name_big_clean_audio = 'training_set_oct30_5h_balanced/all_clean.raw'
    f_name_big_noise_audio = 'training_set_oct30_5h_balanced/all_noise.raw'

    folder_name_clean_speech, folder_name_noise, f_name_big_clean_audio, f_name_big_noise_audio = create_and_parse_args(folder_name_clean_speech,
        folder_name_noise, f_name_big_clean_audio, f_name_big_noise_audio)

    if f_name_big_clean_audio.rfind('/') != -1:
        folder_name_for_big_clean_audio = f_name_big_clean_audio[:f_name_big_clean_audio.rfind('/')]
        if not os.path.exists(folder_name_for_big_clean_audio):
            os.mkdir(folder_name_for_big_clean_audio)
    
    if f_name_big_noise_audio.rfind('/') != -1:
        folder_name_for_big_noise_audio = f_name_big_noise_audio[:f_name_big_noise_audio.rfind('/')]
        if not os.path.exists(folder_name_for_big_noise_audio):
            os.mkdir(folder_name_for_big_noise_audio)

    print('[i] Target sample rate: {} Hz'.format(TARGET_SAMPLE_RATE))
    print('[i] Target sample width: {} bytes/{} bit'.format(TARGET_SAMPLE_WIDTH, TARGET_SAMPLE_WIDTH*8))


    f_names_clean_audio = search_audio_in_folder(folder_name_clean_speech, 'clean speech')
    test_preparation(f_name_big_clean_audio, f_names_clean_audio, 'clean speech')
    prepare_all_audio(f_names_clean_audio, f_name_big_clean_audio, 'clean speech')


    f_names_noise_audio = search_audio_in_folder(folder_name_noise, 'noise')
    test_preparation(f_name_big_noise_audio, f_names_noise_audio, 'noise')
    prepare_all_audio(f_names_noise_audio, f_name_big_noise_audio, 'noise')


if __name__ == '__main__':
    main()
