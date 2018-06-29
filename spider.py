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
import time

def spider(page_num):
    # 伪装浏览器访问的请求头部，防止被反爬虫处理
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/67.0.3396.87 Safari/537.36'}
    # 以页码为url参数请求每日行情页面
    response = requests.get('http://www.sge.com.cn/sjzx/mrhqsj', params={'p': str(page_num)}, headers=headers)
    if response.status_code != 200:
        print('Failure', response.status_code)
        return
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "lxml")

    # 找到每日行情链接列表
    date_list = soup.findAll(href=re.compile("/sjzx/mrhqsj/"))
    for date in date_list:
        # 限制访问频率，避免IP被封
        time.sleep(3)

        # 构造url，获取某日行情数据页面
        date_response = requests.get('http://www.sge.com.cn' + date['href'], headers=headers)
        if date_response.status_code != 200:
            print('Error', date_response.status_code)
            return
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

        # 表头为json键
        if tr_index == 0:
            # 表头为th标签
            for (td_index, th) in enumerate(tr.findAll('th')):
                key.append(th.get_text(strip=True))
            # 表头为td标签
            for (td_index, td) in enumerate(tr.findAll('td')):
                key.append(td.get_text(strip=True))
        # 表项为json值
        else:
            for (td_index, td) in enumerate(tr.findAll('td')):
                data[key[td_index]] = td.get_text(strip=True)

        # 数据转换：dict -> json
        if tr_index != 0:
            json_data = json.dumps(data, ensure_ascii=False)
            print(json_data)


# todo some test
if __name__ == '__main__':
    spider(page_num=1)