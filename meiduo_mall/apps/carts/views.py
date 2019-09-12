import base64
import json
import pickle

from django import http
from django.shortcuts import render
from django.views import View

# Create your views here.
from django_redis import get_redis_connection

from apps.goods.models import SKU
from utils.response_code import RETCODE


class CartsView(View):

    def post(self,request):
        """
        1.接收参数
        2.获取参数
        3.判断参数
            3.1 判断参数是否齐全
            3.2 判断商品id
            3.3 判断count的类型
            3.4 判断selected的类型
        4.根据用户的登陆状态进行判断
        5.登陆用户保存到redis
            5.1 连接redis
            5.2 保存数据
            5.3 返回相应
        6.未登录用户保存到cookie中
            6.1 先获取cookie数据中carts数据
            6.2 判断carts数据是否存在
                存在则解码
                不存在则初始化字典
            6.3 更新数据
            6.4 对新字典carts数据进行编码处理
            6.5 设置cookie,返回相应
        """
        # 1.接收参数
        data=json.loads(request.body.decode())
        # 2.获取参数
        sku_id=data.get('sku_id')
        count=data.get('count')
        selected=data.get('selected',True)
        # 3.判断参数
        # 3.1 判断参数是否齐全
        if not all([sku_id,count]):
            return http.HttpResponseBadRequest('参数不齐')
        # 3.2 判断商品id
        try:
            sku=SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseNotFound('暂无此商品')
        # 3.3 判断count的类型
        try:
            count=int(count)
        except Exception as e:
            return http.HttpResponseBadRequest('参数格式不正确')
        # 3.4 判断selected的类型
        if not isinstance(selected,bool):
            return http.HttpResponseBadRequest('参数格式不正确')
        # 4.根据用户的登陆状态进行判断
        if request.user.is_authenticated:
            # 5.登陆用户保存到redis
            #     5.1 连接redis
            redis_conn = get_redis_connection('carts')
            pl=redis_conn.pipeline()
            #     5.2 保存数据
            pl.hincrby('carts_%s'%request.user.id,sku_id,count)
            if selected:
                pl.sadd('selected_%s'%request.user.id,sku_id)

            pl.execute()
            #     5.3 返回相应
            return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok'})
        else:
            # 6.未登录用户保存到cookie中
            #     6.1 先获取cookie数据中carts数据
            cookie_str=request.COOKIES.get('carts')
            #     6.2 判断carts数据是否存在
            if cookie_str is not None:
                #         存在则解码
                cookie_cart=pickle.loads(base64.b64decode(cookie_str))
            else:
                #         不存在则初始化字典
                cookie_cart={}
            #     6.3 更新数据
            if sku_id in cookie_cart:
                # 累加求和
                origin_count = cookie_cart[sku_id]['count']
                count += origin_count
            cookie_cart[sku_id]={
                'count': count,
                'selected': selected
            }
            #     6.4 对新字典carts数据进行编码处理
            cookie_cart_str = base64.b64encode(pickle.dumps(cookie_cart)).decode()

            #     6.5 设置cookie,返回相应
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('carts', cookie_cart_str, max_age=3600)
            return response

    def get(self, request):
        """展示购物车"""
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询redis购物车
            redis_conn = get_redis_connection('carts')
            # 获取redis中的购物车数据
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            # 获取redis中的选中状态
            cart_selected = redis_conn.smembers('selected_%s' % user.id)

            # 将redis中的数据构造成跟cookie中的格式一致，方便统一查询
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            # 用户未登录，查询cookies购物车
            # 用户未登录，查询cookies购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
        # 构造购物车渲染数据
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount': str(sku.price * cart_dict.get(sku.id).get('count')),
            })

        context = {
            'cart_skus': cart_skus,
        }

        # 渲染购物车页面
        return render(request, 'cart.html', context)

    def put(self, request):
        """修改购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseBadRequest('缺少必传参数')
        # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseBadRequest('商品sku_id不存在')
        # 判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseBadRequest('参数count有误')
        # 判断selected是否为bool值
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseBadRequest('参数selected有误')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，修改redis购物车
            # 用户已登录，修改redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 因为接口设计为幂等的，直接覆盖
            pl.hset('carts_%s' % user.id, sku_id, count)
            # 是否选中
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()

            # 创建响应对象
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        else:
            # 用户未登录，修改cookie购物车
            # 用户未登录，修改cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            # 因为接口设计为幂等的，直接覆盖
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 创建响应对象
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('carts', cookie_cart_str, max_age=3600)
            return response

    def delete(self, request):
        """删除购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 判断sku_id是否存在
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseBadRequest('商品不存在')

        # 判断用户是否登录
        user = request.user
        if user is not None and user.is_authenticated:
            # 用户未登录，删除redis购物车
            # 用户未登录，删除redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 删除键，就等价于删除了整条记录
            pl.hdel('carts_%s' % user.id, sku_id)
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()

            # 删除结束后，没有响应的数据，只需要响应状态码即可
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
        else:
            # 用户未登录，删除cookie购物车
            # 用户未登录，删除cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            # 创建响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
            if sku_id in cart_dict:
                del cart_dict[sku_id]
                # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
                cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 响应结果并将购物车数据写入到cookie
                response.set_cookie('carts', cookie_cart_str, max_age=3600)
            return response

class CartsSelectAllView(View):
    """全选购物车"""

    def put(self, request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)

        # 校验参数
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseBadRequest('参数selected有误')

        # 判断用户是否登录
        user = request.user
        if user is not None and user.is_authenticated:
            # 用户已登录，操作redis购物车
            # 用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            cart = redis_conn.hgetall('carts_%s' % user.id)
            sku_id_list = cart.keys()
            if selected:
                # 全选
                redis_conn.sadd('selected_%s' % user.id, *sku_id_list)
            else:
                # 取消全选
                redis_conn.srem('selected_%s' % user.id, *sku_id_list)
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
        else:
            # 用户已登录，操作cookie购物车
            # 用户已登录，操作cookie购物车
            cart = request.COOKIES.get('carts')
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                for sku_id in cart:
                    cart[sku_id]['selected'] = selected
                cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                response.set_cookie('carts', cookie_cart, max_age=3600)

            return response
