# -*- coding: utf-8 -*-
from io import BytesIO
import tkinter as tk

import cv2
import requests  # 首先导入库
import re
import time
import threading
from tkinter import scrolledtext

from PIL import Image

window = tk.Tk()

window.title('网络爬虫小程序——czh')
window.geometry('1000x600')
default_value = tk.StringVar()
default_value.set('赵丽颖')
e = tk.Entry(window, show=None, textvariable=default_value)
e.pack()

##t = tk.Text(window, height=3)
t = scrolledtext.ScrolledText(window, height=100, width=400, wrap=tk.WORD)

MaxSearchPage = 1000  # 收索页数
CurrentPage = 0  # 当前正在搜索的页数
DefaultPath = "picture/"  # 默认储存位置
NeedSave = 1  # 是否需要储存
m = 1
i = 0


# 图片链接正则和下一页的链接正则
def imageFiler(content):  # 通过正则获取当前页面的图片地址数组
    return re.findall('"objURL":"(.*?)"', content, re.S)


def nextSource(content):  # 通过正则获取下一页的网址
    next = re.findall('<div id="page">.*<a href="(.*?)" class="n">', content, re.S)[0]

    ##print("---------" + "http://image.baidu.com" + next)
    return next


def spidler(source):
    content = requests.get(source).text  # 通过链接获取内容
    imageArr = imageFiler(content)  # 获取图片数组
    global CurrentPage
    ##print("Current page:" + str(CurrentPage) + "**********************************")
    global i
    for imageUrl in imageArr:
        if i >= 80:
            return
        global NeedSave
        if NeedSave:  # 如果需要保存图片则下载图片，否则不下载图片
            global DefaultPath
            try:  # 下载图片并设置超时时间,如果图片地址错误就不继续等待了
                picture = requests.get(imageUrl, timeout=5)
            except:
                ##print("Download image error! errorUrl:" + imageUrl)
                continue
            # 创建图片保存的路径
            imageUrl = imageUrl.replace('/', '').replace(':', '').replace('?', '')
            pictureSavePath = DefaultPath + imageUrl + '.jpg'
            tmpIm = BytesIO(picture.content)
            try:
                Image.open(tmpIm).verify()
            except:
                continue
            img = Image.open(tmpIm)

            s_w_h = 9 / 16
            w_h = (img.size[0]) / (img.size[1])

            if w_h < s_w_h * 0.8 or w_h > s_w_h * 1.2:
                continue
            fp = open(pictureSavePath, 'wb')  # 以写入二进制的方式打开文件
            fp.write(picture.content)
            global m
            t.insert('end', "Image" + str(m) + ":" + str(imageUrl))
            t.insert('end', '\n')
            m = m + 1
            t.pack()
            fp.close()
            i += 1
        global MaxSearchPage
        if CurrentPage <= MaxSearchPage:  # 继续下一页爬取
            if nextSource(content):
                CurrentPage += 1
                # 爬取完毕后通过下一页地址继续爬取
                spidler("http://image.baidu.com" + nextSource(content))


def beginSearch():
    ##print(1)
    # (page:爬取页数,save:是否储存,savePath:默认储存路径)
    global MaxSearchPage, NeedSave, DefaultPath
    page = 1
    MaxSearchPage = page
    save = 1
    ##savePath="D:/data/Crawler/"
    ##savePath="../Crawler/"
    NeedSave = save  # 是否保存，值0不保存，1保存
    ##DefaultPath = savePath                #图片保存的位置
    ##key = input("输入爬虫关键词：")
    key = e.get()
    StartSource = "http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=" + str(
        key) + "&ct=201326592&v=flip"  # 分析链接可以得到,替换其`word`值后面的数据来搜索关键词
    ##print(StartSource)
    ##t.insert('insert', StartSource)
    ##t.insert('insert','\n')
    ##t.pack()
    ##time.sleep(5)
    spidler(StartSource)


def thread_it():
    '''将函数打包进线程'''
    # 创建
    t2 = threading.Thread(target=beginSearch)
    # 守护 !!!
    t2.setDaemon(True)
    # 启动
    t2.start()


##b1 = tk.Button(window, text='开始爬虫', width=10,height=2, command=thread_it(beginSearch, 1))
b1 = tk.Button(window, text='开始爬虫', width=10, height=2, command=thread_it)
b1.pack()
t.pack()
window.mainloop()
