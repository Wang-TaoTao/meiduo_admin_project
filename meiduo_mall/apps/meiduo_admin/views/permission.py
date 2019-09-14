




from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializers.permission import PermissionSerializer, ContentTypeSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination


# 新增权限信息---获取权限类别信息
class ContentTypeAPIView(APIView):

    def get(self,request):

        query_set = ContentType.objects.all()

        s =  ContentTypeSerializer(instance=query_set,many=True)

        return Response(s.data)



# 获取权限信息----增删改查功能
class PermissionView(ModelViewSet):


    queryset = Permission.objects.all()

    serializer_class = PermissionSerializer

    pagination_class = CustomPageNumberPagination