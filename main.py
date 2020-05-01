#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = "masaru mizuochi (@_mizumasa)"
__version__ = "1.00"
__date__ = "12 April 2020"

import atexit
import shutil
import sys
import multiprocessing as mp

from common import *

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
from subMain import subMain

def main():
    res = subMain()
    return res

if __name__ == "__main__":
    mp.freeze_support()
    sys.exit(main())
