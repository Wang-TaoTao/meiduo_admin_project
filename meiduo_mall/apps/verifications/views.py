from django import http
from django.shortcuts import render
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from random import randint
from libs.yuntongxun.sms import CCP
from utils.response_code import RETCODE

import logging
logger = logging.getLogger('django')

class ImageCodeView(View):

    def get(self,request,uuid):
        """
        1.获取图片验证码和验证码内容
        2.将验证码内容保存到redis中
        3.返回图片
        """

        text,image = captcha.generate_captcha()

        redis_conn = get_redis_connection('code')

        redis_conn.setex('img_%s'%uuid,120,text)

        return http.HttpResponse(image,content_type='image/jpeg')

class SmsCodeView(View):

    def get(self,request,mobile):
        """
        1.接收参数
        2.获取参数
        3.判断查询字符串是否都传递过来
        4.连接redis,获取redis的图片验证码,获取之后删除图片验证码
        5.比对redis验证码和用户提交的验证码是否一致
        6.生成短信验证码内容
        7.发送短信验证码
        8.保存短信验证码到redis中
        9.返回相应
        """

        # 1.接收参数
        params = request.GET
        # 2.获取参数
        uuid=params.get('image_code_id')
        text=params.get('image_code')
        # 3.判断查询字符串是否都传递过来
        if not all([uuid,text]):
            return http.JsonResponse({'code':RETCODE.NECESSARYPARAMERR,'errmsg':'参数不全'})
        # 4.连接redis,获取redis的图片验证码,获取之后删除图片验证码
        redis_conn = get_redis_connection('code')

        #获取标记
        send_flag = redis_conn.get('send_flag_%s'%mobile)
        if send_flag:
            return http.JsonResponse({'code':RETCODE.THROTTLINGERR,'errmsg':'稍后再试'})

        redis_text = redis_conn.get('img_%s'%uuid)
        if redis_text is None:
            return http.JsonResponse({'code':RETCODE.IMAGECODEERR,'errmsg':'图片验证码已过期'})

        try:
            redis_conn.delete('img_%s'%uuid)
        except Exception as e:
            logger.error(e)

        # 5.比对redis验证码和用户提交的验证码是否一致
        if redis_text.decode().lower() != text.lower():
            return http.JsonResponse({'code':RETCODE.IMAGECODEERR,'errmsg':'图片验证码错误'})
        # 6.生成短信验证码内容

        sms_code = '%06d'%randint(0,666666)

        pl = redis_conn.pipeline()

        # 8.保存短信验证码到redis中
        pl.setex('sms_%s' % mobile, 300, sms_code)
        # 添加标记
        pl.setex('send_flag_%s' % mobile, 60, 1)

        pl.execute()

        # # 8.保存短信验证码到redis中
        # redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        # # 添加标记
        # redis_conn.setex('send_flag_%s' % mobile, 60, 1)

        #发送短信验证码
        # CCP().send_template_sms(mobile,[sms_code,5],1)

        #调用celery任务
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile,sms_code)
        print("手机验证码是:%s" % sms_code)

        #返回相应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok'})
