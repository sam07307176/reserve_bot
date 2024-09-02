#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for person

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
        responseDICT = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "reply/reply_person.json"), encoding="utf-8"))
    except Exception as e:
        print("[ERROR] responseDICT => {}".format(str(e)))

# 將符合句型的參數列表印出。這是 debug 或是開發用的。
def debugInfo(inputSTR, utterance):
    if DEBUG:
        print("[person] {} ===> {}".format(inputSTR, utterance))

def getResponse(utterance, args):
    resultSTR = ""
    if utterance in responseDICT:
        if len(responseDICT[utterance]):
            resultSTR = sample(responseDICT[utterance], 1)[0].format(*args)

    return resultSTR


def numberConvert(args):
    chinese_numeral = args
    arabic_numeral = cn2an.cn2an(chinese_numeral, "smart")
    return arabic_numeral 



def getResult(inputSTR, utterance, args, resultDICT, refDICT, pattern=""):
    debugInfo(inputSTR, utterance)
    if utterance == "[兩][大][兩][小]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            if args[1] == "大":
                resultDICT["adult"] = numberConvert(args[0])
                resultDICT["child"] = numberConvert(args[2])
            else:
                resultDICT["adult"] = numberConvert(args[2])
                resultDICT["child"] = numberConvert(args[0])

            pass

    if utterance == "[兩位]大人[兩位]小孩":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            resultDICT["adult"] = articut.parse(args[0], level="lv3")["number"][args[0]]
            resultDICT["child"] = articut.parse(args[1], level="lv3")["number"][args[1]]
            pass

    if utterance == "[我]要[兩][大][兩][小]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            if args[2] == "大":
                resultDICT["adult"] = numberConvert(args[1])
                resultDICT["child"] = numberConvert(args[3])
            else:
                resultDICT["adult"] = numberConvert(args[3])
                resultDICT["child"] = numberConvert(args[1])
            pass

    if utterance == "[總共][兩][大][兩][小]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            if args[2] == "大":
                resultDICT["adult"] = numberConvert(args[1])
                resultDICT["child"] = numberConvert(args[3])
            else:
                resultDICT["adult"] = numberConvert(args[3])
                resultDICT["child"] = numberConvert(args[1])
            pass

    if utterance == "[總共][兩位]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            resultDICT["adult"] = articut.parse(args[1], level="lv3")["number"][args[1]]
            pass

    if utterance == "[兩位]":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
            if resultDICT["response"]:
                resultDICT["source"] = "reply"
        else:
            resultDICT["adult"] = articut.parse(args[0], level="lv3")["number"][args[0]]

    return resultDICT