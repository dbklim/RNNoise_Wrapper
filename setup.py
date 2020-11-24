#!/usr/bin/python3
# -*- coding: utf-8 -*-
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#       OS : GNU/Linux Ubuntu 16.04 or 18.04
# LANGUAGE : Python 3.5.2 or later
#   AUTHOR : Klim V. O.
#     DATE : 14.10.2019
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from setuptools import setup, find_packages
from typing import List


__version__ = 1.1


def readme() -> List[str]:
    with open('README.md', 'r', encoding='utf-8') as f_readme:
        return f_readme.read()


def requirements() -> List[str]:
    with open('requirements.txt', 'r', encoding='utf-8') as f_requirements:
        return f_requirements.read()


setup(
    name='rnnoise-wrapper',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts':
            ['rnnoise_wrapper = rnnoise_wrapper.cli:denoise']
        },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
    ],
    version=__version__,
    install_requires=requirements(),
    description='RNNoise_Wrapper is a simple wrapper to audio noise reduction RNNoise',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='Vlad Klim',
    author_email='valdsklim@gmail.com',
    license='Apache 2.0',
    url='https://github.com/Desklop/RNNoise_Wrapper',
    keywords='noise noise-reduction noise-suppression denoiser denoise rnnoise rnn nn rtc dsp audio audio-processing wav nlp',
    project_urls={
        'Source': 'https://github.com/Desklop/RNNoise_Wrapper',
    }
)


print('\nRNNoise_Wrapper is ready for work and defense!')
print('All information about this package is available at https://github.com/Desklop/RNNoise_Wrapper')

# To build package run: python3 setup.py sdist bdist_wheel
