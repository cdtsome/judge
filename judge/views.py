from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from judge.judge_thread import put_q_nowait, get_q_size
from judge.log import logger
from judge.services.judge_service import JudgeService
import json


@csrf_exempt
def push(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode().replace("'", "\""))
        jr_id = data['jr_id']
        exec_file = data['exec_file']
        file_pre = data['file_pre']
        pu_id = data['pu_id']
        tps = data['tps']
        time_limit = data['time_limit']
        memory_limit = data['memory_limit']
        is_file = data['is_file']
        is_spj = data['is_spj']
        spj_path = data['spj_path']
        is_test = data['is_test']

        logger.info('receive jr_id: ' + str(jr_id))
        put_q_nowait(jr_id, exec_file, file_pre, pu_id, tps, time_limit, memory_limit, is_file, is_spj, spj_path, is_test)
    return JsonResponse({'success': True})


def task_size(request):
    size = get_q_size()
    response_data = {}
    response_data['size'] = size
    print("task size:" + str(size))
    return JsonResponse(response_data)
