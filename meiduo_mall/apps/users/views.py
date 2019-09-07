import json
import re
from django import http
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from apps.carts.utils import merge_cart_cookie_to_redis
from apps.goods.models import SKU
from apps.users.models import User, Address
import logging

from apps.users.utils import generate_verify_email_url, check_verify_email_token
from utils.response_code import RETCODE
from django.contrib.auth.mixins import LoginRequiredMixin

from utils.views import LoginRequiredJSONMixin

logger = logging.getLogger('django')

class RegisterView(View):

    def get(self,request):

        return render(request,'register.html')

    def post(self,request):
        """
        1.接收参数
        2.获取参数
        3.验证参数是否齐全
        4.判断用户名是否符合条件
        5.验证密码是否符合条件
        6.验证确认密码是否一致
        7.验证手机号是否正确
        8.验证是否同意协议
        9.创建用户
        10.保存登陆状态
        11.跳转到首页
        """
        # 1.接收参数
        data=request.POST
        # 2.获取参数
        username=data.get('username')
        password=data.get('password')
        password2=data.get('password2')
        mobile=data.get('mobile')
        allow=data.get('allow')
        sms_code=data.get('sms_code')
        # 3.验证参数是否齐全
        if not all([username,password,password2,mobile,allow,sms_code]):
            return http.HttpResponseBadRequest('缺少必须的参数')
        # 4.判断用户名是否符合条件
        if not re.match(r'^[0-9a-zA-Z_]{5,20}$',username):
            return http.HttpResponseBadRequest('用户名不正确')
        # 5.验证密码是否符合条件
        if not re.match(r'^[0-9a-zA-Z]{8,20}$',password):
            return http.HttpResponseBadRequest('密码格式不正确')
        # 6.验证确认密码是否一致
        if password != password2:
            return http.HttpResponseBadRequest('密码不一致')
        # 7.验证手机号是否正确
        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return http.HttpResponseBadRequest('手机号格式不正确')
        # 8.验证是否同意协议
        if allow != 'on':
            return http.HttpResponseBadRequest('未同意协议')

        #验证短信验证码
        #连接redis,获取redis的短信验证码,并且比对
        redis_conn=get_redis_connection('code')
        redis_sms_code = redis_conn.get('sms_%s'%mobile)
        if redis_sms_code is None:
            return render(request, 'register.html', {'sms_code_errmsg':'无效的短信验证码'})

        if redis_sms_code.decode() != sms_code:
            return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})

        # 9.创建用户
        try:
            user = User.objects.create_user(username=username,
                                        password=password,
                                        mobile=mobile)
        except Exception as e:
            logger.error(e)
            return render(request,'register.html',{'register_errmsg':'创建失败'})
        # 10.保存登陆状态
        login(request,user)
        # 11.跳转到首页
        return redirect(reverse('contents:index'))
        # return http.HttpResponse('注册成功，重定向到首页')

class RegisterUsernameCountView(View):

    def get(self,request,username):
        """
         1.根据用户名查询数量
         2.返回个数信息
        """
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':'数据查询失败'})

        return http.JsonResponse({'code':RETCODE.OK,'msg':'ok','count':count})

class RegisterMobileCountView(View):

    def get(self,request,mobile):
        """
         1.根据用户名查询数量
         2.返回个数信息
        """
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':'数据查询失败'})

        return http.JsonResponse({'code':RETCODE.OK,'msg':'ok','count':count})

class LoginView(View):

    def get(self,request):

        return render(request,'login.html')

    def post(self,request):
        """
         1.接收参数
         2.获取参数
         3.判断参数是否齐全
         4.判断用户名是否符合要求
         5.判断密码是否符合要求
         6.根据用户名进行查询
         7.根据是否记住密码设置会话有效期
         8.跳转到首页
        """
        # 1.接收参数
        data=request.POST
        # 2.获取参数
        username=data.get('username')
        password=data.get('password')
        is_remembered=data.get('remembered')
        # 3.判断参数是否齐全
        if not all([username,password,is_remembered]):
            return http.HttpResponseBadRequest('参数不全')
        # 4.判断用户名是否符合要求
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return http.HttpResponseBadRequest('用户名格式不正确')
        # 5.判断密码是否符合要求
        if not re.match(r'^[0-9A-Za-z]{8,20}$',password):
            return http.HttpResponseBadRequest('密码格式不正确')
        # 6.进行用户名和密码的验证
        from django.contrib.auth import authenticate
        user = authenticate(request,username=username,password=password)
        if user is None:
            return render(request,'login.html',{'errmsg':'用户名或密码错误'})
        # 7.根据是否记住密码设置会话有效期
        login(request,user)
        if is_remembered != 'on':
            request.session.set_expiry(0)
        # 8.跳转到首页/next页面
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))

        response.set_cookie('username',username,max_age=15*24*3600)

        response = merge_cart_cookie_to_redis(request=request, user=user, response=response)

        return response

