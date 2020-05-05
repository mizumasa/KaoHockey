#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
共通importモジュール
"""
import os
import json
import tempfile
import shutil
import winsound

from math import ceil, floor
from datetime import datetime

__author__ = "masaru mizuochi"
__version__ = "1.01"
__date__ = "12 April 2020"

def soundBar():
    playSound("cursor2.wav")

def soundWall():
    playSound("cursor4.wav")

def soundPoint():
    playSound("decision22.wav")

def playSound(filename):
    if not os.path.isfile(filename):
        return
    try:
        winsound.PlaySound(filename, winsound.SND_ASYNC | winsound.SND_NOSTOP)
    except:
        pass

def getTimeStamp():
    buf = datetime.now()
    return buf.strftime("%Y")[2:] + buf.strftime("%m%d_%H%M%S")

def getExt(_path):
    return os.path.splitext(_path)[1]

def MakeDir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    else:
        shutil.rmtree(path) #ディレクトリごと削除してから.
        os.makedirs(path)

if __name__ == "__main__":
    pass
