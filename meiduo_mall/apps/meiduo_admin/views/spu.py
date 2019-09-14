
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SPU, Brand, GoodsCategory
from apps.meiduo_admin.serializers.spu import SPUModelSerializer, SPUSerializer, BrandsSerizliser, CategorysSerizliser

from apps.meiduo_admin.utils import CustomPageNumberPagination


# 新增SPU数据---获取二级三级分类信息
class Channel23CategorysView(ListAPIView):

    serializer_class = CategorysSerizliser

    def get_queryset(self):

        pk = self.kwargs['pk']

        return GoodsCategory.objects.filter(parent=pk)




# 新增SPU数据---获取一级分类信息
class ChannelCategorysView(ListAPIView):

    queryset = GoodsCategory.objects.filter(parent=None)

    serializer_class = CategorysSerizliser




# 新增SPU数据---获取品牌信息
class SPUBrandView(ListAPIView):

    queryset = Brand.objects.all()

    serializer_class = BrandsSerizliser



# 获取SPU表所有数据
class SPUGoodsView(ModelViewSet):

    queryset = SPU.objects.all()

    serializer_class = SPUSerializer

    pagination_class = CustomPageNumberPagination



# 获取SPU表名数据
class SPUGoodsListAPIView(ListAPIView):

    queryset = SPU.objects.all()

    serializer_class = SPUModelSerializer