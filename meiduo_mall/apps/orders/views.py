import json
from decimal import Decimal

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

# Create your views here.
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from utils.response_code import RETCODE
from utils.views import LoginRequiredJSONMixin


class OrderSettlementView(LoginRequiredMixin,View):

    def get(self,request):

        """
        1.获取用户信息
        2.获取用户地址信息
        3.获取redis中的信息
        4.组织转换成选中商品的信息
        5.遍历信息
        6.计算总价格和总数量
        """
        # 1.获取用户信息
        user=request.user
        # 2.获取用户地址信息
        try:
            addresses=Address.objects.filter(user=user)
        except Exception as e:
            addresses=None

        # 3.获取redis中的信息
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        cart_selected = redis_conn.smembers('selected_%s' % user.id)
        # 4.组织转换成选中商品的信息
        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])
        #初始化统计数据
        total_amount=0
        total_count=Decimal(0.00)
        skus=SKU.objects.filter(pk__in=cart.keys())
        # 5.遍历信息
        for sku in skus:

            sku.count=cart[sku.id]
            sku.amount=sku.price*sku.count
            # 6.计算总价格和总数量
            total_amount+=sku.amount
            total_count+=sku.count

        # 补充运费
        freight = Decimal('10.00')
        #组织上下文
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }

        return render(request,'place_order.html',context)

class OrderCommitView(LoginRequiredJSONMixin, View):
    """订单提交"""

    def post(self, request):
        """
        保存订单信息和订单商品信息
        1.生成订单信息
            1.1接收数据
            1.2验证数据
            1.3获取登陆用户信息
            1.4生成订单id
            1.5初始化订单金额等信息
            1.6判断订单状态
        2.生成订单商品信息
            2.1连接redis,获取redis选中商品的数据
            2.2获取商品id
            2.3遍历商品id
            2.4查询商品
            2.5判断库存是否充足
            2.6库存减少,销量增加
            2.7保存订单商品
            2.8累加订单信息
        3.清除购物车数据
        4.返回相应
        """
        # 1.生成订单信息
        #     1.1接收数据
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        #     1.2验证数据
        # 校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseBadRequest('缺少必传参数')
        # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return http.HttpResponseBadRequest('参数address_id错误')
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseBadRequest('参数pay_method错误')
        #     1.3获取登陆用户信息
        user=request.user
        #     1.4生成订单id
        from django.utils import timezone
        order_id=timezone.localtime().strftime('%Y%m%d%H%M%S') + '%09d'%user.id
        #     1.5初始化订单金额等信息
        total_amount=Decimal('0')
        total_count=0
        freight=Decimal('10.00')
        #     1.6判断订单状态
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status=OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        order=OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_amount=total_amount,
            total_count=total_count,
            freight=freight,
            pay_method=pay_method,
            status=status
        )
        # 2.生成订单商品信息
        #     2.1连接redis,获取redis选中商品的数据
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        selected = redis_conn.smembers('selected_%s' % user.id)
        carts = {}
        for sku_id in selected:
            carts[int(sku_id)] = int(redis_cart[sku_id])
        #     2.2获取商品id
        sku_ids = carts.keys()
        #     2.3遍历商品id
        for sku_id in sku_ids:
            # 查询SKU信息
            sku = SKU.objects.get(id=sku_id)
            #     2.4查询商品
            sku_count = carts[sku.id]
            #     2.5判断库存是否充足
            if sku_count > sku.stock:
                return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
            #     2.6库存减少,销量增加
            import time
            time.sleep(5)

            sku.stock -= sku_count
            sku.sales += sku_count
            sku.save()
            #     2.7保存订单商品
            OrderGoods.objects.create(
                order=order,
                sku=sku,
                count=sku_count,
                price=sku.price,
            )
            #     2.8累加订单信息
            order.total_count += sku_count
            order.total_amount += (sku_count * sku.price)

        # 添加邮费和保存订单信息
        order.total_amount += order.freight
        order.save()

        # 3.清除购物车数据
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *selected)
        pl.srem('selected_%s' % user.id, *selected)
        pl.execute()

        # 4.返回相应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})

class OrderSuccessView(LoginRequiredMixin, View):
    """提交订单成功"""

    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id':order_id,
            'payment_amount':payment_amount,
            'pay_method':pay_method
        }
        return render(request, 'order_success.html', context)


