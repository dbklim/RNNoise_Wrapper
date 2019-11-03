#!/usr/bin/python3
# -*- coding: utf-8 -*-
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#       OS : GNU/Linux Ubuntu 16.04 or 18.04
# LANGUAGE : Python 3.5.2 or later
#   AUTHOR : Klim V. O.
#     DATE : 14.10.2019
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

'''
Тесты для RNNoise_Wrapper.
'''

import time
from rnnoise_wrapper import RNNoise


def main():
    denoiser = RNNoise()
    result_tests = []

    # Тест работы с аудио в виде байтовой строки без заголовков
    f_name_audio = 'test_audio/test_1.wav'
    audio = denoiser.read_wav(f_name_audio)

    start_time = time.time()
    filtered_audio = denoiser.filter(audio.raw_data, sample_rate=audio.frame_rate)
    work_time = time.time() - start_time

    f_name_denoised_audio = f_name_audio[:f_name_audio.rfind('.wav')] + '_denoised.wav'
    denoiser.write_wav(f_name_denoised_audio, filtered_audio, sample_rate=audio.frame_rate)
    print('Audio: %s\nLength audio: %.4f s\nDenoised audio: %s\nWork time: %.4f s' % (f_name_audio, len(audio)/1000, f_name_denoised_audio, work_time))

    # Если последний фрейм меньше 10 мс, то он дополняется нулями до необходимого размера. Из-за этого возможно небольшое увеличение длины
    # аудиозаписи после шумоподавления
    if round(len(audio.raw_data)/2/8000, 1) == round(len(filtered_audio)/2/8000, 1) and audio.raw_data != filtered_audio:
        result_tests.append(True)
        print('OK')
    else:
        result_tests.append(False)


    # Тест работы с аудио в виде pydub.AudioSegment (предпочитаемый вариант использования)
    for i in range(2, 6):
        f_name_audio = 'test_audio/test_%i.wav' % i
        audio = denoiser.read_wav(f_name_audio)
        
        start_time = time.time()
        filtered_audio = denoiser.filter(audio)
        work_time = time.time() - start_time

        f_name_denoised_audio = f_name_audio[:f_name_audio.rfind('.wav')] + '_denoised.wav'
        denoiser.write_wav(f_name_denoised_audio, filtered_audio)
        print('\nAudio: %s\nLength audio: %.4f s\nDenoised audio: %s\nWork time: %.4f s' % (f_name_audio, len(audio)/1000, f_name_denoised_audio, work_time))

        if round(len(audio)/1000, 1) == round(len(filtered_audio)/1000, 1) and audio != filtered_audio:
            result_tests.append(True)
            print('OK')
        else:
            result_tests.append(False)


    # Тест работы с потоковым аудио (размер буфера 10 мс, т.е. размером 1 фрейм) - т.е. обработка аудиозаписи по n миллисекунд
    f_name_audio = 'test_audio/test_1.wav'
    audio = denoiser.read_wav(f_name_audio)

    filtered_audio = b''
    buffer_size_ms = 10

    start_time = time.time()
    average_work_time_per_frame = []
    for i in range(buffer_size_ms, len(audio), buffer_size_ms):
        time_per_frame = time.time()
        filtered_audio += denoiser.filter(audio[i-buffer_size_ms:i].raw_data, sample_rate=audio.frame_rate)
        average_work_time_per_frame.append(time.time() - time_per_frame)
    if len(audio) % buffer_size_ms != 0:
        time_per_frame = time.time()
        filtered_audio += denoiser.filter(audio[len(audio)-(len(audio)%buffer_size_ms):].raw_data, sample_rate=audio.frame_rate)
        average_work_time_per_frame.append(time.time() - time_per_frame)
    work_time = time.time() - start_time
    average_work_time = sum(average_work_time_per_frame) / len(average_work_time_per_frame)

    f_name_denoised_audio = f_name_audio[:f_name_audio.rfind('.wav')] + '_denoised_f.wav'
    denoiser.write_wav(f_name_denoised_audio, filtered_audio, sample_rate=audio.frame_rate)
    print('\nAudio: %s\nLength audio: %.4f s\nDenoised audio: %s\nTotal work time (by frames): %.4f s\nAverage work time (per 1 frame): %.6f s'
          % (f_name_audio, len(audio)/1000, f_name_denoised_audio, work_time, average_work_time))
    
    if round(len(audio.raw_data)/2/8000, 1) == round(len(filtered_audio)/2/8000, 1) and audio.raw_data != filtered_audio:
        result_tests.append(True)
        print('OK')
    else:
        result_tests.append(False)

    
    if all(result_tests):
        print('\nALL OK')


if __name__ == '__main__':
    main()