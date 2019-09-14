


from rest_framework import serializers
from apps.goods.models import SPU, Brand, GoodsCategory




# 新增SPU表数据---获取一级分类信息
class CategorysSerizliser(serializers.ModelSerializer):

    parent_id = serializers.IntegerField()
    parent = serializers.StringRelatedField(read_only=True)


    class Meta:
        model = GoodsCategory
        fields= ['id','parent','parent_id','name']



# 新增SPU表数据---获取品牌信息
class BrandsSerizliser(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = '__all__'



# 获取SPU表所有数据 序列化器
class SPUSerializer(serializers.ModelSerializer):

    brand_id = serializers.IntegerField()
    brand = serializers.StringRelatedField(read_only=True)

    category1_id = serializers.IntegerField()
    category1 = serializers.StringRelatedField(read_only=True)

    category2_id = serializers.IntegerField()
    category2 = serializers.StringRelatedField(read_only=True)

    category3_id = serializers.IntegerField()
    category3 = serializers.StringRelatedField(read_only=True)


    class Meta:
        model = SPU
        fields = '__all__'



# 获取SPU表名数据 序列化器
class SPUModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SPU
        fields = ['id','name']