


from rest_framework import serializers

from apps.goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory


# 新增频道数据---获取一级分类信息
class CategoriesSerializer(serializers.ModelSerializer):

    parent_id = serializers.IntegerField()
    parent = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsCategory
        fields = '__all__'



# 新增频道数据---获取频道组信息 序列化器
class ChannelGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsChannelGroup
        fields = '__all__'


# 获取频道信息 序列化器
class GoodsChannelSerializer(serializers.ModelSerializer):

    group_id = serializers.IntegerField()
    group = serializers.StringRelatedField(read_only=True)

    category_id = serializers.IntegerField()
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsChannel
        fields = '__all__'