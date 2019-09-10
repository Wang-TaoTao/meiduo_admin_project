
from rest_framework.generics import ListAPIView
from apps.goods.models import SPU
from apps.meiduo_admin.serializers.spu import SPUModelSerializer




# 获取SPU数据
class SPUGoodsListAPIView(ListAPIView):

    queryset = SPU.objects.all()

    serializer_class = SPUModelSerializer