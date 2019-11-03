#!/bin/bash

SOURCE_DIRECTORY='rnnoise_source'

if ! [ -d rnnoise_source ]; then
echo "[E] Directory '$SOURCE_DIRECTORY' not found"
exit 1
fi

cd $SOURCE_DIRECTORY
./autogen.sh
./configure
make
cd -
mkdir -p rnnoise_wrapper/libs
mv $SOURCE_DIRECTORY/.libs/librnnoise.so.0.* rnnoise_wrapper/libs
rm -rf $SOURCE_DIRECTORY

echo -e "\n'librnnoise.so.0.*' files has been successfully moved to 'rnnoise_wrapper/libs'"
