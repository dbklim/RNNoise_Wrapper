#!/usr/bin/python3
# -*- coding: utf-8 -*-
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#       OS : GNU/Linux Ubuntu 16.04 or later
# LANGUAGE : Python 3.5.2 or later
#   AUTHOR : Klim V. O.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

'''
Comparative tests for RNNoise_Wrapper with building of melspectrograms for each test audio recording and model.
'''

import os
import sys
import time
import pydub
import librosa
import librosa.feature
import librosa.display
import matplotlib.pylab as plt
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

is_whl_test = False
if is_whl_test:
    for i, path in enumerate(sys.path):
        if path == os.getcwd():
            del sys.path[i]
            break

from rnnoise_wrapper import RNNoise


def calculate_melspectrogram(audio_data, sample_rate, figure, axis):
    ''' Calculation and building of melspectrogram for audio. '''

    melspectrogram = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate, n_fft=512, hop_length=128)
    melspectrogram_dB = librosa.power_to_db(melspectrogram, ref=np.max(melspectrogram))
    img = librosa.display.specshow(melspectrogram_dB, x_axis='s', y_axis='linear', sr=sample_rate, hop_length=128, fmax=8000, ax=axis, cmap='gist_ncar')
    figure.colorbar(img, ax=axis, format='%+2.0f dB')
    return figure


def calculate_mean_rms(audio_data):
    ''' Calculation mean RMS for audio. '''

    spectrogram = librosa.magphase(librosa.stft(audio_data, window=np.ones, center=False))[0]
    rmse_values = librosa.feature.rms(S=spectrogram)
    mean_rms = round(np.mean(rmse_values), 4)
    return mean_rms


def build_melspectrograms(f_name_source_audio, f_name_denoised_def_audio, f_name_denoised_new_audio, f_name_plot):
    ''' Calculation and building of melspectrograms for source audio, denoised audio using default RNNoise model and denoised audio using new RNNoise model.
    
    1. f_name_source_audio - source audio name
    2. f_name_denoised_def_audio - denoised audio name using default model
    3. f_name_denoised_new_audio - denoised audio name using new model
    4. f_name_plot - plot name with melspectrograms
    5. returns None '''

    source_audio_data, sample_rate = sf.read(f_name_source_audio)
    denoised_audio_data_def, sample_rate = sf.read(f_name_denoised_def_audio)
    denoised_audio_data_new, sample_rate = sf.read(f_name_denoised_new_audio)

    # Calculating length of audio recording and median RMS for each audio
    mean_rms = calculate_mean_rms(source_audio_data)
    denoised_mean_rms_def = calculate_mean_rms(denoised_audio_data_def)
    denoised_mean_rms_new = calculate_mean_rms(denoised_audio_data_new)

    # Build melspectrograms before and after denoising
    # Beautiful color options for cmap: gist_ncar, CMRmap, hot
    figure, axes = plt.subplots(3, 1, figsize=(16, 12), dpi=150, constrained_layout=True)

    figure = calculate_melspectrogram(source_audio_data, sample_rate, figure, axes[0])
    axes[0].set_title('Source mel-spectrogram, mean RMS: {}'.format(mean_rms), color='black')

    figure = calculate_melspectrogram(denoised_audio_data_def, sample_rate, figure, axes[1])
    axes[1].set_title('Denoised mel-spectrogram (default model), mean RMS: {}'.format(denoised_mean_rms_def), color='black')

    figure = calculate_melspectrogram(denoised_audio_data_new, sample_rate, figure, axes[2])
    axes[2].set_title('Denoised mel-spectrogram (new model), mean RMS: {}'.format(denoised_mean_rms_new), color='black')

    plt.savefig(f_name_plot)
    plt.close(figure)
    plt.clf()


def denoise(f_name_source_audio, f_name_denoised_audio, denoiser_obj, buffer_size_ms=20):
    ''' Noise reduction of audio recording using RNNoise in streaming audio mode.
    
    1. f_name_source_audio - source audio name
    2. f_name_denoised_audio - denoised audio name
    3. denoiser_obj - initialized RNNoise class
    4. buffer_size_ms - buffer size in ms for denoising of streaming audio
    5. returns length audio in seconds, elapsed time for denoising, average elapsed time for denoising buffer '''
    
    audio = denoiser_obj.read_wav(f_name_source_audio)

    audio_b = audio.raw_data
    sample_rate = audio.frame_rate
    sample_width = audio.sample_width
    len_audio_s = len(audio) / 1000
    denoised_audio_b = b''
    buffer_size_ms = 20
    buffer_size_b = int(buffer_size_ms/1000*sample_rate*sample_width)

    start_time = time.time()
    elapsed_time_per_buffer = []

    for i in range(buffer_size_b, len(audio_b), buffer_size_b):
        time_per_frame = time.time()
        denoised_audio_b += denoiser_obj.filter(audio_b[i-buffer_size_b:i], sample_rate=sample_rate)
        elapsed_time_per_buffer.append(time.time() - time_per_frame)

    if len(audio) % buffer_size_b != 0:
        time_per_frame = time.time()
        denoised_audio_b += denoiser_obj.filter(audio_b[len(audio_b)-(len(audio_b)%buffer_size_b):], sample_rate=sample_rate)
        elapsed_time_per_buffer.append(time.time() - time_per_frame)

    elapsed_time = time.time() - start_time
    average_elapsed_time_per_buffer = sum(elapsed_time_per_buffer) / len(elapsed_time_per_buffer)

    denoiser_obj.write_wav(f_name_denoised_audio, denoised_audio_b, sample_rate=sample_rate)
    return len_audio_s, elapsed_time, average_elapsed_time_per_buffer




