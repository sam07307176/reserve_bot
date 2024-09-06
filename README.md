# ReserveBot 餐廳預約聊天機器人

## 簡介

本專案目的是協助業主跟客戶在 **Discord**的平台上，透過與聊天機器人進行多輪對話，讓業主取得客戶輸入的資訊（包含姓名、手機號碼、人數、時間）；接著使用 **卓騰語言科技公司 DroidTown** 的產品 **Articut**、**Loki** 來進行語意理解的處理；接著去比對客戶所輸入的時段是否可開放預約；最後進行回覆，並將成功預約的客戶資訊存入餐廳訂位的檔案。

## 目錄

```
├── Resetaurant_reserveLoki.py  # NLU主程式，使用Loki進行語意處理
├── Resetaurant_reserveBot.py  # 處理Discord的運作、餐廳訂位安排
├── README.md
├── intent  # 全部的intent
│   ├── .DS_Store
│   ├── Loki_name.py
│   ├── Loki_person.py
│   ├── Loki_phone.py
│   ├── Loki_time_basic.py
│   ├── USER_DEFINED.json
│   ├── Updater.py
│   └── __init__.py
├── ref  # 提供Loki讀取
│   ├── name.ref
│   ├── person.ref
│   ├── phone.ref
│   └── time_basic.ref
└── Resservation data  # 餐廳訂位資料庫
```

## 環境設置

### 註冊卓騰帳號 

1. 請至[卓騰語言科技](https://api.droidtown.co/)官方網站註冊帳號並登入頁面。
2. 於網頁右上角點選註冊 
![](https://imgur.com/2v6Xhmy.jpg)
3. 註冊完成後即可登入
![](https://imgur.com/mpwBJKp.jpg)

### 使用Loki

1. 選擇 **Loki** 並開始使用
2. 輸入專案名稱並建立專案
3. 前往專案並匯入意圖（intent）
4. 部署模型
5. 點選左上房子圖示回到 **Loki** 控制台
6. 複製專案金鑰

### 使用Articut

1. 前往服務資訊
2. 選擇 **Articut** 並複製 API 金鑰
```
pip install ArticutAPI
```

### 建立 Discord bot

1. 到 [Discord Developers](https://discord.com/login?redirect_to=/developers/applications) 建立一個新的 Application
2. 新增一個 Bot
3. 取得 Bot token
4. 將 Bot 加入伺服器


### 建立  account.info

```
{
"username":"your account",  #你的帳號
"api_key":"your articut key",  #你的articut金鑰
"loki_key":"your loki key",  #你的loki專案金鑰
"discord_token": "your bot token"  #你的discord bot的token
}
```

## 使用者輸入範例

:bulb:**每則訊息都一定要標注機器人 ==@restaurant_reserve_bot==**

1. 標注機器人，並向它打聲招呼開啟對話。
> 你可以說：hi/hello/嗨/哈囉/您好/你好/訂位

2. 機器人會回覆：「嗨嗨，我是餐廳預約小幫手～請留下您的姓名，讓我協助您進行預約。」接著你可以輸入你的姓名，不一定要全名
> 你可以說：張小姐/張先生/我姓張/張

3. 機器人會接著詢問你想預約的時段
> 你可以說：今天下午三點/12/25下午三點/明天15:00

4. 機器人會接著詢問你訂位人數
> 你可以說：兩大兩小/總共四位/兩位大人

5. 機器人會接著詢問你的手機號碼
> 你可以說：0912345678

6. 接著會為你查詢是否可以預約該時段。如果該時段額滿，機器人會說：「抱歉，該時段無法預約，請更換時段。」接著請你再次回覆其他時段。

7. 如果該時段可以預約，機器人會回覆：
```
Hello Ｏ小姐，您已訂位成功！
跟您確認您的訂位資訊

電話：09XXXXXXXX
人數：Ｏ人
時間：2024-XX-XX XX:XX

Thank you!
```

## 作者

[Jennifer Chang](https://github.com/Jenn-ccf)

[Sam Chen](https://github.com/sam07307176)