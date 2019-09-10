from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import GoodsCategory, SKU
from apps.meiduo_admin.serializers.sku import  SKUSerializer, SKUCategorieSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination





# 获取三级分类数据的视图
class SKUCategoriesListView(ListAPIView):

    queryset = GoodsCategory.objects.filter(parent_id__gt=37)

    serializer_class = SKUCategorieSerializer




# 获取SKU信息的视图集
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