#!/usr/bin/python3
# -*- coding: utf-8 -*-
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#       OS : GNU/Linux Ubuntu 16.04 or later
# LANGUAGE : Python 3.5.2 or later
#   AUTHOR : Klim V. O.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

'''
Balancing the number of .wav audio in folders with clear speech in the Microsoft DNS-Challenge dataset by the smallest folder of them.
'''

import os
import sys
import time
import platform
import signal
import curses
import argparse
from random import shuffle
from itertools import chain
from shutil import copyfile, rmtree


def create_and_parse_args(root_folder, folder_names_with_speech, folder_name_for_balanced_speech):
    ''' Creating and parsing command line arguments. Returns updated `root_folder`, `folder_names_with_speech` and `folder_name_for_balanced_speech`. '''

    parser = argparse.ArgumentParser(description='Balancing the number of .wav audio in folders with clear speech by the smallest folder of them. ' + \
                                                 'The selected .wav audio files are copied to a separate folder. The source audio file names are saved.')
    parser.add_argument('-rf', '--root_folder', type=str, default=None,
                        help='Full path to clear speech folders (for example, "/storage/DNS-Challenge/datasets/clean")')
    parser.add_argument('-sf', '--speech_folders', type=str, default=','.join(folder_names_with_speech),
                        help='Subfolders with clear speech, separated by commas (default is "{}")'.format(','.join(folder_names_with_speech)))
    parser.add_argument('-bsf', '--balanced_speech_folder', type=str, default=folder_name_for_balanced_speech,
                        help='Folder name where balanced clear speech will be saved (default is "{}")'.format(folder_name_for_balanced_speech))
    args = parser.parse_args()

    if not args.root_folder:
        root_folder = os.path.join(os.getcwd(), 'datasets/clean/')
        print("[W] Root folder is not specified! The following path is used: '{}'\n".format(root_folder))

    if args.speech_folders:
        folder_names_with_speech = [folder_name.strip() for folder_name in args.speech_folders.split(',')]

    if args.balanced_speech_folder:
        folder_name_for_balanced_speech = args.balanced_speech_folder
        if folder_name_for_balanced_speech[-1] != '/':
            folder_name_for_balanced_speech += '/'
    
    return root_folder, folder_names_with_speech, folder_name_for_balanced_speech




def main():
    curses.setupterm()

    root_folder = '/home/vlad/172.16.10.10/NSNet_dataset/datasets/clean/'
    folder_names_with_speech = [
        'russian_speech',
        'read_speech',
        'french_data',
        'german_speech',
        'italian_speech',
        'spanish_speech'
    ]
    folder_name_for_balanced_speech = 'all_balanced_speech/'

    root_folder, folder_names_with_speech, folder_name_for_balanced_speech = create_and_parse_args(root_folder, folder_names_with_speech,
                                                                                                   folder_name_for_balanced_speech)


    # Search .wav audio in specified folders
    folder_info = {}
    print("[i] Search .wav audio in '{}'...".format(root_folder))
    for folder_name in folder_names_with_speech:
        f_names_wavs = []
        print("\n[i] Search .wav audio in '{}'... 0".format(folder_name))
        for path, folder_names, f_names in os.walk(root_folder+folder_name):
            for f_name in f_names:
                if f_name.rfind('.wav') != -1:
                    if len(f_names_wavs) % 1000 == 0:
                        os.write(sys.stdout.fileno(), curses.tigetstr('cuu1'))
                        print("[i] Search .wav audio in '{}'... {}".format(folder_name, len(f_names_wavs)))

                    f_names_wavs.append(os.path.join(path, f_name))

        os.write(sys.stdout.fileno(), curses.tigetstr('cuu1'))
        print("[i] Search .wav audio in '{}'... {}".format(folder_name, len(f_names_wavs)))
       
        f_names_wavs = [[f_name, os.path.getsize(f_name)] for f_name in f_names_wavs]
        total_size_gb = sum([f_size for f_name, f_size in f_names_wavs]) / 1024 / 1024 / 1024
        print('[i] Total size of found .wav audio {:.1f} Gb'.format(total_size_gb))

        folder_info[folder_name] = {'number_files': len(f_names_wavs), 'wavs': f_names_wavs, 'size_gb': total_size_gb}


    # Trimming number of found .wav audio in each folder by the smallest folder of them
    folder_name_with_min_size = min(folder_info, key=lambda folder_name: folder_info[folder_name]['size_gb'])
    min_size_b = folder_info[folder_name_with_min_size]['size_gb'] * 1024 * 1024 * 1024

    print('\n[i] Trimming number of found .wav audio in each folder to {:.1f} Gb...'.format(folder_info[folder_name_with_min_size]['size_gb']))
    for folder_name in folder_info:
        if folder_name != folder_name_with_min_size:
            f_names_wavs = folder_info[folder_name]['wavs']
            shuffle(f_names_wavs)

            current_size = 0
            for i, (f_name, f_size) in enumerate(f_names_wavs):
                if current_size < min_size_b:
                    current_size += f_size
                else:
                    del f_names_wavs[i:]
                    break
            
            folder_info[folder_name]['number_files'] = len(f_names_wavs)
            folder_info[folder_name]['wavs'] = f_names_wavs
            folder_info[folder_name]['size_gb'] = sum([f_size for f_name, f_size in f_names_wavs]) / 1024 / 1024 / 1024

    print('[i] Folder information after trimming:')
    for folder_name in folder_info:
        print("\tfolder '{}': {} .wav files, {:.1f} Gb".format(folder_name, folder_info[folder_name]['number_files'], folder_info[folder_name]['size_gb']))


    # Copying each selected/remaining .wav audio to a separate folder
    if not os.path.exists(root_folder+folder_name_for_balanced_speech):
        os.mkdir(root_folder+folder_name_for_balanced_speech)
    else:
        rmtree(root_folder+folder_name_for_balanced_speech, ignore_errors=True)
        os.mkdir(root_folder+folder_name_for_balanced_speech)

    f_names_all_wavs = [f_name_wav for f_name in folder_info for f_name_wav, f_size_wav in folder_info[f_name]['wavs']]
    f_names_all_wavs = list(chain(f_names_all_wavs))
    elapsed_time_per_file = 0.0
    print("\n[i] Copying each remaining .wav audio to '{}'... 0 of {}".format(folder_name_for_balanced_speech, len(f_names_all_wavs)))
    for i, f_name_wav in enumerate(f_names_all_wavs):
        if i % 10 == 0 or i == len(f_names_all_wavs) - 1:
            os.write(sys.stdout.fileno(), curses.tigetstr('cuu1'))
            print("[i] Copying each remaining .wav audio to '{}'... {} of {}, {:.4f} s/file".format(
                    folder_name_for_balanced_speech, i, len(f_names_all_wavs), elapsed_time_per_file))

        start_time = time.time()
        f_name_wav_new = root_folder + folder_name_for_balanced_speech + f_name_wav[f_name_wav.rfind('/')+1:]
        copyfile(f_name_wav, f_name_wav_new)
        elapsed_time_per_file = time.time() - start_time

    os.write(sys.stdout.fileno(), curses.tigetstr('cuu1'))
    print("[i] Copying each remaining .wav audio to '{}'... {} of {}                ".format(
            folder_name_for_balanced_speech, len(f_names_all_wavs), len(f_names_all_wavs)))


if __name__ == '__main__':
    main()
