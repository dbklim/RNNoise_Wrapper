# Обучение RNNoise

Для обучения использовался датасет от [Microsoft DNS Challenge](https://github.com/microsoft/DNS-Challenge). Обучение выполнялось на машине с CPU Intel Core i7-10510U и 16Gb RAM, ОС Ubuntu 19.10 64bit.

**В инструкции подразумевается, что у вас уже склонированы репозитории** с Microsoft DNS Challenge и текущий репозиторий RNNoise_Wrapper.

### **1. Подготовка датасета Microsoft DNS Challenge**

**Подготовка данных в Microsoft DNS Challenge** путём обновления `noisyspeech_synthesizer.cfg` и выполнения `python3 noisyspeech_synthesizer_singleprocess.py` в соответствии с [исходной инструкцией в репозитории](https://github.com/microsoft/DNS-Challenge#usage).

**Примечание 1.1. Скрипты в DNS Challenge нуждаются в простых правках:**

- замена обратного слэша на обычный во всех путях в `noisyspeech_synthesizer.cfg` и `noisyspeech_synthesizer_singleprocess.py`
- добавление вывода текущего обрабатываемого аудио `print('Processing file #{}...'.format(file_num))` после 165 строки в [`noisyspeech_synthesizer_singleprocess.py`](https://github.com/microsoft/DNS-Challenge/blob/master/noisyspeech_synthesizer_singleprocess.py#L165) (для удобства, процесс подготовки данных довольно медленный)
- добавление `return np.zeros(0), 16000` в обработку исключения в `audioread()` после 43 строки в [`audiolib.py`](https://github.com/microsoft/DNS-Challenge/blob/master/audiolib.py#L43)

**Примечание 1.2.** По умолчанию в конфиге можно выбрать только одну папку с чистой речью, т.е. только [один из доступных языков](https://github.com/microsoft/DNS-Challenge/tree/master/datasets/clean). **Для того, что бы использовать все доступные аудио с чистой речью (около 750 часов), нужно папки с речью на других языках переместить в папку с английской речью или в новую отдельную папку.**

Перемещение папок с речью на других языках в папку с английской речью (выполнять в `DNS-Challenge/datasets/clean`):

```bash
mv -v french_data german_speech italian_speech russian_speech spanish_speech read_speech
```

Вернуть всё обратно:

```bash
mv -v read_speech/french_data read_speech/german_speech read_speech/italian_speech read_speech/russian_speech read_speech/spanish_speech ../clean
```

**Примечание 1.3.** Если нужно выполнить обучение не на всех доступных данных (а только, например, на 5 часах из них), но с использованием всех доступных языков, **рекомендуется предварительно обрезать количество аудиозаписей для каждого языка по самому наименьшему из них** (меньше всего данных для русского языка, около 47 часов). То есть **сбалансировать языки по числу аудиозаписей** в них.

Это можно сделать скриптом [`training_utils/balance_dns_challenge_dataset.py`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/training_utils/balance_dns_challenge_dataset.py) (скрипт лучше скопировать в папку с датасетом, выполнять в `DNS-Challenge`):

```bash
python3 balance_dns_challenge_dataset.py -rf datasets/clean -sf russian_speech,read_speech,french_data,german_speech,italian_speech,spanish_speech -bsf all_balanced_speech
```

Сбалансированная чистая речь будет сохранена в папке `all_balanced_speech`. Исходная структура аудиозаписей нарушается (все аудиозаписи будут внутри указанной папки, без подпапок), а исходные имена аудиозаписей сохраняются.

**ВАЖНО!** Примечание 2 и примечание 3 **взаимоисключающие**. Что бы не возникло проблем, **рекомендуется использовать только примечание 3.**

**После подготовки данных рекомендуется скопировать их в папку `RNNoise_Wrapper/datasets`.** Для удобства, датасету присвоено **имя `test_training_set`**, то есть полный путь к датасету будет `RNNoise_Wrapper/datasets/test_training_set`.

### **2. Подготовка окружения для RNNoise**

Перед работой с RNNoise, нужно либо склонировать исходный [репозиторий](https://github.com/xiph/rnnoise), либо распаковать его копию в текущем проекте:

```bash
unzip rnnoise_master_20.11.2020.zip
```

Для компиляции RNNoise и его инструментов нужно сначала подготовить ОС (предполагается, что `gcc` уже установлен):

```bash
sudo apt-get install autoconf libtool
```

Затем выполнить сборку инструментов RNNoise (выполнять в `RNNoise_Wrapper`):

```bash
cd rnnoise-master/src && ./compile.sh && cd -
```

И подготовить виртуальное окружение Python для обучения:

```bash
virtualenv --python=python3.7 env_train
source env_train/bin/activate
pip install -r requirements_train.txt
```

### **3. Объединение аудиозаписей в датасете**

**RNNoise для обучения требует 2 аудиозаписи: с чистой речью и с шумами.** Аудиозаписи должны быть в формате .raw, моно, 16 бит и 48000 Гц. То есть для обучения необходимо объединить аудиозаписи в датасете в 2 большие.

Объединить и подготовить все аудиозаписи с чистой речью и все аудиозаписи с шумами можно скриптом [`prepare_dataset_for_training.py`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/training_utils/prepare_dataset_for_training.py) (выполнять в `RNNoise_Wrapper`):

```bash
python3 training_utils/prepare_dataset_for_training.py -cf datasets/test_training_set/clean -nf datasets/test_training_set/noise -bca datasets/test_training_set/all_clean.raw -bna datasets/test_training_set/all_noise.raw
```

### **4. Формирование обучающей выборки**

После объединения аудиозаписей **необходимо извлечь из них коэффициенты и сформировать готовую обучающую выборку.** Ключевым параметром является размер матрицы с данными. По умолчанию он равен `500000х87`. **Рекомендуется изменять первую размерность в зависимости от размера датасета.**

**Примечание 4.1.** Я пробовал обучать с `500000`, `1000000` и `5000000`. Рекомендую попробовать шаг меньше: `500000`, `1000000`, `2000000`. Или даже `500000`, `1000000`, `1500000`, `2000000`. Так будет проще потом отобрать наиболее удачную/качественную модель.

Формирование обучающей выборки (выполнять в `RNNoise_Wrapper`):

```bash
rnnoise-master/src/denoise_training datasets/test_training_set/all_clean.raw datasets/test_training_set/all_noise.raw 5000000 > train_logs/test_training_set/training_test_b_500k.f32
```

Конвертирование обучающей выборки в `.h5` (выполнять в `RNNoise_Wrapper`):

```bash
python3 rnnoise-master/training/bin2hdf5.py train_logs/test_training_set/training_test_b_500k.f32 5000000 87 train_logs/test_training_set/training_test_b_500k.h5
```

### **5. Обучение модели**

Перед запуском обучения нужно **скопировать обновлённый скрипт** из [`training_utils/rnn_train_mod.py`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/training_utils/rnn_train_mod.py) в `rnnoise-master/training`.

Обновлённый скрипт обучения **отличается** от исходного **поддержкой аргументов командной строки и доработанными логами**.

Запуск обучения (выполнять в `RNNoise_Wrapper`):

```bash
python3 rnnoise-master/training/rnn_train_mod.py train_logs/test_training_set/training_test_b_500k.h5 train_logs/test_training_set/weights_test_b_500k.hdf5
```

Обучение длится **120 эпох**. После завершения обучения **веса полученной модели сохраняются в `train_logs/test_training_set/weights_test_b_500k.hdf5`**. На указанной ранее машине обучение заняло около 45 минут.

**Примечание 5.1.** Для запуска обучения на GPU необходимо установить `tensorflow-gpu==1.15.4`. На NVIDIA RTX2080Ti процесс обучения использовал около 10Гб видеопамяти.

### **6. Конвертирование модели**

RNNoise написан на С, поэтому полученную обученную tenosrflow **модель необходимо конвертировать в исходный код на С**.

Исходный конвертер в репозитории с проектом приводит к ошибкам при попытке компиляции RNNoise с новой моделью. **Исправленный конвертер нужно скопировать** из [`training_utils/dump_rnn_mod.py`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/training_utils/dump_rnn_mod.py) в `rnnoise-master/training`. Исправления основаны на [issue в исходном репозитории RNNoise](https://github.com/xiph/rnnoise/issues/74#issuecomment-517075991).

Конвертирование модели (выполнять в `RNNoise_Wrapper`):

```bash
python3 rnnoise-master/training/dump_rnn_mod.py train_logs/test_training_set/weights_test_b_500k.hdf5 rnnoise-master/src/rnn_data.c rnnoise-master/src/rnn_data.h
```

**Примечение 6.1.** Изменять названия и местоположение конечных `.c` и `.h` файлов не рекомендуется. Иначе понадобится изменять скрипты для компиляции RNNoise.

### **7. Сборка RNNoise с новой моделью**

Для проверки и использования новой модели **нужно скомпилировать RNNoise** с обновлёнными `src/rnn_data.c` и `src/rnn_data.h` (выполнять в `RNNoise_Wrapper`):

```bash
cd rnnoise-master && make clean && ./autogen.sh && ./configure && make && cd -
```

После успешной сборки, для удобства можно скопировать полученный бинарник в папку с обученной моделью и её весами:

```bash
cp rnnoise-master/.libs/librnnoise.so.0.4.1 train_logs/test_training_set/librnnoise_test_b_500k.so.0.4.1
```

### **8. Тестирование новой модели**

**Для оценки качества работы** полученной модели рекомендуется **выполнить сравнительный тест со стандартной моделью** с помощью [`rnnoise_wrapper_comparative_test.py`](https://github.com/Desklop/RNNoise_Wrapper/blob/master/rnnoise_wrapper_comparative_test.py).

## Для справки

**Репозиторий так же содержит [`Dockerfiles`](https://github.com/Desklop/RNNoise_Wrapper/tree/master/training_utils) для запуска обучения в docker контейнере**, как на CPU, так и на GPU. Это **может быть полезно на старых CPU**, которые не поддерживают AVX инструкции и на которых не установится TensorFlow из pip (в этом случае можно поискать подходящий пакет tensorflow в [`optimized_tensorflow_wheels`](https://github.com/Desklop/optimized_tensorflow_wheels) или в Google).

**Список полезных bash команд:**

1. Копирование папок вместе с содержимым: `cp -R source source_copy`
2. Перемещение папок вместе с содержимым: `mv -v source_1 source_2 source_N all_source`
3. Копирование 10 случайных файлов из текущей папки: `ls | shuf -n 10 | xargs -i cp {} /datasets/random_audio`
4. Подсчёт размера папки: `du -hs datasets/clean`
5. Подсчёт количества файлов в текущей папке и всех её подпапках: `ls -laR | grep "^-" | wc`
6. Архивировать папку в .zip: `zip -r test_training_set.zip datasets/test_training_set`
7. Распаковать архив в текущую папку: `unzip test_training_set.zip`

## Источники

Документация и issues, на основе которых составлена данная инструкция:

1. https://github.com/xiph/rnnoise/blob/master/TRAINING-README
2. https://github.com/xiph/rnnoise/issues/1#issuecomment-467170166
3. https://github.com/xiph/rnnoise/issues/8#issuecomment-346947946
4. https://github.com/xiph/rnnoise/issues/74

---

Если у вас возникнут вопросы или вы хотите сотрудничать, можете написать мне на почту: vladsklim@gmail.com или в [LinkedIn](https://www.linkedin.com/in/vladklim/).
