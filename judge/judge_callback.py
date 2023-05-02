#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/8/6 15:13
# @Author  : codingtang
# @File    : judge_callback.py
import json
from queue import Queue
from threading import Thread
from time import sleep

import requests

# CALLBACK_URL = 'http://host.docker.internal:8001/judgemachine/scallback/'

# product
CALLBACK_URL = 'http://host.docker.internal:9000/judgemachine/scallback/'
# CALLBACK_URL = 'http://172.19.179.159/judgemachine/scallback/'
cq = Queue()


def start_callback_thread():
    print("startJudgeThread")
    #refreshSeason()
    #print("refreshReason")
    NUM = 1
    threads = []
    # 开启线程
    for i in range(NUM):
        t = Thread(target=working)  # 线程的执行函数为working
        threads.append(t)

    for item in threads:
        item.setDaemon(True)
        item.start()


def working():
    while True:
        # refreshSeason()
        arguments = cq.get()  # 默认队列为空时，线程暂停
        run_callback(arguments)
        sleep(0.01)
        cq.task_done()


def run_callback(arguments, repeat=True):
    try:
        # print("url: {}".format(url))
        req = requests.post(CALLBACK_URL, json=arguments, timeout=5)

        if req.status_code != 200 and repeat:
            sleep(1000)
            run_callback(arguments, False)
            # put_cq_to_db(judge_record.id)

    except Exception as e:
        print('runCallback:' + e.__str__())
        put_cq_nowait(arguments)


def put_cq_nowait(arguments):
    cq.put_nowait(arguments)