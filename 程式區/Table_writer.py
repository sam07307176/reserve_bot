#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import json



def table_wrtier():
    with open('Table_List.json', 'r', encoding='utf-8') as file:
        table_list = json.load(file)

    for table in table_list:
        for key in table:
        # 輸入日期、時間和人數
            date = input(f"請輸入 {key} 的預約日期 (格式: YYYY-MM-DD): ")
            time = input(f"請輸入 {key} 的預約時間 (格式: HH:MM): ")
            name = input(f"請輸入 {key} 的姓名 (格式: 姓氏＿名): ")
            phone = input(f"請輸入 {key} 的電話號碼 (格式: 09....): ")

        # 更新該桌子的預約信息
        table[key]['reserved_date'] = date
        table[key]['reserved_time'] = time
        table[key]['reserved_name'] = name
        table[key]['reserved_phone'] = phone


        with open('Table_List_updated.json', 'w', encoding='utf-8') as file:
                json.dump(table_list, file, ensure_ascii=False, indent=4)    


if __name__ == "__main__":