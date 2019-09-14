

from rest_framework import serializers
from apps.goods.models import SPUSpecification



# 获取规格数据 序列化器
class SPUSpec2Serializer(serializers.ModelSerializer):

    spu_id = serializers.IntegerField()
    spu = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SPUSpecification
        fields = '__all__'