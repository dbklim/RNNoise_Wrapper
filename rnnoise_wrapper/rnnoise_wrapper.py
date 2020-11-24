#!/usr/bin/python3
# -*- coding: utf-8 -*-
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#       OS : GNU/Linux Ubuntu 16.04 or later
# LANGUAGE : Python 3.5.2 or later
#   AUTHOR : Klim V. O.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

'''
Предназначен для подавления шума в wav аудиозаписи с помощью библиотеки RNNoise (https://github.com/xiph/rnnoise).

Содержит класс RNNoise. Подробнее в https://github.com/Desklop/RNNoise_Wrapper.

Зависимости: pydub, numpy.
'''

import os
import platform
import time
import ctypes
import pkg_resources
import numpy as np
from pydub import AudioSegment


__version__ = 1.1


class RNNoise(object):
    ''' Предоставляет методы для упрощения работы с шумодавом RNNoise:
    - read_wav(): загрузка .wav аудиозаписи и приведение её в поддерживаемый формат
    - write_wav(): сохранение .wav аудиозаписи
    - filter(): разбиение аудиозаписи на фреймы и очистка их от шума
    - filter_frame(): очистка только одного фрейма от шума (обращение напрямую к бинарнику RNNoise)
    - reset(): пересоздать объект RNNoise из библиотеки для сброса состояния нейронной сети

    1. f_name_lib - путь к библиотеке, если None и:
            - тип используемой ОС linux или mac (darwin) - использовать librnnoise_5h_b_500k.so.0.4.1 из файлов пакета
            - тип используемой ОС windows или другое - выполнить поиск в текущей папке и её подпапках файла с префиксом 'librnnoise'
        если является путём к библиотеке/именем библиотеки - проверить существование переданного пути/имени библиотеки и если:
            - путь/имя существует - вернуть абсолютный путь
            - путь/имя не существует - выполнить поиск в текущей папке и её подпапках файла/пути, используя переданное значение в качестве субимени'''

    sample_width = 2
    channels = 1
    sample_rate = 48000
    frame_duration_ms = 10

    def __init__(self, f_name_lib=None):
        f_name_lib = self.__get_f_name_lib(f_name_lib)
        self.rnnoise_lib = ctypes.cdll.LoadLibrary(f_name_lib)

        self.rnnoise_lib.rnnoise_process_frame.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
        self.rnnoise_lib.rnnoise_process_frame.restype = ctypes.c_float
        self.rnnoise_lib.rnnoise_create.restype = ctypes.c_void_p
        self.rnnoise_lib.rnnoise_destroy.argtypes = [ctypes.c_void_p]

        self.rnnoise_obj = self.rnnoise_lib.rnnoise_create(None)


    def __get_f_name_lib(self, f_name_lib=None):
        ''' Найти и/или проверить путь к скомпилированной библиотеке RNNoise.

        1. f_name_lib - путь к библиотеке, если None и:
                - тип используемой ОС linux или mac (darwin) - использовать librnnoise_5h_b_500k.so.0.4.1 из файлов пакета
                - тип используемой ОС windows или другое - выполнить поиск в текущей папке и её подпапках файла с префиксом 'librnnoise'
            если является путём к библиотеке/именем библиотеки - проверить существование переданного пути/имени библиотеки и если:
                - путь/имя существует - вернуть абсолютный путь
                - путь/имя не существует - выполнить поиск в текущей папке и её подпапках файла/пути, используя переданное значение в качестве субимени
        2. возвращает f_name_lib с проверенным абсолютным путём к найденной библиотеке '''

        package_name = __file__
        package_name = package_name[package_name.rfind('/')+1:package_name.rfind('.py')]

        if not f_name_lib:
            subname = 'librnnoise'
            system = platform.system()
            if system == 'Linux' or system == 'Darwin':
                found_f_name_lib = pkg_resources.resource_filename(package_name, 'libs/{}_5h_b_500k.so.0.4.1'.format(subname))
                if not os.path.exists(found_f_name_lib):
                    found_f_name_lib = self.__find_lib(subname)
            else:
                found_f_name_lib = self.__find_lib(subname)
            
            if not found_f_name_lib:
                raise NameError("could not find RNNoise library with subname '{}'".format(subname))

        else:
            f_names_available_libs = pkg_resources.resource_listdir(package_name, 'libs/')
            for available_lib in f_names_available_libs:
                if available_lib.find(f_name_lib) != -1:
                    f_name_lib = pkg_resources.resource_filename(package_name, 'libs/{}'.format(available_lib))

            found_f_name_lib = self.__find_lib(f_name_lib)
            if not found_f_name_lib:
                raise NameError("could not find RNNoise library with name/subname '{}'".format(f_name_lib))

        return found_f_name_lib


    def __find_lib(self, f_name_lib, root_folder='.'):
        ''' Выполнить рекурсивный поиск файла f_name_lib в папке root_folder и всех её подпапках.
        1. f_name_lib - имя искомого файла или его субимя (часть имени, позволяющая однозначно идентифицировать файл)
        2. root_folder - корневая папка, из которой начинать поиск
        3. возвращает найденный существующий путь или None '''

        f_name_lib_full = os.path.abspath(f_name_lib)
        if os.path.isfile(f_name_lib_full) and os.path.exists(f_name_lib_full):
            return f_name_lib_full

        for path, folder_names, f_names in os.walk(root_folder):
            for f_name in f_names:
                if f_name.rfind(f_name_lib) != -1:
                    return os.path.join(path, f_name)


    def reset(self):
        ''' Сбросить состояние нейронной сети путём создания нового объекта RNNoise в скомпилированной исходной библиотеке.
        Может быть полезно, когда шумоподавление используется на большом количестве аудиозаписей для предотвращения ухудшения
        качества работы.
        
        Эффективность и надобность в данном методе не доказана. Реализовано просто на всякий случай :) '''

        self.rnnoise_lib.rnnoise_destroy(self.rnnoise_obj)
        self.rnnoise_obj = self.rnnoise_lib.rnnoise_create(None)


    def filter_frame(self, frame):
        ''' Очистка одного фрейма от шума с помощью RNNoise. Фрейм должен быть длиной 10 миллисекунд в формате 16 бит 48 кГц.
        1. frame - байтовая строка с аудиоданными
        2. возвращает tuple из вероятности наличия голоса во фрейме и очищенный от шума фрейм
        
        Вероятность наличия голоса во фрейме (в denoise.c названо 'vad_probability') - это число от 0 до 1, отражающее вероятность
        того, что фрейм содержит голос (или, возможно, громкий звук). Может использоваться для реализации встроенного VAD. '''

        # 480 = len(frame)/2, len(frame) всегда должна быть 960 значений (т.к. ширина фрейма 2 байта (16 бит))
        # (т.е. длина фрейма 10 мс (0.01 сек) при частоте дискретизации 48000 Гц, 48000*0.01*2=960).
        # Если len(frame) != 960, будет ошибка сегментирования либо сильные искажения на итоговой аудиозаписи.

        # Если вынести np.ndarray((480,), 'h', frame).astype(ctypes.c_float) в __get_frames(), то прирост в скорости работы составит
        # не более 5-7% на аудиозаписях, длиной от 60 секунд. На более коротких аудиозаписях прирост скорости менее заметен и несущественен.

        frame_buf = np.ndarray((480,), 'h', frame).astype(ctypes.c_float)
        frame_buf_ptr = frame_buf.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

        vad_probability = self.rnnoise_lib.rnnoise_process_frame(self.rnnoise_obj, frame_buf_ptr, frame_buf_ptr)
        return vad_probability, frame_buf.astype(ctypes.c_short).tobytes()


    def filter(self, audio, sample_rate=None, voice_prob_threshold=0.0, save_source_sample_rate=True):
        ''' Получить фреймы из аудиозаписи и очистить их от шума. Для шумоподавления используется RNNoise.
        
        RNNoise дополнительно для каждого фрейма возвращает вероятность наличия голоса в этом фрейме (в виде числа от 0 до 1) и
        с помощью voice_prob_threshold можно отфильтровать фреймы по этому значению. Если вероятность ниже, чем voice_prob_threshold,
        то фрейм будет удалён из аудиозаписи.
        
        ВНИМАНИЕ! Частота дискретизации аудиозаписи принудительно приводится к 48 кГц. Другие значения не поддерживаются RNNoise.
        Однако частота дискретизации возвращаемой аудиозаписи может быть обратно приведена к исходной.

        ВНИМАНИЕ! Для успешной работы RNNoise необходима аудиозапись длиной минимум 1 секунда, на которой присутсвует как голос, так и шум
        (причём шум в идеале должен быть так же и перед голосом). В противном случае качество шумоподавления будет очень низким.
        
        ВНИМАНИЕ! В случае, если передаются части одной аудиозаписи (шумоподавление аудио в потоке), то их длина должна быть не менее 10 мс
        и кратна 10 (т.к. библиотека RNNoise поддерживает только фреймы длиной 10 мс). Такой вариант работы на качество шумоподавления
        практически не влияет.

        1. audio - объект pydub.AudioSegment с аудиозаписью или байтовая строка с аудиоданными (без заголовков wav)
        2. sample_rate - частота дискретизации (обязательно только когда audio - байтовая строка)
        3. voice_prob_threshold - порог вероятности наличия голоса в каждом фрейме (значение от 0 до 1, если 0 - использовать все фреймы)
        4. save_source_sample_rate - True: приводить частоту дискретизации возвращаемой аудиозаписи к исходной
        5. возвращает pydub.AudioSegment или байтовую строку (без заголовков wav), очищенную от шума (тип возвращаемого объекта соответствует типу audio) '''

        frames, source_sample_rate = self.__get_frames(audio, sample_rate)
        if not save_source_sample_rate:
            source_sample_rate = None

        denoised_audio = self.__filter_frames(frames, voice_prob_threshold, source_sample_rate)

        if isinstance(audio, AudioSegment):
            return denoised_audio
        else:
            return denoised_audio.raw_data


    def __filter_frames(self, frames, voice_prob_threshold=0.0, sample_rate=None):
        ''' Очистка фреймов от шума. Для шумоподавления используется RNNoise.
        
        RNNoise дополнительно для каждого фрейма возвращает вероятность наличия голоса в этом фрейме (в виде числа от 0 до 1) и
        с помощью voice_prob_threshold можно отфильтровать фреймы по этому значению. Если вероятность ниже, чем voice_prob_threshold,
        то фрейм будет удалён из аудиозаписи.

        ВНИМАНИЕ! Для успешной работы RNNoise необходима аудиозапись длиной минимум 1 секунда, на которой присутсвует как голос, так и шум
        (причём шум в идеале должен быть так же и перед голосом). В противном случае качество шумоподавления будет очень низким.
        
        ВНИМАНИЕ! В случае, если передаются части одной аудиозаписи, то их длина должна быть не менее 10 мс (длина одного фрейма) и кратна 10
        (т.к. RNNoise поддерживает только фреймы длиной 10 мс). Такой вариант работы на качество шумоподавления не влияет и может использоваться
        для шумоподавления аудио в потоке.

        1. frames - список фреймов длиной по 10 миллисекунд
        2. voice_prob_threshold - порог вероятности наличия голоса в каждом фрейме (значение от 0 до 1, если 0 - использовать все фреймы)
        3. sample_rate - желаемая частота дискретизации очищенной аудиозаписи (если None - не менять частоту дискретизации)
        4. возвращает объект pydub.AudioSegment с аудиозаписью, очищенной от шума '''

        denoised_frames_with_probability = [self.filter_frame(frame) for frame in frames]
        denoised_frames = [frame_with_prob[1] for frame_with_prob in denoised_frames_with_probability if frame_with_prob[0] >= voice_prob_threshold]
        denoised_audio_bytes = b''.join(denoised_frames)

        denoised_audio = AudioSegment(data=denoised_audio_bytes, sample_width=self.sample_width, frame_rate=self.sample_rate, channels=self.channels)

        if sample_rate:
            denoised_audio = denoised_audio.set_frame_rate(sample_rate)
        return denoised_audio


    def __get_frames(self, audio, sample_rate=None):
        ''' Получить фреймы из аудиозаписи. Фреймы представляют собой байтовые строки с аудиоданными фиксированной длины.
        RNNoise поддерживает только фреймы длиной 10 миллисекунд.

        ВНИМАНИЕ! Частота дискретизации аудиозаписи принудительно приводится к 48 кГц. Другие значения не поддерживаются RNNoise.

        1. audio - объект pydub.AudioSegment с аудиозаписью или байтовая строка с аудиоданными (без заголовков wav)
        2. sample_rate - частота дискретизации (обязательно только когда audio - байтовая строка):
            если частота дискретизации не поддерживается - она будет приведена к поддерживаемым 48 кГц
        3. возвращает tuple из списка фреймов и исходной частоты дискретизации аудиозаписи '''

        if isinstance(audio, AudioSegment):
            sample_rate = source_sample_rate = audio.frame_rate
            if sample_rate != self.sample_rate:
                audio = audio.set_frame_rate(self.sample_rate)
            audio_bytes = audio.raw_data
        elif isinstance(audio, bytes):
            if not sample_rate:
                raise ValueError("when type(audio) = 'bytes', 'sample_rate' can not be None")
            audio_bytes = audio
            source_sample_rate = sample_rate
            if sample_rate != self.sample_rate:
                audio = AudioSegment(data=audio_bytes, sample_width=self.sample_width, frame_rate=sample_rate, channels=self.channels)
                audio = audio.set_frame_rate(self.sample_rate)
                audio_bytes = audio.raw_data
        else:
            raise TypeError("'audio' can only be AudioSegment or bytes")

        frame_width = int(self.sample_rate * (self.frame_duration_ms / 1000.0) * 2)
        if len(audio_bytes) % frame_width != 0:
            silence_duration = frame_width - len(audio_bytes) % frame_width
            audio_bytes += b'\x00' * silence_duration

        offset = 0
        frames = []
        while offset + frame_width <= len(audio_bytes):
            frames.append(audio_bytes[offset:offset + frame_width])
            offset += frame_width
        return frames, source_sample_rate


    def read_wav(self, f_name_wav, sample_rate=None):
        ''' Загрузить .wav аудиозапись. Поддерживаются только моно аудиозаписи 2 байта/16 бит. Если параметры у загружаемой аудиозаписи
        отличаются от указанных - она будет приведена в требуемый формат.
        1. f_name_wav - имя .wav аудиозаписи или BytesIO
        2. sample_rate - желаемая частота дискретизации (если None - не менять частоту дискретизации)
        3. возвращает объект pydub.AudioSegment с аудиозаписью '''

        if isinstance(f_name_wav, str) and f_name_wav.rfind('.wav') == -1:
            raise ValueError("'f_name_wav' must contain the name .wav audio recording")

        audio = AudioSegment.from_wav(f_name_wav)

        if sample_rate:
            audio = audio.set_frame_rate(sample_rate)
        if audio.sample_width != self.sample_width:
            audio = audio.set_sample_width(self.sample_width)
        if audio.channels != self.channels:
            audio = audio.set_channels(self.channels)
        return audio


    def write_wav(self, f_name_wav, audio_data, sample_rate=None):
        ''' Сохранить .wav аудиозапись.
        1. f_name_wav - имя .wav аудиозаписи, в который будет сохранена аудиозапись или BytesIO
        2. audio_data - объект pydub.AudioSegment с аудиозаписью или байтовая строка с аудиоданными (без заголовка wav)
        3. sample_rate - частота дискретизации аудиозаписи:
            когда audio_data - байтовая строка, должна соответствовать реальной частоте дискретизации аудиозаписи
            в остальных случаях частота дискретизации будет приведена к указанной (если None - не менять частоту дискретизации) '''

        if isinstance(audio_data, AudioSegment):
            self.write_wav_from_audiosegment(f_name_wav, audio_data, sample_rate)
        elif isinstance(audio_data, bytes):
            if not sample_rate:
                raise ValueError("when type(audio_data) = 'bytes', 'sample_rate' can not be None")
            self.write_wav_from_bytes(f_name_wav, audio_data, sample_rate)
        else:
            raise TypeError("'audio_data' is of an unsupported type. Supported:\n" + \
                            "\t- pydub.AudioSegment with audio\n" + \
                            "\t- byte string with audio data (without wav header)")


    def write_wav_from_audiosegment(self, f_name_wav, audio, desired_sample_rate=None):
        ''' Сохранить .wav аудиозапись.
        1. f_name_wav - имя .wav файла, в который будет сохранена аудиозапись или BytesIO
        2. audio - объект pydub.AudioSegment с аудиозаписью
        3. desired_sample_rate - желаемая частота дискретизации (если None - не менять частоту дискретизации) '''

        if desired_sample_rate:
            audio = audio.set_frame_rate(desired_sample_rate)
        audio.export(f_name_wav, format='wav')


    def write_wav_from_bytes(self, f_name_wav, audio_bytes, sample_rate, desired_sample_rate=None):
        ''' Сохранить .wav аудиозапись.
        1. f_name_wav - имя .wav файла, в который будет сохранена аудиозапись или BytesIO
        2. audio_bytes - байтовая строка с аудиозаписью (без заголовков wav)
        3. sample_rate - частота дискретизации
        4. desired_sample_rate - желаемая частота дискретизации (если None - не менять частоту дискретизации) '''

        audio = AudioSegment(data=audio_bytes, sample_width=self.sample_width, frame_rate=sample_rate, channels=self.channels)
        if desired_sample_rate and desired_sample_rate != sample_rate:
            audio = audio.set_frame_rate(desired_sample_rate)

        audio.export(f_name_wav, format='wav')




