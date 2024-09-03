#!/user/bin/env python
# -*- coding: utf-8 -*-

import logging
import discord
import json
import os
import re
from datetime import datetime, timedelta
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


class TableReserve:


    def __init__(self, mscDICT):
        
        self.mscDICT = mscDICT
        self.reservation_time = mscDICT["reservation_time"]
        self.party_size = mscDICT["num_of_people"]["total"]
        self.file_path = f"./{self.reservation_time[0:10].replace('-', '')}_table.json"  # 文件路径
        self.start_time = datetime.strptime(self.reservation_time, "%Y-%m-%d %H:%M")
        self.end_time = self.start_time + timedelta(minutes=90)
        self.opening_time = self.start_time.replace(hour=9, minute=0, second=0, microsecond=0)
        self.closing_time = self.start_time.replace(hour=21, minute=0, second=0, microsecond=0)
        self.default_template = {
                                        "max_seats": 10,
                                        "tables": [
                                            {"id": 1, "capacity": 2, "reservations": []},
                                            {"id": 2, "capacity": 2, "reservations": []},
                                            {"id": 3, "capacity": 2, "reservations": []},
                                            {"id": 4, "capacity": 2, "reservations": []},
                                            {"id": 5, "capacity": 2, "reservations": []}
        ]
    }

    def load_reservations(self):
        """加载指定路径的 JSON 文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error(f"File {self.file_path} not found.")
            return None

    def save_reservations(self, reservations):
        """保存预订信息到指定路径的 JSON 文件"""
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(reservations, file, ensure_ascii=False, indent=4)

    def ensure_file_exists(self):
        """确保指定路径的 JSON 文件存在，如果不存在则创建一个新的文件"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(self.default_template, file, ensure_ascii=False, indent=4)

    def check_availability(self, reservations):

        if self.start_time < self.opening_time or self.end_time > self.closing_time:
            return "超出營業時間" # 超出營業時間

        total_seats_reserved = sum(
            res['party_size'] + (1 if res['party_size'] % 2 != 0 and table['capacity'] > res['party_size'] else 0)
            for table in reservations['tables']
            for res in table['reservations']
            if self.start_time < datetime.strptime(res['end_time'], "%Y-%m-%d %H:%M") and self.end_time > datetime.strptime(res['start_time'], "%Y-%m-%d %H:%M")
        )
        return reservations['max_seats'] - total_seats_reserved >= self.party_size

    def make_reservation(self):
        self.ensure_file_exists()
        reservations = self.load_reservations()
        if not self.check_availability(reservations):
            return "該時段無法預約" 

        seats_needed = self.party_size

        for table in reservations['tables']:
            current_seats_reserved = sum(
                res['party_size'] + (1 if res['party_size'] % 2 != 0 and table['capacity'] > res['party_size'] else 0)
                for res in table['reservations']
                if self.start_time < datetime.strptime(res['end_time'], "%Y-%m-%d %H:%M") and self.end_time > datetime.strptime(res['start_time'], "%Y-%m-%d %H:%M")
            )
            available_seats = table['capacity'] - current_seats_reserved

            if seats_needed <= 0:
                break

            if available_seats > 0:
                seats_to_reserve = min(seats_needed, available_seats)
                seats_needed -= seats_to_reserve
                table['reservations'].append({
                    "Name": self.mscDICT["name"],
                    "Phone number": self.mscDICT["phone_num"],
                    "Reserved people": self.mscDICT["num_of_people"],
                    "start_time": self.reservation_time,
                    "end_time": self.end_time.strftime("%Y-%m-%d %H:%M"),
                    "party_size": seats_to_reserve

                    
                })

        self.save_reservations(reservations)
        return "預約成功"  

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
                             "reservation_time": None,
                             "num_of_people": {"adult": None, "child": None, "total": None},
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
                        replySTR = "嗨嗨，我是餐廳預約小幫手～請留下您的姓名，讓我協助您進行預約。"
                    #有講過話，而且還沒超過5分鐘就又跟我 hello (就繼續上次的對話)
                    else:
                        replySTR = self.mscDICT[message.author.id]["latestQuest"]
                #沒有講過話(給他一個新的template)
                else:
                    self.mscDICT[message.author.id] = self.resetMSCwith(message.author.id)
                    replySTR = "嗨嗨，我是餐廳預約小幫手～請留下您的姓名，讓我協助您進行預約。"

