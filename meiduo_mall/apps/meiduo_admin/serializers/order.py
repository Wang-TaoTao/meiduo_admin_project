


from rest_framework import serializers

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods


# 获取订单详情信息中的 订单商品信息中的 图片信息 序列化器
class OrderSKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['name','default_image']



# 获取订单详情信息中的 订单商品信息  序列化器
class OrderGoodsSerializer(serializers.ModelSerializer):

    # 使用隐藏字段获取sku中的图片
    sku = OrderSKUSerializer()

    class Meta:
        model = OrderGoods
        fields = '__all__'




# 获取订单数据、订单详情信息 序列化器
class OrderSerializer(serializers.ModelSerializer):

    # 使用隐藏字段 skus 获取订单商品信息
    skus = OrderGoodsSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'