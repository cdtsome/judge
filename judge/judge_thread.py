#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/8/6 14:31
# @Author  : codingtang
# @File    : judge_thread.py
from queue import Queue
from threading import Thread
from time import sleep

from judge.judge_callback import run_callback
from judge.log import logger
from judge.services.judge_service import JudgeService

q = Queue()


def log_info(msg):
    print(msg)
    logger.error(msg)


def start_judge_thread():
    log_info("startJudgeThread")
    NUM = 4
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
        arguments = q.get()  # 默认队列为空时，线程暂停
        run_judge_work(arguments)
        sleep(0.01)
        q.task_done()


def run_judge_work(arguments):
    try:
        res = JudgeService.judge(arguments)
        if res:
            run_callback(res)
        else:
            put_q_nowait_args(arguments)
    except Exception as e:
        logger.error(e.__str__())
        put_q_nowait_args(arguments)


def put_q_nowait(jr_id, exec_file, file_pre, pu_id, tps, time_limit, memory_limit, is_file, is_spj, spj_path, is_test):
    dic = dict(
        jr_id=jr_id,
        exec_file=exec_file,
        file_pre=file_pre,
        pu_id=pu_id,
        tps=tps,
        time_limit=time_limit,
        memory_limit=memory_limit,
        is_file=is_file,
        is_spj=is_spj,
        spj_path=spj_path,
        is_test=is_test
    )
    q.put_nowait(dic)


def put_q_nowait_args(args):
    q.put_nowait(args)

def get_q_size():
    return q.qsize()