class LogoutView(View):

    def get(self,request):
        #退出登陆
        from django.contrib.auth import logout
        logout(request)

        #清除cookie信息中的username
        response = redirect(reverse('contents:index'))

        response.delete_cookie('username')

        return response

class UserInfoView(LoginRequiredMixin,View):

    def get(self,request):

        context = {
            'username':request.user.username,
            'mobile':request.user.mobile,
            'email':request.user.email,
            'email_active':request.user.email_active
        }

        return render(request,'user_center_info.html',context)

class EmailView(LoginRequiredJSONMixin,View):

    def put(self,request):
        """
        1.接收参数
        2.获取参数
        3.验证参数
        4.更新数据
        5.返回相应
        """
        # 1.接收参数
        data=request.body
        body_str=data.decode()
        params=json.loads(body_str)
        # 2.获取参数
        email=params.get('email')
        # 3.验证参数
        if not email:
            return http.HttpResponseBadRequest('参数不能省略')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return http.HttpResponseBadRequest('参数不符合规则')
        # 4.更新数据
        try:
            request.user.email=email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        #发送邮件
        from celery_tasks.email.tasks import send_verify_email
        verify_email=generate_verify_email_url(request.user)
        send_verify_email.delay(email,verify_email)

        # 5.返回相应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok'})

class VerifyEmailView(View):
    """验证邮箱"""

    def get(self, request):
        """
        1.接收参数
        2.判断参数是否为空
        3.对token进行验证码
        4.修改邮件激活状态
        5.返回相应,调转到指定页面
        """
        # 1.接收参数
        token = request.GET.get('token')
        # 2.判断参数是否为空
        if token is None:
            return http.HttpResponseBadRequest('缺少参数')
        # 3.对token进行验证码
        user = check_verify_email_token(token)
        # 4.修改邮件激活状态
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮件失败')

        # 5.返回相应,调转到指定页面
        return redirect(reverse('users:info'))

class AddressView(LoginRequiredJSONMixin,View):

    def get(self,request):
        """
         1.查询用户地址列表
         2.将对象列表转换为字典列表
         3.返回相应
        """
        # 1.查询用户地址列表
        user=request.user
        addresses=user.addresses.filter(is_deleted=False)
        # 2.将对象列表转换为字典列表
        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "province_id":address.province_id,
                "city": address.city.name,
                "city_id":address.city_id,
                "district": address.district.name,
                "district_id":address.district_id,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        # 3.返回相应
        context = {
            'default_address_id':user.default_address_id,
            'addresses':address_dict_list
        }
        return render(request,'user_center_site.html',context=context)

class CreateAddressView(LoginRequiredJSONMixin,View):

    def post(self,request):
        """
         1.判断地址数量是否达到上限
         2.接收参数
         3.验证参数是否齐全
         4.判断手机号，电话，邮箱是否符合规则
         5.保存地址
         6.设置默认地址
         7.组织返回数据
         8.返回相应结果
        """
        # 1.判断地址数量是否达到上限
        count=Address.objects.filter(user=request.user).count()
        if count >= 20:
            return http.JsonResponse({'code':RETCODE.THROTTLINGERR,'errmsg':'超过地址数量上限'})
        # 2.接收参数
        body=request.body
        body_str=body.decode()
        data=json.loads(body_str)
        receiver=data.get('receiver')
        province_id=data.get('province_id')
        city_id=data.get('city_id')
        district_id=data.get('district_id')
        place=data.get('place')
        mobile=data.get('mobile')
        tel=data.get('tel')
        email=data.get('email')

        # 3.验证参数是否齐全
        if not all([receiver,province_id,city_id,district_id,place,mobile]):
            return http.HttpResponseBadRequest('参数不全')
        # 4.判断手机号，电话，邮箱是否符合规则
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')
        # 5.保存地址
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            # 6.设置默认地址
            if not request.user.default_address:
                request.user.default_address=address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})
        # 7.组织返回数据
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # 8.返回相应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})

