#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Software: PyCharm
# @Time    : 2022/7/14 11:10
# @File    : main.py
# @Author  : Xue Jinlong

import time, re, os
import requests
from selenium import webdriver
from tqdm import tqdm


keywords = "Weakly Supervised Semantic Segmentation"
# driverpath = "D:\Chromedriver\chromedriver.exe"
driverpath = "/usr/bin/chromedriver"
options = webdriver.ChromeOptions()
options.add_argument('headless')

def main():
    # 如果存放标题文件不存在则创建该文件
    if not os.path.exists("title.txt"):
        file = open("title.txt", "w")
        file.write("title\tpublished\tdate\n")

    # 拼接网址开始启动爬虫
    keyword = keywords.replace(" ", "+")
    # driver = webdriver.Chrome(executable_path=driverpath)
    driver = webdriver.Chrome(executable_path=driverpath, options=options)
    # 打开首页往下滑三页
    driver.get("https://dblp.uni-trier.de/search/publ?q={}".format(keyword))
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
    text = driver.page_source
    # 调整获得的标题格式
    paper_titles = re.findall('<span class="title" itemprop="name">(.+?).</span>', text)
    for i, title in enumerate(paper_titles):
        title = title.replace(' <mark data-markjs="true">', " ")
        title = title.replace('<mark data-markjs="true">', "")
        title = title.replace('</mark>', "")

        paper_titles[i] = title
    # 获得发表期刊或会议名称
    names = re.findall('<span itemprop="name">(.+?)</span>', text)
    # 获得发表时间
    date = re.findall('<span itemprop="datePublished">(.+?)</span>', text)

    # 读取论文库中已有的论文
    global exit_lists
    with open(file="title.txt", mode='r') as f:
        exit_lists = f.readlines()

    # 开始将获得的论文写入到文件中
    print("共有{}篇，开始检测。。。".format(len(paper_titles)))
    write_list = []
    with open(file="title.txt", mode='a') as f:
        for i, title in tqdm(enumerate(paper_titles)):
            global is_write
            is_write = True
            for exit_list in exit_lists:
                if title in exit_list:
                    is_write = False
            if is_write:
                write_list.append("{} | {} | {}\n".format(title, names[i], date[i]))
                f.write("{}\t{}\t{}\n".format(title, names[i], date[i]))
    print("写入完成！", write_list)
    if write_list != []:
        # 生成发送Markdown
        send_title = """title | published | date\n---|---|---\n"""
        with open("temporary.txt", "w") as f:
            f.write(send_title)
        with open("temporary.txt", "a") as f:
            for i in write_list:
                f.write(i)
        # 发送Markdown
        with open("temporary.txt", "r") as f:
            content = f.read()
            print(content)
            requests.get("https://sctapi.ftqq.com/SCT14069TgycwQ5V4kedvBKQMOVM8tI91.send?title=有新论文啦&desp={}".format(content))



if __name__ == '__main__':
    main()

