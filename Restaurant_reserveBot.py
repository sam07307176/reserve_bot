#!/user/bin/env python
# -*- coding: utf-8 -*-

import logging
import discord
import json
import os
import re
from datetime import datetime, timedelta
from pprint import pprint
from Restaurant_reserveLoki import execLoki

logging.basicConfig(level=logging.DEBUG)


def getLokiResult(inputSTR, filterLIST=[]):
    splitLIST = ["！", "，", "。", "？", "!", ",", " ", "\n", "；", "\u3000", ";"] #
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
        self.reserveTimeSTR = str(mscDICT["reservation_time"][0])
        self.partySizeINT = mscDICT["num_of_people"]["total"] 
        self.filePathSTR = f"./Reservation data/{self.reserveTimeSTR[0:10].replace('-', '')}_table.json"  # 文件路徑
        self.startTimeDT = datetime.strptime(self.reserveTimeSTR, "%Y-%m-%d %H:%M")
        self.endTimeDT = self.startTimeDT + timedelta(minutes=90)
        self.openingTimeDT = self.startTimeDT.replace(hour=9, minute=0, second=0, microsecond=0)  # 開業時間為 9:00
        self.closingTimeDT = self.startTimeDT.replace(hour=21, minute=0, second=0, microsecond=0)  # 歇業時間為 21:00
        self.tableTemplateDICT = {      # 餐廳共有五張雙人桌，最多可容納十人
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
        """載入指定路徑的 JSON 文件"""
        with open(self.filePathSTR, 'r', encoding='utf-8') as file:
                return json.load(file)

    def save_reservations(self, reservationDICT):
        """保存更新後的定位資訊到指定路徑的 JSON 文件"""
        with open(self.filePathSTR, 'w', encoding='utf-8') as file:
            json.dump(reservationDICT, file, ensure_ascii=False, indent=4)

    def ensure_file_exists(self):
        """如果該天檔案不存在則在指定路徑創建一個新的 JSON 文件"""
        if not os.path.exists(self.filePathSTR):
            with open(self.filePathSTR, 'w', encoding='utf-8') as file:
                json.dump(self.tableTemplateDICT, file, ensure_ascii=False, indent=4)

    def check_availability(self, reservationDICT):
        """預約時間是否在營業時間之內"""
        if self.startTimeDT < self.openingTimeDT or self.endTimeDT > self.closingTimeDT:
            return "超出營業時間" 
        """該時段預定人數加上此訂單是否會超過餐廳容納人數，雙人桌若是已有一位客人則不開放併桌"""
        totalSeatsReservedINT = sum(
            res['partySizeINT'] + (1 if res['partySizeINT'] % 2 != 0 and table['capacity'] > res['partySizeINT'] else 0)
            for table in reservationDICT['tables']
            for res in table['reservations']
            if self.startTimeDT < datetime.strptime(res['endTimeDT'], "%Y-%m-%d %H:%M") and self.endTimeDT > datetime.strptime(res['startTimeDT'], "%Y-%m-%d %H:%M")
        )
        return reservationDICT['max_seats'] - totalSeatsReservedINT >= self.partySizeINT

    def make_reservation(self):
        self.ensure_file_exists()
        reservationDICT = self.load_reservations()
        if not self.check_availability(reservationDICT):
            return "該時段無法預約" 

        """安排座位"""
        seatsNeededINT = self.partySizeINT

        for table in reservationDICT['tables']:
            currentSeatsReservedINT = sum(
                res['partySizeINT'] + (1 if res['partySizeINT'] % 2 != 0 and table['capacity'] > res['partySizeINT'] else 0)
                for res in table['reservations']
                if self.startTimeDT < datetime.strptime(res['endTimeDT'], "%Y-%m-%d %H:%M") and self.endTimeDT > datetime.strptime(res['startTimeDT'], "%Y-%m-%d %H:%M")
            )
            availableSeatsINT = table['capacity'] - currentSeatsReservedINT

            if seatsNeededINT <= 0:
                break

            if availableSeatsINT > 0:
                seatsToReserveINT = min(seatsNeededINT, availableSeatsINT)
                seatsNeededINT -= seatsToReserveINT
                table['reservations'].append({
                    "Name": self.mscDICT["name"],
                    "Phone number": self.mscDICT["phone_num"],
                    "Reserved people": self.mscDICT["num_of_people"],
                    "startTimeDT": self.reserveTimeSTR,
                    "endTimeDT": self.endTimeDT.strftime("%Y-%m-%d %H:%M"),
                    "partySizeINT": seatsToReserveINT

                    
                })
                logging.debug(table["reservations"])

        self.save_reservations(reservationDICT)
        return "預約成功"  

class BotClient(discord.Client):

    def resetMSCwith(self, messageAuthorID):
        '''
        清空與 messageAuthorID 之間的對話記錄
        '''
        templateDICT = {    
                             "id": messageAuthorID,
                             "latestQuest": "",
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
            elif msgSTR.lower() in ["哈囉","嗨","你好","您好","hi","hello", "訂位"]:
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
            else: 
                """從這裡開始接上 NLU 模型"""

                lokiResultDICT = getLokiResult(msgSTR)
                if lokiResultDICT:
                    if message.author.id not in self.mscDICT:    # 判斷 User 是否為第一輪對話
                        self.mscDICT[message.author.id] = {
                            "name": None,
                            "reservation_time": None,
                            "num_of_people": {"adult": None, "child": None, "total": None},
                            "phone_num": None,
                            "updatetime": datetime.now(),
                        }

                    user_data = self.mscDICT[message.author.id]
        
                    # 根據 Loki 的處理結果來處理多輪對話
                    if lokiResultDICT["name"]:
                        user_data["name"] = lokiResultDICT["name"]
                        logging.debug("######\nLoki 處理結果如下：")
                        logging.debug(lokiResultDICT)
                        logging.debug(user_data)
                        replySTR = "請問您想預約什麼時候？"

                    if lokiResultDICT["time"]:
                        user_data["reservation_time"] = lokiResultDICT["time"]
                        logging.debug("######\nLoki 處理結果如下：")
                        logging.debug(lokiResultDICT)
                        logging.debug(user_data)
                        replySTR = "請問預約人數是多少？（Ｏ大Ｏ小）"

                    if lokiResultDICT["adult"]:
                        if "大人" in msgSTR or "大" in msgSTR:
                            if lokiResultDICT["child"] == []:
                                user_data["num_of_people"]["child"] = "無"
                                user_data["num_of_people"]["adult"] = lokiResultDICT["adult"]
                                user_data["num_of_people"]["total"] = int(user_data["num_of_people"]["adult"][0])
                            else:
                                user_data["num_of_people"]["adult"] = lokiResultDICT["adult"]
                            replySTR = "請提供您的聯絡電話。"
                        else:
                            user_data["num_of_people"]["total"] = int(lokiResultDICT["adult"][0])
                            replySTR = "請問有小孩嗎？"
                        logging.debug("######\nLoki 處理結果如下：")
                        logging.debug(lokiResultDICT)
                        logging.debug(user_data)

                    if lokiResultDICT["child"]:
                        if user_data["num_of_people"]["adult"] is None and lokiResultDICT["child"] != 0:
                            user_data["num_of_people"]["child"] = lokiResultDICT["child"]
                            user_data["num_of_people"]["adult"] = user_data["num_of_people"]["total"] - user_data["num_of_people"]["child"][0]
                        elif user_data["num_of_people"]["adult"] is None and lokiResultDICT["child"] == 0:
                            user_data["num_of_people"]["child"] = lokiResultDICT["child"]
                            user_data["num_of_people"]["adult"] = user_data["num_of_people"]["total"] - user_data["num_of_people"]["child"]
                        else:
                            user_data["num_of_people"]["child"] = lokiResultDICT["child"]
                            user_data["num_of_people"]["total"] = user_data["num_of_people"]["adult"][0] + user_data["num_of_people"]["child"][0]
                        if user_data["num_of_people"]["child"] == 0:
                            user_data["num_of_people"]["child"] = "無"

                        logging.debug("######\nLoki 處理結果如下：")
                        logging.debug(lokiResultDICT)
                        logging.debug(user_data)
                        replySTR = "請提供您的聯絡電話。"

                    if lokiResultDICT["phone"]:
                        user_data["phone_num"] = lokiResultDICT["phone"]
                        # 檢查是否所有信息都已提供
                        if all(user_data[key] not in [None, "無"] for key in ["name", "reservation_time"]) and \
                           all(user_data["num_of_people"][key] not in [None, "無"] for key in ["adult", "child", "total"]):
                            replySTR = "感謝您提供的信息，我們正在為您查詢。"
                        else:
                            replySTR = "請提供所有必要的信息以完成預約。"
                        logging.debug("######\nLoki 處理結果如下：")
                        logging.debug(lokiResultDICT)
                        logging.debug(user_data)

                    """若客戶資訊搜集完畢則確認是否能安排座位"""
                    if all(user_data[key] not in [None] for key in ["name", "reservation_time", "phone_num"]) and \
                       all(user_data["num_of_people"][key] not in [None] for key in ["adult", "child", "total"]):
                        user_data["finish"] = True
                        logging.debug(user_data)
                        
                        CheckTable = TableReserve(user_data)
                        result = CheckTable.make_reservation()
                        
                        if result == "預約成功":
                            replySTR = f"""Hello {user_data["name"][0]}，您已訂位成功！\n跟您確認您的訂位資訊\n\n電話：{user_data["phone_num"][0]}\n人數：{user_data["num_of_people"]["total"]}人\n時間：{user_data["reservation_time"][0]}\n\nThank you! """
                        else:
                            replySTR = "抱歉，該時段無法預約，請更換時段。"
                    
            # 回應訊息送出
            await message.reply(replySTR)



if __name__ == "__main__":
    with open("account.info", encoding="utf-8") as f: #讀取account.info
        accountDICT = json.loads(f.read())
    client = BotClient(intents=discord.Intents.default())
    client.run(accountDICT["discord_token"])
