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

from .rnnoise_wrapper import RNNoise
