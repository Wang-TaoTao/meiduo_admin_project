import re

from django import http
from django.contrib.auth import login
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django_redis import get_redis_connection

from apps.oauth.models import OAuthQQUser
from apps.oauth.utils import generate_eccess_token, check_access_token
from apps.users.models import User
from meiduo_mall import settings
from utils.response_code import RETCODE
import logging
logger = logging.getLogger('django')


class QQOauthURLView(View):

    def get(self,request):
        #1.创建实例
        next = request.GET.get('next')
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)
        #2.获取url
        login_url = oauth.get_qq_url()
        #3.返回相应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok','login_url':login_url})

class QQOauthUserView(View):

    def get(self,request):
        """
        1.获取code
        2.通过code换取token
        3.通过token换取openid
        4.根据openid进行查询,判断用户之前是否绑定过
        5.绑定过则登陆
        6.没有绑定过则进行绑定
        """
        # 1.获取code
        code = request.GET.get('code')
        if code is None:
            return http.HttpResponseBadRequest('缺少必须的参数')
        # 2.通过code换取token
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            token = oauth.get_access_token(code)
            # 3.通过token换取openid
            openid = oauth.get_open_id(token)
            # 4.根据openid进行查询,判断用户之前是否绑定过
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('绑定失败')

        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 6.没有绑定过则进行绑定
            access_token = generate_eccess_token(openid)
            context = {'access_token': access_token}
            return render(request, 'oauth_callback.html', context)
        else:
            # 5.绑定过则登陆
            # 设置登陆状态
            login(request, qquser.user)

            # 记录cookie信息
            next = request.GET.get('state')
            response = redirect(next)

            response.set_cookie('username', qquser.user.username, max_age=15 * 24 * 3600)

            return response

    def post(self,request):
        """
         1.接收参数
         2.获取参数
         3.判断参数是否齐全
         4.判断手机号是否符合规则
         5.判断密码是否符合规则
         6.判断短信验证码是否正确
         7.判断access_token(openid)是否一致
         8.根据手机号进行用户信息的确认
         9.绑定
         10.设置登陆状态信息
         11.设置cookie信息
         12.跳转页面
        """
        # 1.接收参数
        data=request.POST
        # 2.获取参数
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code_client = data.get('sms_code')
        access_token = data.get('access_token')
        # 3.判断参数是否齐全
        if not all([mobile,password,sms_code_client,access_token]):
            return http.HttpResponseBadRequest('参数不全')
        # 4.判断手机号是否符合规则
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('请输入正确的手机号码')
        # 5.判断密码是否符合规则
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        # 6.判断短信验证码是否正确
        redis_conn = get_redis_connection('code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})

        # 7.判断access_token(openid)是否一致
        openid = check_access_token(access_token)
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})

        # 8.根据手机号进行用户信息的确认
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 用户不存在,新建用户
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:
            # 如果用户存在，检查用户密码
            if not user.check_password(password):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})
        # 9.绑定
        try:
            OAuthQQUser.objects.create(openid=openid, user=user)
        except DatabaseError:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})
        # 10.设置登陆状态信息
        login(request, user)

        next = request.GET.get('state')
        response = redirect(next)

        # 11.设置cookie信息
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response


