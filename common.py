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

SCRIPT_DIR_COMMON = os.path.dirname(__file__)
CONFIG_FILE = os.path.join('./', SCRIPT_DIR_COMMON, 'conf.json')

# config file
try:
    f = open(CONFIG_FILE, 'r')
except IndexError:
    conf = json.loads('"file":"null"')
except IOError:
    conf = json.loads('{"file":"null"}')
else:
    conf = json.load(f)
    f.close()

if conf.get("FFMPEG_LOG_LEVEL") is not None:
    FFMPEG_LOG_LEVEL = conf["FFMPEG_LOG_LEVEL"]
else:
    FFMPEG_LOG_LEVEL = "-loglevel info"

if conf.get("FFMPEG_DIR") is not None:
    FFMPEG_DIR = conf["FFMPEG_DIR"]
else:
    FFMPEG_DIR = ""

DEBUG_LOG_LEVEL = 'Info'
# Error, Warn, Info, Log_off(or other level string)
DEBUG_LOG_LEVEL_DESCRIPTION = {
    'Error':['Error'],
    'Warn':['Error', 'Warn'],
    'Info':['Error', 'Warn', 'Info'],
    'Log_off':[]
    }

TEMP_DIR = tempfile.mkdtemp()


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


def searchLutVideo(filename):
    lutVideoExist = False
    lutFile = None
    if ".mp4" in filename:
        lutFile = filename.replace(".mp4","_LUT.mp4")
    if ".MP4" in filename:
        lutFile = filename.replace(".MP4","_LUT.mp4")
    if lutFile is not None and os.path.isfile(lutFile):
        lutVideoExist = True
    return lutVideoExist,lutFile

def checkCTV(ctv,idx):
    b = eval("0b1"+"0"*idx)
    return (ctv & b == 0)

#
# parameter ツール
#

def support_default(o):
    if isinstance(o, PARAM_TOOL):
        return o.__dict__
    raise TypeError(repr(o) + " is not JSON serializable")

class PARAM_TOOL:
    def __init__(self):
        pass
    def add(self,scope_name):
        self.__dict__[scope_name] = PARAM_TOOL()
    def save(self,filename):
        f = open(filename,"w")
        json.dump(self.__dict__,f, ensure_ascii=False, indent=2, sort_keys=True, separators=(',', ': '),default=support_default)
        f.close()
    def __len__(self):
        return len(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)
    def __str__(self):
        return str(self.__dict__)
    def __iter__(self):
        return self.__dict__.iteritems()
    def __getitem__(self, key):
        return self.__dict__[key]
    def __setitem__(self, key, value):
        self.__dict__[key] = value

pp = PARAM_TOOL()

#
# parameter ツール ここまで
#

def print_log(log_level, log_str):
    u"""
    log出力制御関数
    @param log_level str : log level
    @param log_str str : log string
    """
    if DEBUG_LOG_LEVEL in DEBUG_LOG_LEVEL_DESCRIPTION:
        supported_list = DEBUG_LOG_LEVEL_DESCRIPTION[DEBUG_LOG_LEVEL]
        if log_level in supported_list:
            print("[%s]: %s" % (log_level, log_str))

if __name__ == "__main__":
    pass
