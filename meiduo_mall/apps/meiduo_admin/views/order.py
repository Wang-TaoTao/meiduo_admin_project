
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.meiduo_admin.serializers.order import OrderSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination
from apps.orders.models import OrderInfo


# 获取订单数据、订单详情信息 视图集
class OrderModelViewSet(ModelViewSet):

    queryset = OrderInfo.objects.all()

    serializer_class = OrderSerializer

    pagination_class = CustomPageNumberPagination

    # 重写destroy方法 防止恶意删除
    def destroy(self, request, *args, **kwargs):

        return Response({"msg":"禁止恶意删除！"})


    # 修改订单状态
    @action(methods=['put'],detail=True)
    def status(self,request,pk):

        # 1.修改订单状态
        try:
            OrderInfo.objects.filter(order_id=pk)\
                .update(status=request.data.get('status'))
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # 2.返回响应
        return Response({
            'order_id':pk,
            'status':request.data.get('status')
        })