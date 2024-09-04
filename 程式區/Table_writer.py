#!/usr/bin/env python3
# -*- coding:utf-8 -*-


#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import json


def load_table_list(file_path):
    """讀取 JSON 檔案並返回桌子列表"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def save_table_list(file_path, table_list):
    """將更新後的桌子列表寫入 JSON 檔案"""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(table_list, file, ensure_ascii=False, indent=4)


def check_availability(table_list, date, time):
    """檢查指定日期和時間的預約情況"""
    for table in table_list:
        for key, info in table.items():
            if info['reserved_date'] == date and info['reserved_time'] == time:
                return f"{key} 在這個時間已經預約過了。"
    return None


def display_available_tables(table_list, date, time):
    """顯示可用的桌子"""
    available_tables = []
    for table in table_list:
        for key, info in table.items():
            if info['reserved_date'] == "" and info['reserved_time'] == "":
                available_tables.append(key)
    return available_tables


def table_writer():
    """主程序，用於處理預約和更新桌子資訊"""
    # 讀取 JSON 檔案
    table_list = load_table_list('Table_List.json')

    # 輸入預約資訊
    date = input("請輸入預約日期 (格式: YYYY-MM-DD): ")
    time = input("請輸入預約時間 (格式: HH:MM): ")
    name = input("請輸入姓名 (格式: 姓氏＿名): ")
    phone = input("請輸入電話號碼 (格式: 09....): ")

    # 檢查是否有空桌子
    availability_message = check_availability(table_list, date, time)
    if availability_message:
        print(availability_message)
        return

    # 顯示可用桌子
    available_tables = display_available_tables(table_list, date, time)
    if not available_tables:
        print("抱歉，這個時間已被預約。")
        return

    print("以下是空位：")
    for table in available_tables:
        print(table)

    selected_table = input("請選擇桌子 (例如: table_01): ")

    # 更新選定桌子的預約信息
    table_found = False
    for table in table_list:
        if selected_table in table:
            table[selected_table]['reserved_date'] = date
            table[selected_table]['reserved_time'] = time
            table[selected_table]['name'] = name
            table[selected_table]['phone'] = phone
            table_found = True
            break

    if table_found:
        print("預約成功！")
    else:
        print("錯誤。")

    # 寫入更新後的 JSON 檔案
    save_table_list('Table_List_updated.json', table_list)


if __name__ == "__main__":
    table_writer()
