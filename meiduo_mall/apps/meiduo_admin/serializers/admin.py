from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.response import Response

from apps.users.models import User


# 新增管理员---获取用户组信息 序列化器
class GroupSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


# 获取管理员信息 序列化器
class AdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

        # 序列化的时候不输出
        extra_kwargs = {
            'password':{'write_only':True}

        }

    # 为了加密密码 和 将is_staff改为True 所以重写create方法
    def create(self, validated_data):

        user = super().create(validated_data)

        # 加密密码
        user.set_password(validated_data.get('password'))
        # 将is_staff改为True
        user.is_staff = True
        user.save()

        # 响应结果
        return user


    # 为了加密密码 重写update方法
    def update(self, instance, validated_data):

        user = super().update(instance,validated_data)

        if validated_data['password']:

            user.set_password(validated_data.get('password'))

            user.save()

        return user