def main():
    folder_name_with_audio = 'test_audio/comparative_tests/5h_ru_500k'
    f_name_rnnoise_binary = 'train_logs/training_set_oct30_5h_ru/librnnoise_5h_ru_500k.so.0.4.1'

    buffer_size_ms = 20

    denoiser_def = RNNoise(f_name_lib='librnnoise_default')
    denoiser_new = RNNoise(f_name_lib=f_name_rnnoise_binary)


    # Search audio recordings for test
    all_objects = os.listdir(folder_name_with_audio)
    f_names_source_audio = []
    for one_object in all_objects:
        if os.path.isfile(os.path.join(folder_name_with_audio, one_object)) and one_object.rfind('.wav') != -1 \
                                                                            and one_object.rfind('denoised') == -1 \
                                                                            and one_object.rfind('rnnoise') == -1:
            f_names_source_audio.append(os.path.join(folder_name_with_audio, one_object))
    f_names_source_audio = sorted(f_names_source_audio, key=lambda f_name: int(f_name[f_name.rfind('_')+1:f_name.rfind('.')]))


    # Main testing cycle
    rt_speeds_def = []
    rt_speeds_new = []
    rt_speeds_buf_def = []
    rt_speeds_buf_new = []
    for f_name_audio in f_names_source_audio:
        f_name_denoised_def_audio = f_name_audio[:f_name_audio.rfind('.')] + '_rnnoise_def.wav'
        f_name_denoised_new_audio = f_name_audio[:f_name_audio.rfind('.')] + '_rnnoise_new.wav'
        f_name_plot = f_name_audio[:f_name_audio.rfind('.')] + '_mel.png'

        # Denoising audio
        len_audio_s, elapsed_time_def, elapsed_time_buf_def = denoise(f_name_audio, f_name_denoised_def_audio, denoiser_def, buffer_size_ms)
        len_audio_s, elapsed_time_new, elapsed_time_buf_new = denoise(f_name_audio, f_name_denoised_new_audio, denoiser_new, buffer_size_ms)

        build_melspectrograms(f_name_audio, f_name_denoised_def_audio, f_name_denoised_new_audio, f_name_plot)

        # Calculating work speed
        rt_speeds_def.append(len_audio_s/elapsed_time_def)
        rt_speeds_buf_def.append(buffer_size_ms/(elapsed_time_buf_def*1000))

        rt_speeds_new.append(len_audio_s/elapsed_time_new)
        rt_speeds_buf_new.append(buffer_size_ms/(elapsed_time_buf_new*1000))

        print("\n[i] Audio '{}', length {:.2f} s (default/new):".format(f_name_audio, len_audio_s))
        print('\tprocessing time                               {:.2f}/{:.2f} s'.format(elapsed_time_def, elapsed_time_new))
        print('\taverage processing time of 1 buffer ({} ms)   {:.2f}/{:.2f} ms'.format(buffer_size_ms, elapsed_time_buf_def*1000, elapsed_time_buf_new*1000))
        print('\tprocessing speed                              {:.1f}/{:.1f} RT'.format(rt_speeds_def[-1], rt_speeds_new[-1]))
        print('\taverage processing speed of 1 buffer ({} ms)  {:.1f}/{:.1f} RT'.format(buffer_size_ms, rt_speeds_buf_def[-1], rt_speeds_buf_new[-1]))

    print('\n[i] Average processing speed {:.1f}/{:.1f} RT, average processing speed of 1 buffer ({} ms) {:.1f}/{:.1f} RT'.format(
        sum(rt_speeds_def)/len(rt_speeds_def), sum(rt_speeds_new)/len(rt_speeds_new),
        buffer_size_ms,
        sum(rt_speeds_buf_def)/len(rt_speeds_buf_def), sum(rt_speeds_buf_new)/len(rt_speeds_buf_new)))


if __name__ == '__main__':
    main()
