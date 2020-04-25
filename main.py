#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = "masaru mizuochi (@_mizumasa)"
__version__ = "1.00"
__date__ = "12 April 2020"

import atexit
import shutil
import sys
import multiprocessing as mp

from add_args import AddArgs
from common import *

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
from subMain import subMain

def main(args):
    print_log('Info', 'main.py is called [' + str(args) + ']')
    res = subMain(args)
    return res

if __name__ == "__main__":
    mp.freeze_support()
    args = AddArgs().get_args()
    DEBUG_LOG_LEVEL = args.log_level
    print(TEMP_DIR)
    atexit.register(shutil.rmtree, TEMP_DIR)
    sys.exit(main(args))
