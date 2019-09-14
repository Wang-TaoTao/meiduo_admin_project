from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SPUSpecification
from apps.meiduo_admin.serializers.spec import SPUSpec2Serializer
from apps.meiduo_admin.utils import CustomPageNumberPagination


# 获取规格信息----增删改查功能
class SPUSpecModelView(ModelViewSet):

    queryset = SPUSpecification.objects.all()

    serializer_class = SPUSpec2Serializer

    pagination_class = CustomPageNumberPagination