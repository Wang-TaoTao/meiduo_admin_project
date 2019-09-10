



from rest_framework import serializers

from apps.goods.models import SKUImage, SKU


# 获取图片数据 序列化器
class SKUImageSerializer(serializers.ModelSerializer):

    # 设置外键
    sku = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SKUImage
        fields = ['id','sku','image']


# 获取新增图片时的SKU数据 序列化器
class SimpleSKUSerializer(serializers.ModelSerializer):


    class Meta:
        model = SKU
        fields = ['id','name']

