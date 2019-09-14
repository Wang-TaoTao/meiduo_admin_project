




from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


# 新增权限信息----获取权限类别序列化器
class ContentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentType
        # fields = '__all__'
        fields = ['id','name']


# 获取权限信息 序列化器
class PermissionSerializer(serializers.ModelSerializer):


    class Meta:
        model = Permission
        fields = '__all__'