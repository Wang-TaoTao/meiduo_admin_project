

from rest_framework import serializers
from apps.goods.models import SpecificationOption, SPUSpecification


# 新增规格选项信息---获取规格信息
class OptionSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = SPUSpecification
        fields = ['id','name']



# 获取规格选项信息 序列化器
class OptionSerializer(serializers.ModelSerializer):

    spec_id = serializers.IntegerField()
    spec = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SpecificationOption
        fields = '__all__'