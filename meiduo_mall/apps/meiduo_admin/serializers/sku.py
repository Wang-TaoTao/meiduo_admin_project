from django.db import transaction
from rest_framework import serializers
from apps.goods.models import GoodsCategory, SKU, SpecificationOption, SPUSpecification, SKUSpecification


# 新增SKU数据时候的 根据规格信息获取 规格选项信息的序列化器   （15.6寸，黑色等）
class SpecificationOptionSerializer(serializers.ModelSerializer):


    class Meta:
        model = SpecificationOption
        fields = ['id','value']


# 新增SKU数据时候的 获取规格信息 序列化器  （屏幕尺寸、颜色等）
class SPUSpecSerializer(serializers.ModelSerializer):

    # 使用options 获取 规格选项信息
    options  = SpecificationOptionSerializer(many=True)


    class Meta:
        model = SPUSpecification
        fields = '__all__'



# 新增SKU表数据时候的 获取三级分类数据 序列化器
class SKUCategorieSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = ['id','name']


# 保存SKU规格信息的 序列化器
class SKUSpecificationSerializer(serializers.ModelSerializer):

    spec_id= serializers.IntegerField()
    option_id= serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ['spec_id','option_id']


# 新增SKU数据的时候 实现保存SKU数据功能 序列化器
class SKUSerializer(serializers.ModelSerializer):

    # 报错---以下两个为必填字段 所以加上read_only=True
    spu = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    # 报错---必须传入spu_id
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()


    # 为了获取spec_id 和option_id
    specs = SKUSpecificationSerializer(many=True)

    class Meta:
        model = SKU
        fields = '__all__'


    # 重写create 方法  保存SKU数据和SKU规格数据
    def create(self, validated_data):

        # 1.接收specs
        specs = validated_data.get('specs')

        # 2.判断是否有specs
        if specs:
            # 2.1 如果有specs 就删除
            del validated_data['specs']

        # 设置事务开启点
        with transaction.atomic():

            # 设置事务保存点
            save_id = transaction.savepoint()

        try:
            # 3.将删除specs后的数据写入sku表里
            sku = SKU.objects.create(**validated_data)


            # 4.将SKU商品规格信息写入SKU规格表中
            for spec in specs:
                # spec = {"spec_id": 4, "option_id": 8}
                SKUSpecification.objects.create(
                    sku_id = sku.id,
                    spec_id = spec.get('spec_id'),
                    option_id = spec.get('option_id')
                )

            # 因为异步任务会报错没有default_image 所以：
            sku.default_image = "group1/M00/00/02/CtM3BVrRa8iAZdz1AAFZsBqChgk2188464"
            sku.save()
        except:

            # 回滚事务
            transaction.savepoint_rollback(save_id)
            return serializers.ValidationError("数据库错误")

        else:

            # 提交事务
            transaction.savepoint_commit(save_id)

        # 5.调用异步任务方法 生成html详情页面
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku.id)

        # 6.返回结果
        return sku


    # 重写update方法
    def update(self, instance, validated_data):

        # 1.接收specs
        specs = validated_data['specs']
        # 2.判断如果有specs 那就删除
        if specs:
            del validated_data['specs']

        # 设置事务开启点
        with transaction.atomic():

            # 设置事务保存点
            save_id = transaction.savepoint()

            try:
                # 3.然后先更新sku数据
                SKU.objects.filter(id=instance.id).update(**validated_data)

                # # 删除所有SKUSpecification中的数据
                # SKUSpec = SKUSpecification.objects.get(sku_id=instance.id)
                # SKUSpec.delete()
                # SKUSpec.save()

                # 4.再更新sku规格数据
                for spec in specs:
                    SKUSpecification.objects.filter(sku_id=instance.id,
                                                    spec_id=spec.get('spec_id'))\
                                            .update(
                                                    spec_id = spec.get('spec_id'),
                                                    option_id = spec.get('option_id')
                                                    )
            except:

                # 设置事务回滚点
                transaction.savepoint_rollback(save_id)
                return serializers.ValidationError("更新错误")

            else:

                # 设置事务提交点
                transaction.savepoint_commit(save_id)

        # 5.调用异步任务方法 生成html详情页面
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html(instance.id)

        # 5.返回结果
        return instance











