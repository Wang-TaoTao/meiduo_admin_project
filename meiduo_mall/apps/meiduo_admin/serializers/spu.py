


from rest_framework import serializers
from apps.goods.models import SPU



# 获取SPU数据 序列化器
class SPUModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SPU
        fields = ['id','name']