# ##########非初次對話：這裡用 Loki 計算語意
            else: #開始處理正式對話
                #從這裡開始接上 NLU 模型
                lokiResultDICT = getLokiResult(msgSTR)
                if lokiResultDICT:
                    if message.author.id not in self.mscDICT:    # 判斷 User 是否為第一輪對話
                        self.mscDICT[message.author.id] = {
                            "name": None,
                            "reservation_time": None,
                            "num_of_people": {"adult": None, "child": None, "total": None}, ## 分成大人跟小孩 
                            "phone_num": None,
                            "updatetime": datetime.now(),
                            "finish": False
                        }

                    # 根據 Loki 的處理結果來處理多輪對話
                    if "name" in lokiResultDICT:
                        self.mscDICT[message.author.id]["name"] = lokiResultDICT["name"]
                        logging.debug("######\nLoki 處理結果如下：")
                        logging.debug(lokiResultDICT)
                        replySTR = "請問您想預約什麼時候？"

                    elif "time" in lokiResultDICT:
                        self.mscDICT[message.author.id]["reservation_time"] = lokiResultDICT["time"]
                        logging.debug("######\nLoki 處理結果如下：")
                        logging.debug(lokiResultDICT)
                        replySTR = "請問預約人數是多少？（Ｏ大Ｏ小）"

                    elif "adult" in lokiResultDICT:
                        if "大人" or "大" in msgSTR:
                            self.mscDICT[message.author.id]["num_of_people"]["adult"] = lokiResultDICT["adult"]
                        else:
                            self.mscDICT[message.author.id]["num_of_people"]["adult"] = lokiResultDICT["adult"]
                            replySTR = "請問有小孩嗎？"
                        logging.debug("######\nLoki 處理結果如下：")
                        logging.debug(lokiResultDICT)

                    elif "child" in lokiResultDICT:
                        self.mscDICT[message.author.id]["num_of_people"]["child"] = lokiResultDICT["child"]
                        self.mscDICT[message.author.id]["num_of_people"]["adult"] = self.mscDICT[message.author.id]["num_of_people"]["adult"][0] - lokiResultDICT["child"][0]
                        self.mscDICT[message.author.id]["num_of_people"]["total"] = self.mscDICT[message.author.id]["num_of_people"]["adult"][0] + self.mscDICT[message.author.id]["num_of_people"]["child"][0]
                        logging.debug("######\nLoki 處理結果如下：")
                        logging.debug(lokiResultDICT)
                        replySTR = "請提供您的聯絡電話。"

                    elif "phone" in lokiResultDICT:
                        self.mscDICT[message.author.id]["phone_num"] = lokiResultDICT["phone"]
                        logging.debug("######\nLoki 處理結果如下：")
                        logging.debug(lokiResultDICT)
                        replySTR = "感謝您提供的信息，我們正在為您查詢"

                    # 根據完成情況來回應
                    if all(value for key, value in self.mscDICT[message.author.id].items() if key != "updatetime"):
                        self.mscDICT[message.author.id]["finish"] = True
                        # reservation_time = self.mscDICT[message.author.id]["reservation_time"]
                        # party_size = self.mscDICT[message.author.id]["num_of_people"]["total"]
                        # file_path = f"./{reservation_time[0:10].replace('-', '')}_table.json"  # 文件路径
                        # mscDICT = self.mscDICT[message.author.id]
                        CheckTable = TableReserve(self.mscDICT[message.author.id])
                        result = CheckTable.make_reservation()
                        
                        if result == "預約成功":
                            replySTR = f"""\
                            Hello {self.mscDICT[message.author.id]["name"]}，您已訂位成功！
                            跟您確認您的訂位資訊

                            電話：{self.mscDICT[message.author.id]["phone_num"]}
                            人數：{self.mscDICT[message.author.id]["num_of_people"]["total"]}人
                            時間：{self.mscDICT[message.author.id]["reservation_time"]}

                            Thank you! """
                        else:
                            replySTR = "抱歉，該時段無法預約，請更換時段。"

                # 確保回應訊息
                await message.reply(replySTR)



if __name__ == "__main__":
    with open("account.info", encoding="utf-8") as f: #讀取account.info
        accountDICT = json.loads(f.read())
    client = BotClient(intents=discord.Intents.default())
    client.run(accountDICT["discord_token"])
