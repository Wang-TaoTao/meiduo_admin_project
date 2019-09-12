import os
from celery import Celery

#1.设置django的配置文件,celery运行要使用settings文件
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

#2.创建celery实例对象
app = Celery('meiduo_mall')

#3.加载配置文件
app.config_from_object('celery_tasks.config')

#4.自动检测任务
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email','celery_tasks.html'])