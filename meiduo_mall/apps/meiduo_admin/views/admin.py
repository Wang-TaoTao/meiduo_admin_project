from django.contrib.auth.models import Group
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from apps.meiduo_admin.serializers.admin import AdminSerializer, GroupSimpleSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination
from apps.users.models import User


# 新增管理员---获取用户组信息
class GroupSimpleView(ListAPIView):

    queryset = Group.objects.all()

    serializer_class = GroupSimpleSerializer


# 获取管理员信息
class AdminModelView(ModelViewSet):

    queryset = User.objects.filter(is_staff=True)

    serializer_class = AdminSerializer

    pagination_class = CustomPageNumberPagination