# -*- coding: utf-8 -*-
# @Time    : 2021/4/15 02:57
# @Author  : AA8j
# @FileName: CrawlChenduSubway.py
# @Software: PyCharm
# @Blog    ：https://blog.csdn.net/qq_44874645
import json
import re
import time

import requests
from bs4 import BeautifulSoup
from pyexcel_xls import save_data
from collections import OrderedDict
import pickle
from collections import defaultdict
import pandas as pd


# 从成都地铁官网爬取站点信息
def spyder():
    # 获得成都的地铁信息
    url = 'https://www.chengdurail.com/stroke/Inquire.html#anchor3'
    user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'
    headers = {'User-Agent': user_agent}
    # 请求网页
    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    # 获得页面源码
    html = r.text

    # 分析html源码后找到所有线路及站点
    lines_list = re.findall(r'class="(lines-\d{1,3}-\d)', html)

    # 找到所有线路名
    line_names = []
    for line_name in lines_list:
        # 如line|s-01-1和lines-01-2都归并到到lines01列表
        line_name_str = line_name.split('-')[0] + line_name.split('-')[1]
        if line_name_str not in line_names:
            line_names.append(line_name_str)

    # 生成线路字典，字典键为站点名，值为站点名列表
    dic = dict()
    for i in line_names:
        dic.update({i: []})

    # 构建html的soup对象
    soup = BeautifulSoup(html, 'lxml')
    for line_name in lines_list:
        print(f'正在线爬取{line_name}线的站点信息', end='')
        # div：标签名 .h18类名 默认返回列表
        line_div = soup.select(f'div .{line_name} div .h18')
        # 将其装入对应列表
        site_list = []
        for site_name in line_div:
            site_list.append(site_name.get_text())
        # 将站点名列表装入对应线路名
        line_name_str = line_name.split('-')[0] + line_name.split('-')[1]
        dic[line_name_str] += site_list
        # 使用列表集合双重转化去重，并保持原来的顺序
        l1 = dic[line_name_str]
        l2 = list(set(l1))
        l2.sort(key=l1.index)
        dic[line_name_str] = l1
        print(dic[line_name_str])
    print('爬取完成！\n')
    # 写入xlxs

    # 创建表
    data = OrderedDict()
    # Sheet1
    sheet_1 = []
    # 站点名，几号线，经纬度
    title = ['name', 'site', 'longitude', 'latitude']
    sheet_1.append(title)
    # 查询经纬度
    print('正在查询经纬度：')
    for line in dic:
        for site in dic[line]:
            longitude, latitude = get_location(site)
            row = [site, line, longitude, latitude]
            print(row)
            sheet_1.append(row)
    print('经纬度查询完成！')
    print('正在保存xlsx文件...')
    # 更新表
    data.update({'ChenDuSubway': sheet_1})
    # 保存
    save_data('./ChenDuSubway.xlsx', data)
    print('保存成功！')


# 从高德地图获取经纬度
def get_location(site):
    # 获得经纬度
    user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'
    headers = {'User-Agent': user_agent}
    url = 'http://restapi.amap.com/v3/place/text?key=' + '778f88a3593b4900e17447ad2d5dc357' + '&keywords=' + site + '&types=&city=' + '成都' + '&children=1&offset=1&page=1&extensions=all'
    data = requests.get(url, headers=headers)
    data.encoding = 'utf-8'
    data = json.loads(data.text)
    result = data['pois'][0]['location'].split(',')
    return result[0], result[1]


# 保存为get_graph文件
def get_graph():
    print('正在创建pickle文件...')
    data = pd.read_excel('./ChenDuSubway.xlsx')
    # 创建点之间的距离
    graph = defaultdict(dict)
    for i in range(data.shape[0]):
        site1 = data.iloc[i]['site']
        if i < data.shape[0] - 1:
            site2 = data.iloc[i + 1]['site']
            # 如果是共一条线
            if site1 == site2:
                longitude1, latitude1 = data.iloc[i]['longitude'], data.iloc[i]['latitude']
                longitude2, latitude2 = data.iloc[i + 1]['longitude'], data.iloc[i + 1]['latitude']
                name1 = data.iloc[i]['name']
                name2 = data.iloc[i + 1]['name']
                distance = get_the_distance(longitude1, latitude1, longitude2, latitude2)
                graph[name1][name2] = distance
                graph[name2][name1] = distance
    output = open('graph.pkl', 'wb')
    pickle.dump(graph, output)


# 计算2点之间的距离
def get_the_distance(longitude1, latitude1, longitude2, latitude2):
    user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'
    headers = {'User-Agent': user_agent}
    url = 'http://restapi.amap.com/v3/distance?key=' + '778f88a3593b4900e17447ad2d5dc357' + '&origins=' + str(
        longitude1) + ',' + str(
        latitude1) + '&destination=' + str(longitude2) + ',' + str(latitude2) + '&type=1'
    data = requests.get(url, headers=headers)
    data.encoding = 'utf-8'
    data = json.loads(data.text)
    result = data['results'][0]['distance']
    return result


if __name__ == '__main__':
    spyder()
    get_graph()
