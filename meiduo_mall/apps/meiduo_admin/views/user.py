from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ListAPIView, ListCreateAPIView
from apps.meiduo_admin.serializers.user import UserSerializer, UserAddSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination
from apps.users.models import User







# 查询和新增 用户信息
class UserListCreateView(ListCreateAPIView):

    # 查询结果集
    # queryset = User.objects.all()
    # 指定序列化器对象
    # serializer_class = UserSerializer
    # 指定重写的分页
    pagination_class = CustomPageNumberPagination


    # 搜索功能 ， 重写获取查询集方法 ， 根据不同的参数来查询不同的结果集
    def get_queryset(self):

        # 根据用户传入的keyword查询参数来判断用户想要获取的用户信息
        keyword = self.request.query_params.get('keyword')
        # 如果用户输入了keyword 那么进行模糊查询
        if keyword:
            return User.objects.filter(username__contains=keyword)
        # 如果用户没输入keyword 那么就返回所有用户信息
        return User.objects.all()


    # 新增用户功能 ， 重写获取序列化器类方法 ，根据不同的请求方式 来 指定不同的序列化器
    def get_serializer_class(self):

        # 判断用户的请求方式
        if self.request.method == 'GET':
            # 如果是GET方式 返回查询的序列化器
            return UserSerializer

        # 否则 返回新增用户的序列化器
        return UserAddSerializer