class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):

    def put(self,request,address_id):
        """
         1.接收数据
         2.验证数据
         3.验证参数是否齐全
         4.判断手机号，电话，邮箱是否符合规则
         5.判断地址是否存在,并更新地址
         6.构造相应数据
         7.返回相应
        """
        #1.接收数据
        body = request.body
        body_str = body.decode()
        data = json.loads(body_str)
        # 2.接收参数
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')

        # 3.验证参数是否齐全
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('参数不全')
        # 4.判断手机号，电话，邮箱是否符合规则
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')
        # 5.判断地址是否存在,并更新地址
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':'数据库错误'})
        # 6.构造相应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # 7.返回相应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self,request,address_id):
        """
        1.查询数据
        2.修改标记位
        3.返回相应
        """
        try:
            #1.查询数据
            address=Address.objects.get(id=address_id)
            #2.修改标记位
            address.is_deleted=True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':'数据库异常'})

        #3.返回相应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'删除成功'})

class DefaultAddressView(LoginRequiredJSONMixin, View):

    def put(self,request,address_id):
        """
        1.查询数据
        2.修改数据
        3.返回相应
        """
        try:
            # 接收参数,查询地址
            address = Address.objects.get(id=address_id)

            # 设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})

            # 响应设置默认地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})

class UpdateTitleAddressView(LoginRequiredJSONMixin, View):

    def put(self,request,address_id):
        """
        1.接收参数
        2.查询数据
        3.更新数据
        4.返回相应
        """
        # 1.接收参数
        data = json.loads(request.body.decode())
        title = data.get('title')
        # 2.查询数据
        try:
            address = Address.objects.get(id=address_id)

            # 3.更新数据
            address.title=title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':'数据库异常'})
        # 4.返回相应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})

class ChangePasswordView(LoginRequiredMixin, View):
    """修改密码"""

    def get(self, request):
        """展示修改密码界面"""
        return render(request, 'user_center_pass.html')

    def post(self, request):
        """
        1.接收参数
        2.验证参数
        3.检验旧密码是否正确
        4.更新新密码
        5.退出登陆,删除登陆信息
        6.跳转到登陆页面
        """
        # 1.接收参数
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')
        # 2.验证参数
        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.HttpResponseBadRequest('密码最少8位，最长20位')
        if new_password != new_password2:
            return http.HttpResponseBadRequest('两次输入的密码不一致')

        # 3.检验旧密码是否正确
        if not request.user.check_password(old_password):
            return render(request, 'user_center_pass.html', {'origin_password_errmsg':'原始密码错误'})
        # 4.更新新密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_password_errmsg': '修改密码失败'})
        # 5.退出登陆,删除登陆信息
        logout(request)
        # 6.跳转到登陆页面
        response = redirect(reverse('users:login'))

        response.delete_cookie('username')

        return response

class UserHistoryView(LoginRequiredJSONMixin,View):

    def get(self,request):
        """
        1.获取用户信息
        2.连接redis
        3.获取ids信息
        4.根据id信息获取商品详细信息
        5.对象转换为字典
        6.返回相应
        """
        # 1.获取用户信息
        user = request.user
        # 2.连接redis
        redis_conn = get_redis_connection('history')
        # 3.获取ids信息
        ids = redis_conn.lrange('history_%s'%user.id,0,4)
        # 4.根据id信息获取商品详细信息
        skus = []
        for id in ids:
            sku = SKU.objects.get(pk=id)
            # 5.对象转换为字典
            skus.append({
                'id':sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })

        # 6.返回相应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok','skus':skus})

    def post(self,request):
        """
        1.接收参数
        2.验证参数
        3.连接redis
        4.去重
        5.添加
        6.保存指定数量历史记录
        7.返回相应
        """
        # 1.接收参数
        data=json.loads(request.body.decode())
        sku_id=data.get('sku_id')
        # 2.验证参数
        try:
            SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.NODATAERR,'errmsg':'暂无此数据'})
        # 3.连接redis
        redis_conn = get_redis_connection('history')
        pl=redis_conn.pipeline()

        user = request.user
        # 4.去重
        pl.lrem('history_%s'%user.id,0,sku_id)
        # 5.添加
        pl.lpush('history_%s'%user.id,sku_id)
        # 6.保存指定数量历史记录
        pl.ltrim('history_%s'%user.id,0,4)
        pl.execute()
        # 7.返回相应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK'})

