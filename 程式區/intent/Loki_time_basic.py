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

def getResult(inputSTR, utterance, args, resultDICT, refDICT, pattern=""):
    debugInfo(inputSTR, utterance)
    if utterance == "[14]:[00]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            date = datetime.datetime.today().strftime('%Y-%m-%d')
            hour = args[0]
            minute = args[1]
            resultDICT["time"] = f"{date} {hour:02}:{minute:02}"


    if utterance == "[8]/[22]/[21]:[00]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            date = datetime.datetime.today().strftime('%Y')
            date = f"{date}-{int(args[0]):02}-{int(args[1]):02}"
            hour = args[2]
            minute = args[3]
            resultDICT["time"] = f"{date} {hour:02}:{minute:02}"
            

    if utterance == "[8]/[22][晚上九點]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            date = datetime.datetime.today().strftime('%Y')
            date = f"{date}-{int(args[0]):02}-{int(args[1]):02}"
            dateDICT = articut.parse(args[2], level="lv3")
            datetime_str = dateDICT['time'][0][0]['datetime']
            hour_minute = datetime_str[11:16]
            resultDICT["time"] = f"{date} {hour_minute}"
            

    if utterance == "[下午兩點]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            dateDICT = articut.parse(args[0], level="lv3")
            datetime_str = dateDICT['time'][0][0]['datetime']
            resultDICT["time"] = datetime_str[0:16]


    if utterance == "[明天晚上][9]:[00]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            dateDICT = articut.parse(args[0], level="lv3")
            datetime_str = dateDICT['time'][0][0]['datetime']
            date = datetime_str[0:10]
            
            if ("晚上" in args[0] or "下午" in args[0]) and int(args[1]) <= 12:
                hour = int(args[1])+12
            else:
                hour = args[1]
            minute = args[2]
            resultDICT["time"] = f"{date} {hour:02}:{minute:02}"
            

    return resultDICT