
from rest_framework import serializers
from apps.goods.models import GoodsCategory, SKU


# 获取三级分类数据的序列化器
class SKUCategorieSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = ['id','name']


# 获取SKU信息的序列化器
class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = '__all__'