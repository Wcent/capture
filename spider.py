#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'cent'

'''
web spider to capture datas from 'www.sge.com.cn'
'''

import requests
from bs4 import BeautifulSoup
import json
import re

def spider(page_num):
    # 按页码获取每日行情页面
    response = requests.get('http://www.sge.com.cn/sjzx/mrhqsj?p=%d' % page_num)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "lxml")

    # 找到每日行情链接列表
    date_list = soup.findAll(href=re.compile("/sjzx/mrhqsj/"))
    for date in date_list:
        # 构造url，获取某日行情数据页面
        date_response = requests.get('http://www.sge.com.cn' + date['href'])
        date_response.encoding = 'utf-8'
        date_soup = BeautifulSoup(date_response.text, 'lxml')
        # 解析table，转换为json
        split_data(date_soup)


def split_data(date_soup):
    # 解析获取每日行情数据
    # for tr in date_soup.select('tbody tr'):
    #     for (td_index, td) in enumerate(tr.findAll('td')):
    #         print(td_index, td.get_text(strip=True))

    # 解析日期
    date = date_soup.find(text=re.compile("时间:")).parent.parent.text.split(':')

    # 解析表数据
    for (tr_index, tr) in enumerate(date_soup.select('tbody tr')):
        # 初始化
        if tr_index == 0:
            key = []
        else:
            data = {}.fromkeys(key)
            data[date[0]] = date[1]

        # 构造数据dict
        for (td_index, td) in enumerate(tr.findAll('td')):
            # 表头为json键
            if tr_index == 0:
                key.append(td.get_text(strip=True))
            # 表项为json值
            else:
                data[key[td_index]] = td.get_text(strip=True)

        # 数据转换：dict -> json
        if tr_index != 0:
            json_data = json.dumps(data, ensure_ascii=False)
            print(json_data)


# todo some test
if __name__ == '__main__':
    spider(page_num=1)