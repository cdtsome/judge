#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/8/6 11:49
# @Author  : codingtang
# @File    : judge_service.py
import codecs
import json
import os
import shutil

import lorun
import os


from judge.judge_callback import run_callback
from judge.log import logger



RESULT_STR = [
    'Accepted',
    'Presentation Error',
    'Time Limit Exceeded',
    'Memory Limit Exceeded',
    'Wrong Answer',
    'Runtime Error',
    'Output Limit Exceeded',
    'Compile Error',
    'System Error'
]

INPUT_DIR = '/judge/inp/point/'
INPUT_EXT = '.in'
OUTPUT_EXT = '.out'


class JudgeService:
    @classmethod
    def run_one(cls, exec_cmd, input_path, user_out_path, time_limit, memory_limit, file_out_path=None, is_spj=False,
                spj_path=None, right_out_path=None):
        '''
        测评
        :param exec_cmd:
        :param input_path:
        :param user_out_path:
        :param time_limit:
        :param memory_limit:
        :param is_spj:
        :param spj_path:
        :return:
        '''
        try:
            runcfg = {
                # 'args': [execute_cmd, ],
                'args': exec_cmd.split(" "),
                # 'timelimit': 1000,  # in MS
                'timelimit': time_limit,  # in MS
                # 'memorylimit': 200000,  # in KB
                'memorylimit': memory_limit,  # in KB
                # 'trace':True,
                # 'calls':[1, 2, 3, 4],
                # 'files':{'/etc/ld.so.cache': 0}
            }
            fin = None
            fout = None
            fout_std = None
            # if input:
            #     runcfg['input'] = input

            if input_path:
                # fin = open(in_path)
                fin = codecs.open(input_path, 'r', 'utf-8')
                runcfg['fd_in'] = fin.fileno()

            if right_out_path:
                fout_std = codecs.open(right_out_path, 'r', 'utf-8')
                # fout_std = open(right_out_path)
                runcfg['fd_std_out'] = fout_std.fileno()
            if user_out_path:
                fout = codecs.open(user_out_path, 'w+', 'utf-8')
                # fout = open(user_out_path, 'w+')
                # print(user_out_path)
                runcfg['fd_out'] = fout.fileno()
            if file_out_path:
                # fout = codecs.open(file_out_path, 'w+', 'utf-8')
                # print(file_out_path)
                runcfg['file_out_path'] = file_out_path
                dir = os.path.dirname(file_out_path)
                runcfg['exec_dir'] = dir

            if is_spj and spj_path:
                runcfg['is_spj'] = 1
                runcfg['spj_path'] = spj_path

            rst = lorun.run_no_check(runcfg)
            # here rst['result'] == 0 表示 代码执行了，但结果不一定正确
            if rst['result'] == 0 and not is_spj:
                rst['result_str'] = ''
            else:
                rst['result_str'] = RESULT_STR[rst['result']]
            if fin:
                fin.close()
            if fout_std:
                fout_std.close()
            if fout:
                fout.close()
            # print("output=" + rst['output'])
            return rst
        except Exception as e:
            print(e.__str__())
            logger.error(e.__str__())
            return None

    @classmethod
    def judge(cls, arguments):
        '''
        :param arguments:
        :return:
        '''
        if arguments['is_test'] is True:
            return cls.judge_one_test(arguments)
        if arguments['is_file'] is True:
            return cls.judge_one_file(arguments)
        else:
            return cls.judge_one(arguments)

    @classmethod
    def judge_one(cls, arguments):
        jr_id = arguments['jr_id']
        exec_file = arguments['exec_file']
        file_pre = arguments['file_pre']
        pu_id = arguments['pu_id']
        tps = arguments['tps']
        time_limit = arguments['time_limit']
        memory_limit = arguments['memory_limit']
        is_spj = arguments['is_spj']
        spj_path = arguments['spj_path']

        logger.error(json.dumps(arguments))
        rst = dict(
            jr_id=jr_id,
            file_pre=file_pre,
            uuid=pu_id,
            is_spj=is_spj,
            is_test=False,
            res=[]
        )
        for tp_id in tps:
            testpoint_in_path = INPUT_DIR + pu_id + '/' + str(tp_id) + INPUT_EXT
            user_out_path = file_pre + '_' + str(tp_id) + '.usrout'
            # if os.path.exists(user_out_path):
            #     os.remove(user_out_path)
            # if not os.path.exists(user_out_path):
            #     f = codecs.open(user_out_path, 'w', 'utf-8')
            #     f.close()
            output_path = None
            if is_spj:
                output_path = file_pre + '_' + str(tp_id) + '.tmpout'
            one_res = cls.run_one(exec_file, testpoint_in_path, user_out_path, time_limit, memory_limit, None, is_spj,
                                  spj_path, output_path)
            rst['res'].append(dict(
                tp_id=tp_id,
                res=one_res
            ))
        return rst

    @classmethod
    def judge_one_file(cls, arguments):
        jr_id = arguments['jr_id']
        exec_file = arguments['exec_file']
        file_pre = arguments['file_pre']
        pu_id = arguments['pu_id']
        tps = arguments['tps']
        time_limit = arguments['time_limit']
        memory_limit = arguments['memory_limit']
        is_spj = arguments['is_spj']
        spj_path = arguments['spj_path']

        rst = dict(
            jr_id=jr_id,
            uuid=pu_id,
            file_pre=file_pre,
            is_spj=is_spj,
            is_test=False,
            res=[]
        )
        for tp_id in tps:
            testpoint_in_path = INPUT_DIR + pu_id + '/' + str(tp_id) + INPUT_EXT

            # 这时候重定向用户输入和用户输出，将input改为目录+en_title.in，标准输出不变，用户输出改为 目录+en_title.out
            test_point_file_in_path = file_pre + '.in'
            if os.path.exists(test_point_file_in_path):
                os.remove(test_point_file_in_path)
            shutil.copyfile(testpoint_in_path, test_point_file_in_path)
            test_point_file_user_out_path = file_pre + '.out'
            if os.path.exists(test_point_file_user_out_path):
                os.remove(test_point_file_user_out_path)
            if not os.path.exists(test_point_file_user_out_path):
                f = codecs.open(test_point_file_user_out_path, 'w', 'utf-8')
                # f = open(test_point_user_out_path, 'w')
                f.close()

            output_path = None
            if is_spj:
                output_path = file_pre + '_' + str(tp_id) + '.tmpout'

            one_res = cls.run_one(exec_file, None, None, time_limit, memory_limit, test_point_file_user_out_path, is_spj,
                                  spj_path, output_path)
            rst['res'].append(dict(
                tp_id=tp_id,
                res=one_res
            ))

            # 这时候重定向用户输出，用户输出改为 目录+en_title + _ +tp_id.out
            if os.path.exists(test_point_file_in_path):
                os.remove(test_point_file_in_path)
            test_point_file_user_tp_path = file_pre + '_' + str(tp_id) + '.out'
            if os.path.exists(test_point_file_user_tp_path):
                os.remove(test_point_file_user_tp_path)
            shutil.copyfile(test_point_file_user_out_path, test_point_file_user_tp_path)
            if os.path.exists(test_point_file_user_out_path):
                os.remove(test_point_file_user_out_path)

            os.chmod(test_point_file_user_tp_path, mode=0o766)

        return rst

    @classmethod
    def judge_one_test(cls, arguments):
        jr_id = arguments['jr_id']
        exec_file = arguments['exec_file']
        file_pre = arguments['file_pre']
        pu_id = arguments['pu_id']
        tps = arguments['tps']
        time_limit = arguments['time_limit']
        memory_limit = arguments['memory_limit']
        is_spj = arguments['is_spj']
        spj_path = arguments['spj_path']

        logger.error(json.dumps(arguments))
        rst = dict(
            jr_id=jr_id,
            file_pre=file_pre,
            uuid=pu_id,
            is_spj=is_spj,
            is_test=True,
            res=[]
        )
        testpoint_in_path = file_pre + '.in'
        user_out_path = file_pre + '.out'
        cls.run_one(exec_file, testpoint_in_path, user_out_path, time_limit, memory_limit, None, False,
                              None, None)
        return rst