from django.conf.urls import include, url
from django.urls import path

from judge import views
from judge.judge_callback import start_callback_thread
from judge.judge_thread import start_judge_thread

app_name = 'judge'
urlpatterns = [
    path('push/', views.push, name='push'),
    path('tasksize/', views.task_size, name='task_size'),
]

start_judge_thread()

start_callback_thread()