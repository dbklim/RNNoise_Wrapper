#!/bin/bash

ALL_NUM_HOURS=("5h" "50h" "100h")
ALL_SIZES=("500k" "1kk" "5kk")

for SIZE in "${ALL_SIZES[@]}"; do
    for NUM_HOURS in "${ALL_NUM_HOURS[@]}"; do
        POSTFIX="${NUM_HOURS}_b_${SIZE}"
        echo -e "[i] Training on training_${POSTFIX}.h5\n"
        env_train/bin/python3 rnnoise-master/training/rnn_train_mod.py train_logs/training_set_oct30_${NUM_HOURS}_balanced/training_${POSTFIX}.h5 train_logs/training_set_oct30_${NUM_HOURS}_balanced/weights_${POSTFIX}.hdf5

        echo -e "\n\n\n[i] Dump weights_${POSTFIX}.hdf5 to nn_data.c and rnn_data.h\n"
        env_train/bin/python3 rnnoise-master/training/dump_rnn_mod.py train_logs/training_set_oct30_${NUM_HOURS}_balanced/weights_${POSTFIX}.hdf5 rnnoise-master/src/rnn_data.c rnnoise-master/src/rnn_data.h

        echo -e "\n\n[i] Compiling librnnoise_${POSTFIX}.so.0.4.1\n"
        cd rnnoise-master/
        make clean
        ./autogen.sh && ./configure && make
        cd -
        cp rnnoise-master/.libs/librnnoise.so.0.4.1 train_logs/training_set_oct30_${NUM_HOURS}_balanced/librnnoise_${POSTFIX}.so.0.4.1
    done
done

echo -e "\n[i] Done."
