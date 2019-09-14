from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SpecificationOption, SPUSpecification
from apps.meiduo_admin.serializers.option import OptionSerializer, OptionSimpleSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination


# 新增规格选项信息---获取规格信息
class OptionSimpleView(ListAPIView):

    queryset = SPUSpecification.objects.all()

    serializer_class = OptionSimpleSerializer


# 获取规格选项信息---增删改查功能
class OptionModelView(ModelViewSet):

    queryset = SpecificationOption.objects.all()

    serializer_class = OptionSerializer

    pagination_class = CustomPageNumberPagination

