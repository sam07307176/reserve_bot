#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for time_basic

    Input:
        inputSTR      str,
        utterance     str,
        args          str[],
        resultDICT    dict,
        refDICT       dict,
        pattern       str

    Output:
        resultDICT    dict
"""

from random import sample
import json
import os
from ArticutAPI import Articut
articut = Articut()
import datetime

DEBUG = True
CHATBOT_MODE = False

userDefinedDICT = {}
try:
    userDefinedDICT = json.load(open(os.path.join(os.path.dirname(__file__), "USER_DEFINED.json"), encoding="utf-8"))
except Exception as e:
    print("[ERROR] userDefinedDICT => {}".format(str(e)))

responseDICT = {}
if CHATBOT_MODE:
    try:
        responseDICT = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "reply/reply_time_basic.json"), encoding="utf-8"))
    except Exception as e:
        print("[ERROR] responseDICT => {}".format(str(e)))

# 將符合句型的參數列表印出。這是 debug 或是開發用的。
def debugInfo(inputSTR, utterance):
    if DEBUG:
        print("[time_basic] {} ===> {}".format(inputSTR, utterance))

def getResponse(utterance, args):
    resultSTR = ""
    if utterance in responseDICT:
        if len(responseDICT[utterance]):
            resultSTR = sample(responseDICT[utterance], 1)[0].format(*args)

    return resultSTR

""" 
-----參考Peter-----

def resultDICTPacker(args):
    resultDICT = {}
    # resultDICT["date"] = datetime.datetime.today()
    hourDICT = articut.parse(args[0], level="lv3")
    if hourDICT["time"] != []:
        resultDICT["hour"] = hourDICT["time"]["hour"]

    try:
        minuteDICT = articut.parse(args[1], level="lv3")
        if minuteDICT["time"] != []:
            resultDICT["minute"] = hourDICT[ "time"]["minute"]
        else:
            resultDICT["minute"] = "00"
    except IndexError:
        resultDICT["minute"] = "00"

    return resultDICT

"""

def getResult(inputSTR, utterance, args, resultDICT, refDICT, pattern=""):
    debugInfo(inputSTR, utterance)
    if utterance == "[14]:[00]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            datetime_str = datetime.datetime.today()
            resultDICT["date"] = datetime_str[5:7].lstrip('0') + '/' + datetime_str[8:10].lstrip('0')
            resultDICT["hour"] = args[0]
            resultDICT["minute"] = args[1]
            pass

    if utterance == "[8]/[22]/[21]:[00]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            resultDICT["date"] = args[0]+"/"+args[1]
            resultDICT["hour"] = args[2]
            resultDICT["minute"] = args[3]
            pass

    if utterance == "[8]/[22][晚上九點]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            resultDICT["date"] = args[0]+"/"+args[1]
            dateDICT = articut.parse(args[2], level="lv3")
            resultDICT["hour"] = dateDICT['time'][0][0]['datetime'][11-13]
            resultDICT["minute"] = dateDICT['time'][0][0]['datetime'][14-16]
            pass

    if utterance == "[下午兩點]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            dateDICT = articut.parse(args[0], level="lv3")
            datetime_str = dateDICT['time'][0][0]['datetime']
            resultDICT["date"] = datetime_str[5:7].lstrip('0') + '/' + datetime_str[8:10].lstrip('0')
            resultDICT["hour"] = datetime_str[11:13]
            resultDICT["minute"] = datetime_str[14:16]

            pass

    if utterance == "[明天晚上][9]:[00]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            dateDICT = articut.parse(args[0], level="lv3")
            if dateDICT["time"] != []:
                # resultDICT["date"] = dateDICT["time"]["datetime"]
                datetime_str = dateDICT['time'][0][0]['datetime']
                resultDICT["date"] = datetime_str[5:7].lstrip('0') + '/' + datetime_str[8:10].lstrip('0')
            
            if "晚上" or "下午" in args[0] and int(args[1])<=12:
                resultDICT["hour"] = int(args[1])+12
            else:
                resultDICT["hour"] = args[1]
            resultDICT["minute"] = args[2]
            pass

    return resultDICT