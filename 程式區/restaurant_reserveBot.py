#!/user/bin/env python
# -*- coding: utf-8 -*-

import logging
import discord
import json
import re
from datetime import datetime
from pprint import pprint

from restaurant_reservation import execLoki

logging.basicConfig(level=logging.DEBUG)


def getLokiResult(inputSTR, filterLIST=[]):
    splitLIST = ["！", "，", "。", "？", "!", ",", " ","\n", "；", "\u3000", ";"] #
    # 設定參考資料
    refDICT = { # value 必須為 list
        #"key": []
        "name":[],
        "adult":[],
        "child":[],
        "time":[],
        "phone":[]
    }
    resultDICT = execLoki(inputSTR, filterLIST=filterLIST, splitLIST=splitLIST, refDICT=refDICT)
    logging.debug("Loki Result => {}".format(resultDICT))
    return resultDICT

class BotClient(discord.Client):

    def resetMSCwith(self, messageAuthorID):
        '''
        清空與 messageAuthorID 之間的對話記錄
        '''
        templateDICT = {    
                             # "id": messageAuthorID,
                             # "updatetime" : datetime.now(),
                             # "latestQuest": "",
                             # "false_count" : 0,
                             "name": None,
                             "reserve_time": None,
                             "num_of_people": {"adult": None, "child": None},
                             "phone_num": None,
                             "updatetime": datetime.now(),
                             "finish": False
        }
        return templateDICT

    async def on_ready(self):
        # ################### Multi-Session Conversation :設定多輪對話資訊 ###################
        self.templateDICT = {"updatetime" : None,
                             "latestQuest": ""
        }
        self.mscDICT = { #userid:templateDICT
        }
        # ####################################################################################
        print('Logged on as {} with id {}'.format(self.user, self.user.id))

    async def on_message(self, message):
        # Don't respond to bot itself. Or it would create a non-stop loop.
        # 如果訊息來自 bot 自己，就不要處理，直接回覆 None。不然會 Bot 會自問自答個不停。
        if message.author == self.user:
            return None

        logging.debug("收到來自 {} 的訊息".format(message.author))
        logging.debug("訊息內容是 {}。".format(message.content))
        if self.user.mentioned_in(message):
            replySTR = "我是預設的回應字串…你會看到我這串字，肯定是出了什麼錯！"
            logging.debug("本 bot 被叫到了！")
            msgSTR = message.content.replace("<@{}> ".format(self.user.id), "").strip()
            logging.debug("人類說：{}".format(msgSTR))
            if msgSTR == "ping":
                replySTR = "pong"
            elif msgSTR == "ping ping":
                replySTR = "pong pong"

# ##########初次對話：這裡是 keyword trigger 的。
            elif msgSTR.lower() in ["哈囉","嗨","你好","您好","hi","hello"]:
                #有講過話(判斷對話時間差)
                if message.author.id in self.mscDICT.keys():
                    timeDIFF = datetime.now() - self.mscDICT[message.author.id]["updatetime"]
                    #有講過話，但與上次差超過 5 分鐘(視為沒有講過話，刷新template)
                    if timeDIFF.total_seconds() >= 300:
                        self.mscDICT[message.author.id] = self.resetMSCwith(message.author.id)
                        replySTR = "嗨嗨，我是預約餐廳小幫手～請留下您的姓名，讓我協助您進行預約。"
                    #有講過話，而且還沒超過5分鐘就又跟我 hello (就繼續上次的對話)
                    else:
                        replySTR = self.mscDICT[message.author.id]["latestQuest"]
                #沒有講過話(給他一個新的template)
                else:
                    self.mscDICT[message.author.id] = self.resetMSCwith(message.author.id)
                    # replySTR = msgSTR.title()
                    replySTR = "嗨嗨，我是預約餐廳小幫手～請留下您的姓名，讓我協助您進行預約。"

# ##########非初次對話：這裡用 Loki 計算語意
            else: #開始處理正式對話
                #從這裡開始接上 NLU 模型
                lokiResultDICT = getLokiResult(msgSTR)
                if lokiResultDICT:
                    if message.author.id not in self.mscDICT:    # 判斷 User 是否為第一輪對話
                        self.mscDICT[message.author.id] = {
                            "name": None,
                            "reserve_time": None,
                            "num_of_people": {"adult": None, "child": None}, ## 分成大人跟小孩 
                            "phone_num": None,
                            "updatetime": datetime.now(),
                            "finish": False
                        }

                    # 根據 Loki 的處理結果來處理多輪對話
                    if "name" in lokiResultDICT:
                        self.mscDICT[message.author.id]["name"] = lokiResultDICT["name"]
                        replySTR = "請問您的預約時間是什麼時候？"

                    elif "time" in lokiResultDICT:
                        self.mscDICT[message.author.id]["reserve_time"] = lokiResultDICT["time"]
                        replySTR = "請問預約人數是多少？（Ｏ大Ｏ小）"

                    elif "adult" in lokiResultDICT:
                        if "大人" or "大" in msgSTR:
                            self.mscDICT[message.author.id]["num_of_people"]["adult"] = lokiResultDICT["adult"]
                        else:
                            self.mscDICT[message.author.id]["num_of_people"]["adult"] = lokiResultDICT["adult"]
                            replySTR = "請問有小孩嗎？"

                    elif "child" in lokiResultDICT:
                        self.mscDICT[message.author.id]["num_of_people"]["child"] = lokiResultDICT["child"]
                        self.mscDICT[message.author.id]["num_of_people"]["adult"] = self.mscDICT[message.author.id]["num_of_people"]["adult"][0] - lokiResultDICT["child"][0]
                        replySTR = "請提供您的聯絡電話。"

                    elif "phone" in lokiResultDICT:
                        self.mscDICT[message.author.id]["phone_num"] = lokiResultDICT["phone"]
                        replySTR = "感謝您提供的信息，我們的預約流程已經完成。"

                    # 根據完成情況來回應
                    if all(value for key, value in self.mscDICT[message.author.id].items() if key != "updatetime"):
                        self.mscDICT[message.author.id]["finish"] = True
    ################### 比對餐廳資訊
                        # replySTR = "感謝您的預約資訊。我們會盡快處理。"


                logging.debug("######\nLoki 處理結果如下：")
                logging.debug(lokiResultDICT)
                # 確保回應訊息
                await message.reply(replySTR)


            

         


if __name__ == "__main__":
    with open("account.info", encoding="utf-8") as f: #讀取account.info
        accountDICT = json.loads(f.read())
    client = BotClient(intents=discord.Intents.default())
    client.run(accountDICT["discord_token"])
