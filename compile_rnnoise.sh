#!/bin/bash

ZIP_RNNOISE_SOURCE="rnnoise_master_20.11.2020.zip"

if [ ! -f $ZIP_RNNOISE_SOURCE ]; then
    echo -e "\n[E] Archive ${ZIP_RNNOISE_SOURCE} not found\n"
    exit 1
fi

unzip $ZIP_RNNOISE_SOURCE
cd rnnoise-master
./autogen.sh
./configure
make
cd -
mkdir -p rnnoise_wrapper/libs
mv rnnoise-master/.libs/librnnoise.so.0.4.1 rnnoise_wrapper/libs/librnnoise_default.so.0.4.1
rm -rf rnnoise-master

echo -e "\n'librnnoise.so.0.4.1' has been successfully moved to 'rnnoise_wrapper/libs/librnnoise_default.so.0.4.1'"