def main():
    folder_name_with_audio = 'test_audio/functional_tests'
    f_name_rnnoise_binary = 'librnnoise_default.so.0.4.1'

    denoiser = RNNoise(f_name_rnnoise_binary)

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


    denoiser.reset()  # not necessarily, need has not yet been proven


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
    
    print("\nAudio: '{}', length: {:.2f} s:".format(f_name_audio, len(audio)/1000))
    print("\tdenoised audio                                '{}'".format(f_name_denoised_audio))
    print('\tprocessing time                               {:.2f} s'.format(elapsed_time))
    print('\taverage processing time of 1 buffer ({} ms)   {:.2f} ms'.format(buffer_size_ms, average_elapsed_time_per_frame*1000))
    print('\tprocessing speed                              {:.1f} RT'.format(len(audio)/1000/elapsed_time))
    print('\taverage processing speed of 1 buffer ({} ms)  {:.1f} RT'.format(buffer_size_ms, buffer_size_ms/(average_elapsed_time_per_frame*1000)))


    # Test for working with audio in the form of pydub.AudioSegment
    for f_name_audio in f_names_source_audio[1:6]:
        audio = denoiser.read_wav(f_name_audio)

        start_time = time.time()
        denoised_audio = denoiser.filter(audio)
        elapsed_time = time.time() - start_time

        f_name_denoised_audio = f_name_audio[:f_name_audio.rfind('.wav')] + '_denoised.wav'
        denoiser.write_wav(f_name_denoised_audio, denoised_audio)

        print("\nAudio: '{}', length: {:.2f} s:".format(f_name_audio, len(audio)/1000))
        print("\tdenoised audio    '{}'".format(f_name_denoised_audio))
        print('\tprocessing time   {:.2f} s'.format(elapsed_time))
        print('\tprocessing speed  {:.1f} RT'.format(len(audio)/1000/elapsed_time))


if __name__ == '__main__':
    main()
