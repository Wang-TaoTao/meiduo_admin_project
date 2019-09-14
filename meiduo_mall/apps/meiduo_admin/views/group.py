


from django.contrib.auth.models import Group, Permission
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializers.group import GroupSerializer, GroupSimpleSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination



# 新增用户组 ---获取权限类别信息
class GroupSimpleListView(ListAPIView):

    queryset = Permission.objects.all()

    serializer_class = GroupSimpleSerializer



# 获取用户组信息 ---增删改查功能
class GroupModelView(ModelViewSet):

    queryset = Group.objects.all()

    serializer_class = GroupSerializer

    pagination_class = CustomPageNumberPagination