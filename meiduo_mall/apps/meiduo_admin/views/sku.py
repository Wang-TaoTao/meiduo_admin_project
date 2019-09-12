from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import GoodsCategory, SKU,  SPUSpecification
from apps.meiduo_admin.serializers.sku import  SKUSerializer, SKUCategorieSerializer, \
    SPUSpecSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination





# 新增SKU数据时候的 获取SPU商品规格信息
class SPUSpecView(APIView):

    def get(self,request,pk):

        # 1.根据传来的pk获取规格表中的规格信息
        try:
            specs = SPUSpecification.objects.filter(spu_id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 2.根据规格信息 获取 规格选项信息
        s = SPUSpecSerializer(instance=specs,many=True)

        # 3.返回结果
        return Response(s.data)





# 新增SKU数据时候的 获取三级分类数据
class SKUCategoriesListView(ListAPIView):

    queryset = GoodsCategory.objects.filter(parent_id__gt=37)

    serializer_class = SKUCategorieSerializer




# SKU 的视图集 实现增删改查功能
class SKUModelViewSet(ModelViewSet):

    # queryset = SKU.objects.all()

    serializer_class = SKUSerializer

    pagination_class = CustomPageNumberPagination

    # 模糊搜索功能
    def get_queryset(self):

        keyword = self.request.query_params.get('keyword')

        if keyword:
            return SKU.objects.filter(name__contains=keyword)

        return SKU.objects.all()