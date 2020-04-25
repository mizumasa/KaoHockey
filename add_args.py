#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
main.py から呼び出される関数
main.py実行時の引数を管理
"""

from argparse import ArgumentParser

__author__ = "masaru mizuochi"
__version__ = "1.01"
__date__ = "12 April 2020"

import os
import sys
from common import *

class AddArgs:
    def __init__(self):
        self.parser = ArgumentParser(description='')
        subparsers = self.parser.add_subparsers(help='subcommands', dest='subcommands')
        add_args(subparsers)

        self.parser.add_argument('-i',
                        help='input directory',
                        dest='input_dir', default = None)
        self.parser.add_argument('-t',
                        help='test 10 frame',
                        dest='frame_test', action="store_true")
        self.parser.add_argument('-s',
                        help='scale test',
                        dest='scale_test', action="store_true")
        self.parser.add_argument('-ll',
                            help='log level (Error, Warn, Info, Log_off) default:Info',
                            dest='log_level', default=DEBUG_LOG_LEVEL)
        return
    def get_args(self):
        return self.parser.parse_args()


def add_args(parsers):
    parser = parsers.add_parser(
        'sub',
        help='sub command')
    parser.add_argument('-i',
                    help='input movie file',
                    dest='input_file', default = None)
    parser.add_argument('--param_all',
                        help='show all parameter',
                        dest='param_all', action="store_true")
    parser.add_argument('-o',
                    help='output directory',
                    dest='output_dir', default = None)
    parser.add_argument('-ll',
                        help='log level (Error, Warn, Info, Log_off) default:Info',
                        dest='log_level', default=DEBUG_LOG_LEVEL)

if __name__ == "__main__":
    pass

