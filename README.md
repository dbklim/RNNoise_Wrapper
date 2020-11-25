# RNNoise Wrapper

Это простая обёртка на Python для шумоподавления [RNNoise](https://github.com/xiph/rnnoise). Поддерживается только Python 3. Код основан на [issue от snakers4](https://github.com/xiph/rnnoise/issues/69) из репозитория RNNoise, за что ему отдельное спасибо.

[RNNoise](https://jmvalin.ca/demo/rnnoise/) - это рекуррентная нейронная сеть с ячейками GRU, предназначенная для подаления шума в аудиозаписи в реальном времени (работает даже на Raspberry Pi). Стандартная модель обучена на 6.4Гб зашумленных аудиозаписей и полностью готова к использованию.

RNNoise написан на C и имеет методы для шумоподавления одного фрейма длиной 10 миллисекунд. Фрейм должен быть с частотой дискретизации 48000Гц, моно, 16 бит.

**RNNoise_Wrapper** упрощает работу с RNNoise:

- избавляет от необходимости самому извлекать фреймы/кадры из аудиозаписи
- снимает ограничения на параметры обрабатываемой wav аудиозаписи
- скрывает все нюансы работы с библиотекой на C
- избавляет от необходимости вручную компилировать RNNoise (только для Linux)
- добавляет 2 новых бинарных файла с более качественными моделями, которые поставляются вместе с пакетом (только для Linux)

**RNNoise_Wrapper содержит 2 новые более качественные модели** (обученные веса и скомпилированные бинарники RNNoise для Linux). Для обучения использовался датасет от [Microsoft DNS Challenge](https://github.com/microsoft/DNS-Challenge).

1. **librnnoise_5h_ru_500k** — обучена на 5 часах русской речи (с подмешиванием эмоциональной речи и пения на английском языке), полученной скриптом из репозитория с датасетом. Обученные веса находятся в [`train_logs/weights_5h_ru_500k.hdf5`](https://github.com/Desklop/RNNoise_Wrapper/tree/master/train_logs/weights_5h_ru_500k.hdf5), скомпилированный RNNoise в [`rnnoise_wrapper/libs/librnnoise_5h_ru_500k.so.0.4.1`](https://github.com/Desklop/RNNoise_Wrapper/tree/master/rnnoise_wrapper/libs/librnnoise_5h_ru_500k.so.0.4.1) (только для Linux)

2. **librnnoise_5h_b_500k** — обучена на 5 часах смешанной речи на английском, русском, немецком, французском, итальянском, испанском языках и мандаринского наречия китайского языка (с подмешиванием эмоциональной речи и пения на английском языке). Датасет для каждого языка предварительно был обрезан по самому наименьшему из них (меньше всего данных для русского языка, около 47 часов). Финальная обучающая выборка получена скриптом из репозитория с датасетом. Обученные веса находятся в [`train_logs/weights_5h_b_500k.hdf5`](https://github.com/Desklop/RNNoise_Wrapper/tree/master/train_logs/weights_5h_b_500k.hdf5), скомпилированный RNNoise в [`rnnoise_wrapper/libs/librnnoise_5h_b_500k.so.0.4.1`](https://github.com/Desklop/RNNoise_Wrapper/tree/master/rnnoise_wrapper/libs/librnnoise_5h_b_500k.so.0.4.1) (только для Linux)

3. **librnnoise_default** — стандартная модель от авторов [RNNoise](https://jmvalin.ca/demo/rnnoise/)

Модели `librnnoise_5h_ru_500k` и `librnnoise_5h_b_500k` имеют **практически одинаковое качество** шумоподавления. `librnnoise_5h_ru_500k` больше всего **подходит для работы с русской речью**, а `librnnoise_5h_b_500k` — **для смешанной речи** либо речи на не русском языке, она более универсальна.

Сравнительные примеры работы новых моделей со стандартной доступны в [`test_audio/comparative_tests`](https://github.com/Desklop/RNNoise_Wrapper/tree/master/test_audio/comparative_tests).

Данная обёртка на CPU Intel i7-10510U **работает в 28-30 раз быстрее реального времени** при шумоподавлении целой аудиозаписи, и **в 18-20 раз быстрее реального времени** при работе в потоковом режиме (т.е. обработки фрагментов аудио длиной 20 мс). При этом было задействовано только 1 ядро, нагрузка на которое составила около 80-100%.

## Установка

Данная обёртка имеет следующие зависимости: [pydub](https://github.com/jiaaro/pydub) и [numpy](https://github.com/numpy/numpy).

Установка с помощью pip:

```bash
pip install git+https://github.com/Desklop/RNNoise_Wrapper
```

**ВНИМАНИЕ!** Перед использованием обёртки, RNNoise необходимо скомпилировать. Если вы используете **Linux или Mac**, вы можете использовать **заранее скомпилированный RNNoise** (в ОС Ubuntu 19.10 64 bit), который **поставляется с пакетом** (он так же работает в Google Colaboratory). Если стандартный бинарный файл у вас не работает, попробуйте вручную скомпилировать RNNoise. Для этого необходимо сначала подготовить вашу ОС (предполагается, что `gcc` уже установлен):

```bash
sudo apt-get install autoconf libtool
```

И выполнить:

```bash
git clone https://github.com/Desklop/RNNoise_Wrapper
cd RNNoise_Wrapper
./compile_rnnoise.sh
```

После этого в папке `rnnoise_wrapper/libs` появится файл `librnnoise_default.so.0.4.1`. Путь к данному бинарному файлу нужно передать при создании объекта класса RNNoise из данной обёртки (подробнее см. ниже).

Если вы используете **Windows**, то вам нужно **вручную скомпилировать RNNoise**. Вышеописанная инструкция не будет работать, **воспользуйтесь** данными **ссылками**: [один](https://github.com/xiph/rnnoise/issues/34), [два](https://github.com/jagger2048/rnnoise-windows). После компиляции путь к бинарному файлу нужно передать при создании объекта класса RNNoise из данной обёртки (подробнее см. ниже).

## Использование

### **1. В коде Python**

**Подавление шума в аудиозаписи** `test.wav` и сохранение результата как `test_denoised.wav`:

```python
from rnnoise_wrapper import RNNoise

denoiser = RNNoise()

audio = denoiser.read_wav('test.wav')
denoised_audio = denoiser.filter(audio)
denoiser.write_wav('test_denoised.wav', denoised_audio)
```

**Подавление шума в потоковом аудио** (размер буфера равен 20 миллисекунд, т.е. 2 фрейма) (в примере используется имитация потока путём обработки аудиозаписи `test.wav` по частям с сохранением результата как `test_denoised_stream.wav`):

```python
audio = denoiser.read_wav('test.wav')

denoised_audio = b''
buffer_size_ms = 20

for i in range(buffer_size_ms, len(audio), buffer_size_ms):
    denoised_audio += denoiser.filter(audio[i-buffer_size_ms:i].raw_data, sample_rate=audio.frame_rate)
if len(audio) % buffer_size_ms != 0:
    denoised_audio += denoiser.filter(audio[len(audio)-(len(audio)%buffer_size_ms):].raw_data, sample_rate=audio.frame_rate)

denoiser.write_wav('test_denoised_stream.wav', denoised_audio, sample_rate=audio.frame_rate)
```

**Больше примеров работы с обёрткой** можно найти в [`rnnoise_wrapper_functional_tests.py`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper_functional_tests.py) и [`rnnoise_wrapper_comparative_test.py`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper_comparative_test.py).

Класс [RNNoise](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper/rnnoise_wrapper.py#L29) содержит следующие методы:

- [`read_wav()`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper/rnnoise_wrapper.py#L256): принимает имя .wav аудиозаписи, приводит её в поддерживаемый формат (16 бит, моно) и возвращает объект `pydub.AudioSegment` с аудиозаписью
- [`write_wav()`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper/rnnoise_wrapper.py#L277): принимает имя .wav аудиозаписи, объект `pydub.AudioSegment` (или байтовую строку с аудиоданными без заголовков wav) и сохраняет аудиозапись под переданным именем
- [`filter()`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper/rnnoise_wrapper.py#L150): принимает объект `pydub.AudioSegment` (или байтовую строку с аудиоданными без заголовков wav), приводит его к частоте дискретизации 48000 Гц, **разбивает аудиозапись на фреймы** (длиной 10 миллисекунд), **очищает их от шума и возвращает** объект `pydub.AudioSegment` (или байтовую строку без заголовков wav) с сохранением исходной частоты дискретизации
- [`filter_frame()`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper/rnnoise_wrapper.py#L128): очистка только одного фрейма (длиной 10 мс, 16 бит, моно, 48000 Гц) от шума (обращение напрямую к бинарному файлу библиотеки RNNoise)

Подробная информация о поддерживаемых аргументах и работе каждого метода находится в комментариях в исходном коде этих методов.

**По умолчанию используется модель `librnnoise_5h_b_500k`**. При создании объекта класса `RNNoise` из обёртки с помощью аргумента `f_name_lib` можно указать другую модель (бинарник RNNoise):

- **`librnnoise_5h_ru_500k`** или **`librnnoise_default`** для использования одной из комплектных моделей
- полное/частичное имя/путь к скомпилированному бинарному файлу RNNoise

```python
denoiser_def = RNNoise(f_name_lib='librnnoise_5h_ru_500k')
denoiser_new = RNNoise(f_name_lib='path/to/librnnoise.so.0.4.1')
```

**Особенности основного метода `filter()`:**

- для максимально качественной работы необходима аудиозапись длиной минимум 1 секунда, на которой присутсвует как голос, так и шум (причём шум в идеале должен быть до и после голоса). В противном случае качество шумоподавления будет хуже
- в случае, если передаются части одной аудиозаписи (шумоподавление потоково аудио), то их длина должна быть не менее `10` мс и кратна `10` (т.к. библиотека RNNoise поддерживает только фреймы длиной `10` мс). Такой вариант работы на качество шумоподавления не влияет
- если последний фрейм переданной аудиозаписи меньше `10` мс (или передана часть аудио длиной меньше `10` мс), то он дополняется нулями до необходимого размера. Из-за этого возможно небольшое увеличение длины итоговой аудиозаписи после шумоподавления
- библиотека RNNoise дополнительно для каждого фрейма возвращает вероятность наличия голоса в этом фрейме (в виде числа от `0` до `1`) и с помощью аргумента `voice_prob_threshold` можно отфильтровать фреймы по этому значению. Если вероятность ниже, чем `voice_prob_threshold`, то фрейм будет удалён из аудиозаписи

### **2. В качестве инструмента командной строки**

```bash
python3 -m rnnoise_wrapper.cli -i input.wav -o output.wav
```

или

```bash
rnnoise_wrapper -i input.wav -o output.wav
```

Где:

- `input.wav` - имя исходной .wav аудиозаписи
- `output.wav` - имя .wav аудиофайла, в который будет сохранена аудиозапись после шумоподавления

## Обучение

Инструкция по обучению RNNoise на своих данных находится в [`TRAINING.md`](https://github.com/Desklop/RNNoise_Wrapper/tree/master/TRAINING.md).

---

Если у вас возникнут вопросы или вы хотите сотрудничать, можете написать мне на почту: vladsklim@gmail.com или в [LinkedIn](https://www.linkedin.com/in/vladklim/).
