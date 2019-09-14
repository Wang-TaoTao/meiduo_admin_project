from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from apps.meiduo_admin.serializers.channel import GoodsChannelSerializer, ChannelGroupSerializer, CategoriesSerializer


from apps.meiduo_admin.utils import CustomPageNumberPagination

# 获取频道信息
class GoodsChannelModelView(ModelViewSet):

    queryset = GoodsChannel.objects.all()

    serializer_class = GoodsChannelSerializer

    pagination_class = CustomPageNumberPagination


    # 获取频道组信息
    def channel_types(self,request):

        channels = GoodsChannelGroup.objects.all()

        s = ChannelGroupSerializer(instance=channels,many=True)

        return Response(s.data)

    # 获取一级分类信息
    def categories(self,request):

        category = GoodsCategory.objects.filter(parent=None)

        s = CategoriesSerializer(instance=category,many=True)

        return Response(s.data)
