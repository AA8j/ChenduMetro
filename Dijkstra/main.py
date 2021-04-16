# -*- coding: utf-8 -*-
# @Time    : 2021/4/16 6:08
# @Author  : AA8j
# @FileName: main.py
# @Software: PyCharm
# @Blog    ：https://blog.csdn.net/qq_44874645
import os
from geopy.distance import geodesic

from 算法.Dijkstra.CrawlChenduSubway import *


# 找最近的地铁站
def get_nearest_subway(data, longitude1, latitude1):
    # 找最近的地铁站
    longitude1 = float(longitude1)
    latitude1 = float(latitude1)
    distance = float('inf')
    nearest_subway = None
    for i in range(data.shape[0]):
        site1 = data.iloc[i]['name']
        longitude = float(data.iloc[i]['longitude'])
        latitude = float(data.iloc[i]['latitude'])
        temp = geodesic((latitude1, longitude1), (latitude, longitude)).m
        if temp < distance:
            distance = temp
            nearest_subway = site1
    return nearest_subway


# 读取图的信息
def subway_line(start, end):
    file = open('graph.pkl', 'rb')
    graph = pickle.load(file)
    # 创建点之间的距离
    # 现在我们有了各个地铁站之间的距离存储在graph
    # 创建节点的开销表，cost是指从start到该节点的距离
    costs = {}
    parents = {end: None}
    for node in graph[start].keys():
        costs[node] = float(graph[start][node])
        parents[node] = start
    # 终点到起始点距离为无穷大
    costs[end] = float('inf')
    # 记录处理过的节点list
    processed = []
    shortest_path = dijkstra(start, end, graph, costs, processed, parents)
    return shortest_path


# 计算图中从start到end的最短路径
def dijkstra(start, end, graph, costs, processed, parents):
    # 查询到目前开销最小的节点
    node = find_lowest_cost_node(costs, processed)
    # 使用找到的开销最小节点，计算它的邻居是否可以通过它进行更新
    # 如果所有的节点都在processed里面 就结束
    while node is not None:
        # 获取节点的cost
        cost = costs[node]  # cost 是从node 到start的距离
        # 获取节点的邻居
        neighbors = graph[node]
        # 遍历所有的邻居，看是否可以通过它进行更新
        for neighbor in neighbors.keys():
            # 计算邻居到当前节点+当前节点的开销
            new_cost = cost + float(neighbors[neighbor])
            if neighbor not in costs or new_cost < costs[neighbor]:
                costs[neighbor] = new_cost
                # 经过node到邻居的节点，cost最少
                parents[neighbor] = node
        # 将当前节点标记为已处理
        processed.append(node)
        # 下一步继续找U中最短距离的节点  costs=U,processed=S
        node = find_lowest_cost_node(costs, processed)

    # 循环完成 说明所有节点已经处理完
    shortest_path = find_shortest_path(start, end, parents)
    shortest_path.reverse()
    return shortest_path


# 找到开销最小的节点
def find_lowest_cost_node(costs, processed):
    # 初始化数据
    lowest_cost = float('inf')  # 初始化最小值为无穷大
    lowest_cost_node = None
    # 遍历所有节点
    for node in costs:
        # 如果该节点没有被处理
        if not node in processed:
            # 如果当前的节点的开销比已经存在的开销小，那么久更新该节点为最小开销的节点
            if costs[node] < lowest_cost:
                lowest_cost = costs[node]
                lowest_cost_node = node
    return lowest_cost_node


# 找到最短路径
def find_shortest_path(start, end, parents):
    node = end
    shortest_path = [end]
    # 最终的根节点为start
    while parents[node] != start:
        shortest_path.append(parents[node])
        node = parents[node]
    shortest_path.append(start)
    return shortest_path


def main(site1, site2):
    # 查看是否有pkl文件
    if not os.path.exists('./graph.pkl'):
        # 查看是否有成都地铁的xlsx文件，没有则创建
        if not os.path.exists('./ChenDuSubway.xlsx'):
            spyder()
        # 如果有直接创建pkl图
        get_graph()

    longitude1, latitude1 = get_location(site1)
    longitude2, latitude2 = get_location(site2)
    data = pd.read_excel('./ChenDuSubway.xlsx')
    print('正在寻找最近的地铁站：')
    # 求最近的地铁站
    start = get_nearest_subway(data, longitude1, latitude1)
    print(start)
    print('正在寻找距目标最近的地铁站')
    end = get_nearest_subway(data, longitude2, latitude2)
    print(end)
    # 正在读取pkl图
    shortest_path = subway_line(start, end)
    if site1 != start:
        shortest_path.insert(0, site1)
    if site2 != end:
        shortest_path.append(site2)
    print('路线规划为：', '-->'.join(shortest_path))


if __name__ == '__main__':
    main('成都大学', '四川师范大学')
