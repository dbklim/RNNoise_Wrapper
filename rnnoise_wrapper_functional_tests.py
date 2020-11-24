#!/usr/bin/python3
# -*- coding: utf-8 -*-
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#       OS : GNU/Linux Ubuntu 16.04 or later
# LANGUAGE : Python 3.5.2 or later
#   AUTHOR : Klim V. O.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

'''
Functional tests for RNNoise_Wrapper.
'''

import os
import sys
import time

is_whl_test = False
if is_whl_test:
    for i, path in enumerate(sys.path):
        if path == os.getcwd():
            del sys.path[i]
            break

from rnnoise_wrapper import RNNoise


def main():
    folder_name_with_audio = 'test_audio/functional_tests'

    denoiser = RNNoise()
    result_tests = []

    # Search audio recordings for test
    all_objects = os.listdir(folder_name_with_audio)
    f_names_source_audio = []
    for one_object in all_objects:
        if os.path.isfile(os.path.join(folder_name_with_audio, one_object)) and one_object.rfind('.wav') != -1 \
                                                                            and one_object.rfind('denoised') == -1:
            f_names_source_audio.append(os.path.join(folder_name_with_audio, one_object))
    f_names_source_audio = sorted(f_names_source_audio, key=lambda f_name: int(f_name[f_name.rfind('_')+1:f_name.rfind('.')]))


    # Test for working with audio as a byte string without headers
    f_name_audio = f_names_source_audio[0]
    audio = denoiser.read_wav(f_name_audio)

    start_time = time.time()
    denoised_audio = denoiser.filter(audio.raw_data, sample_rate=audio.frame_rate)
    elapsed_time = time.time() - start_time

    f_name_denoised_audio = f_name_audio[:f_name_audio.rfind('.wav')] + '_denoised.wav'
    denoiser.write_wav(f_name_denoised_audio, denoised_audio, sample_rate=audio.frame_rate)

    print("Audio: '{}', length: {:.2f} s:".format(f_name_audio, len(audio)/1000))
    print("\tdenoised audio    '{}'".format(f_name_denoised_audio))
    print('\tprocessing time   {:.2f} s'.format(elapsed_time))
    print('\tprocessing speed  {:.1f} RT'.format(len(audio)/1000/elapsed_time))

    # If the last frame is less than 10 ms, then it is padded with zeros to the required size. Because of this, perhaps a small increase in the length
    # of the record after noise reduction
    if len(denoised_audio)/2/8000 - len(audio.raw_data)/2/8000 <= 10 and audio.raw_data != denoised_audio:
        result_tests.append(True)
        print('OK\n')
    else:
        result_tests.append(False)


    # Test for working with streaming audio (buffer size 10 ms = 1 frame) - processing audio recording for 10 milliseconds
    f_name_audio = f_names_source_audio[0]
    audio = denoiser.read_wav(f_name_audio)

    denoised_audio = b''
    buffer_size_ms = 10

    start_time = time.time()
    elapsed_time_per_frame = []
    for i in range(buffer_size_ms, len(audio), buffer_size_ms):
        time_per_frame = time.time()
        denoised_audio += denoiser.filter(audio[i-buffer_size_ms:i].raw_data, sample_rate=audio.frame_rate)
        elapsed_time_per_frame.append(time.time() - time_per_frame)
    if len(audio) % buffer_size_ms != 0:
        time_per_frame = time.time()
        denoised_audio += denoiser.filter(audio[len(audio)-(len(audio)%buffer_size_ms):].raw_data, sample_rate=audio.frame_rate)
        elapsed_time_per_frame.append(time.time() - time_per_frame)
    elapsed_time = time.time() - start_time
    average_elapsed_time_per_frame = sum(elapsed_time_per_frame) / len(elapsed_time_per_frame)

    f_name_denoised_audio = f_name_audio[:f_name_audio.rfind('.wav')] + '_denoised_stream.wav'
    denoiser.write_wav(f_name_denoised_audio, denoised_audio, sample_rate=audio.frame_rate)
    
    print("Audio: '{}', length: {:.2f} s:".format(f_name_audio, len(audio)/1000))
    print("\tdenoised audio                                '{}'".format(f_name_denoised_audio))
    print('\tprocessing time                               {:.2f} s'.format(elapsed_time))
    print('\taverage processing time of 1 buffer ({} ms)   {:.2f} ms'.format(buffer_size_ms, average_elapsed_time_per_frame*1000))
    print('\tprocessing speed                              {:.1f} RT'.format(len(audio)/1000/elapsed_time))
    print('\taverage processing speed of 1 buffer ({} ms)  {:.1f} RT'.format(buffer_size_ms, buffer_size_ms/(average_elapsed_time_per_frame*1000)))

    if len(denoised_audio)/2/8000 - len(audio.raw_data)/2/8000 <= 10 and audio.raw_data != denoised_audio:
        result_tests.append(True)
        print('OK\n')
    else:
        result_tests.append(False)


    # Test for working with audio in the form of pydub.AudioSegment
    for f_name_audio in f_names_source_audio[1:]:
        audio = denoiser.read_wav(f_name_audio)

        start_time = time.time()
        denoised_audio = denoiser.filter(audio)
        elapsed_time = time.time() - start_time

        f_name_denoised_audio = f_name_audio[:f_name_audio.rfind('.wav')] + '_denoised.wav'
        denoiser.write_wav(f_name_denoised_audio, denoised_audio)

        print("Audio: '{}', length: {:.2f} s:".format(f_name_audio, len(audio)/1000))
        print("\tdenoised audio    '{}'".format(f_name_denoised_audio))
        print('\tprocessing time   {:.2f} s'.format(elapsed_time))
        print('\tprocessing speed  {:.1f} RT'.format(len(audio)/1000/elapsed_time))

        if len(denoised_audio)/2/8000 - len(audio.raw_data)/2/8000 <= 10 and audio != denoised_audio:
            result_tests.append(True)
            print('OK\n')
        else:
            result_tests.append(False)

    
    if all(result_tests):
        print('\nALL OK')


if __name__ == '__main__':
    main()