# RNNoise Wrapper

Это простая обёртка на Python для [RNNoise](https://github.com/xiph/rnnoise). Поддерживается только Python 3. Код основан на [issue от snakers4](https://github.com/xiph/rnnoise/issues/69) из репозитория RNNoise, за что ему отдельное спасибо.

[RNNoise](https://people.xiph.org/~jm/demo/rnnoise/) - это рекуррентная нейронная сеть с ячейками GRU, предназначенная для подаления шума в аудиозаписи в реальном времени (работает даже на Raspberry Pi). Она обучена на 6.4Гб зашумленных аудиозаписях и полностью готова к использованию.

RNNoise написан на C и имеет методы для шумоподавления одного фрейма длиной 10 миллисекунд. Фрейм должен быть с частотой дискретизации 48000Гц, моно, 16 бит.

**RNNoise_Wrapper** упрощает работу с RNNoise: избавляет пользователя от необходимости самому извлекать фреймы/кадры из аудиозаписи, снимает ограничения на параметры обрабатываемой wav аудиозаписи, скрывает все нюансы работы с библиотекой на C и, в случае использования Linux или Mac, избавляет пользователя от необходимости вручную компилировать RNNoise.

Данная обёртка на CPU Intel i5-5200U **работает в 26-28 раз быстрее реального времени** при шумоподавлении целой аудиозаписи, и **в 16 раз быстрее реального времени** при работе в потоковом режиме (т.е. обработки фрагментов аудио длиной 10 мс). При этом было задействовано только 1 ядро, нагрузка на которое составила около 100%.

## Установка

Данная обёртка имеет следующие зависимости: [pydub](https://github.com/jiaaro/pydub) и [numpy](https://github.com/numpy/numpy).

Установка с помощью pip:
```bash
pip install git+https://github.com/Desklop/RNNoise_Wrapper
```

**ВНИМАНИЕ!** Перед использованием обёртки, RNNoise необходимо скомпилировать. Если вы используете **Linux или Mac**, вы можете использовать **заранее скомпилированный RNNoise** (в ОС Ubuntu 18.04.2 LTS 64 bit), который **поставляется с пакетом** (он так же работает в Google Colaboratory). Если по какой-либо причине стандартный бинарный файл у вас не работает, попробуйте вручную скомпилировать RNNoise. Для этого необходимо сначала подготовить вашу ОС (предполагается, что `gcc` уже установлен):
```bash
sudo apt-get install autoconf libtool
```
И выполнить:
```bash
git clone https://github.com/Desklop/RNNoise_Wrapper
cd RNNoise_Wrapper
./compile_rnnoise.sh
```
После этого в папке `rnnoise_wrapper/libs` появятся файлы `librnnoise.*`. Из них нужен только файл с именем `librnnoise.so.0.4.1` (или аналогичным, с версией библиотеки в конце). Путь к данному бинарному файлу нужно передать при создании объекта класса RNNoise из данной обёртки (подробнее см. ниже) (данный файл можно скопировать в свой проект, в котором вы используете обёртку).

Если вы используете **Windows**, то вам нужно **вручную скомпилировать RNNoise**. Но вышеописанная инструкция не будет работать, **воспользуйтесь** данными **ссылками**: [один](https://github.com/xiph/rnnoise/issues/34), [два](https://github.com/jagger2048/rnnoise-windows). После компиляции путь к бинарному файлу нужно передать при создании объекта класса RNNoise из данной обёртки (подробнее см. ниже).

## Использование

**1.** Из вашего кода Python (подавление шума в аудиозаписи `test.wav` и сохранение результата как `test_denoised.wav`):
```python
from rnnoise_wrapper import RNNoise

denoiser = RNNoise()

audio = denoiser.read_wav('test.wav')
filtered_audio = denoiser.filter(audio)
denoiser.write_wav('test_denoised.wav', filtered_audio)
```

Подавление шума в потоковом аудио (размер буфера равен 10 миллисекунд, т.е. 1 фрейм) (в примере используется имитация потока путём обработки аудиозаписи `test.wav` по частям с сохранением результата как `test_denoised_f.wav`):
```python
audio = denoiser.read_wav('test.wav')

filtered_audio = b''
buffer_size_ms = 10

for i in range(buffer_size_ms, len(audio), buffer_size_ms):
    filtered_audio += denoiser.filter(audio[i-buffer_size_ms:i].raw_data, sample_rate=audio.frame_rate)
if len(audio) % buffer_size_ms != 0:
    filtered_audio += denoiser.filter(audio[len(audio)-(len(audio)%buffer_size_ms):].raw_data, sample_rate=audio.frame_rate)

denoiser.write_wav('test_denoised_f.wav', filtered_audio, sample_rate=audio.frame_rate)
```

Больше примеров работы с обёрткой можно найти [тут](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper/rnnoise_wrapper.py#L331).

Класс [RNNoise](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper/rnnoise_wrapper.py#L30) содержит следующие методы:

- [`read_wav()`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper/rnnoise_wrapper.py#L263): принимает имя .wav аудиозаписи, приводит её в поддерживаемый формат (16 бит, моно) и возвращает объект `pydub.AudioSegment` с аудиозаписью
- [`write_wav()`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper/rnnoise_wrapper.py#L284): принимает имя .wav аудиозаписи, объект `pydub.AudioSegment` (или байтовую строку с аудиоданными без заголовков wav) и сохраняет аудиозапись под переданным именем
- [`filter()`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper/rnnoise_wrapper.py#L157): принимает объект `pydub.AudioSegment` (или байтовую строку с аудиоданными без заголовков wav), приводит его к частоте дискретизации 48000 Гц, разбивает аудиозапись на фреймы (длиной 10 миллисекунд), очищает их от шума и возвращает объект `pydub.AudioSegment` (или байтовую строку без заголовков wav) с сохранением исходной частоты дискретизации
- [`filter_frame()`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper/rnnoise_wrapper.py#L135): очистка только одного фрейма (длиной 10 мс, 16 бит, моно, 48000 Гц) от шума (обращение напрямую к бинарному файлу библиотеки RNNoise)

При создании объекта класса `RNNoise` из обёртки можно передать путь к скомпилированному бинарному файлу библиотеки RNNoise, который необходимо использовать:
```python
denoiser = RNNoise(path_to_lib='path/to/librnnoise.so.0.4.1')
```

Подробная информация о поддерживаемых аргументах и работе каждого метода находится в комментариях в исходном коде этих методов.

Особенности метода `filter()`:

- для успешной работы необходима аудиозапись длиной минимум 1 секунда, на которой присутсвует как голос, так и шум (причём шум в идеале должен быть так же и перед голосом). В противном случае качество шумоподавления будет очень низким
- в случае, если передаются части одной аудиозаписи (шумоподавление аудио в потоке), то их длина должна быть не менее `10` мс и кратна `10` (т.к. библиотека RNNoise поддерживает только фреймы длиной `10` мс). Такой вариант работы на качество шумоподавления практически не влияет
- если последний фрейм переданной аудиозаписи меньше `10` мс (или передана часть аудио длиной меньше `10` мс), то он дополняется нулями до необходимого размера. Из-за этого возможно небольшое увеличение длины итоговой аудиозаписи после шумоподавления
- библиотека RNNoise дополнительно для каждого фрейма возвращает вероятность наличия голоса в этом фрейме (в виде числа от `0` до `1`) и с помощью аргумента `voice_prob_threshold` можно отфильтровать фреймы по этому значению. Если вероятность ниже, чем `voice_prob_threshold`, то фрейм будет удалён из аудиозаписи

---

**2.** В качестве инструмента командной строки:
```bash
python3 -m rnnoise_wrapper.cli input.wav output.wav
```
или
```bash
webrtcvad_wrapper input.wav output.wav
```

Где:

- `input.wav` - имя исходной .wav аудиозаписи
- `output.wav` - имя .wav аудиофайла, в который будет сохранена исходная аудиозапись после шумоподавления

---

Если у вас возникнут вопросы или вы хотите сотрудничать, можете написать мне на почту: vladsklim@gmail.com или в [LinkedIn](https://www.linkedin.com/in/vladklim/).