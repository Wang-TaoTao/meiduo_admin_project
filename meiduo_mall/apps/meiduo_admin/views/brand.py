from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from apps.goods.models import Brand
from apps.meiduo_admin.serializers.brand import BrandSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination

# 获取品牌信息---增删改查功能
class BrandModelView(ModelViewSet):

    queryset = Brand.objects.all()

    serializer_class = BrandSerializer

    pagination_class = CustomPageNumberPagination


    # 重写新增品牌信息方法
    def create(self, request, *args, **kwargs):


        from fdfs_client.client import Fdfs_client
        # 创建fdfs连接对象
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 获取图片资源
        data = request.FILES.get('logo')
        # 上传图片至服务器
        result = client.upload_by_buffer(data.read())
        # 判断状态
        if result['Status'] != 'Upload successed.':
            return Response({'msg':'图片上传失败'})
        # 获取图片路径
        file_id = result['Remote file_id']

        # 保存图片至brand表
        try:
            brands = Brand.objects.create(
                name = request.data.get('name'),
                logo = file_id,
                first_letter = request.data.get('first_letter')
            )
        except:
            return Response({'msg':'数据保存失败'})
        # 响应结果
        return Response({
            'id':brands.id,
            'name':brands.name,
            'logo':file_id,
            'first_letter':brands.first_letter
        })

    # 重写更新品牌信息方法
    def update(self, request, *args, **kwargs):

        from fdfs_client.client import Fdfs_client
        # 创建fdfs对象
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 获取图片资源
        data = request.FILES.get('logo')
        # 将图片上传至服务器
        result = client.upload_by_buffer(data.read())
        # 判断状态
        if result['Status'] != 'Upload successed.':
            return Response({'msg':'图片上传失败'})
        # 获取图片路径
        file_id = result['Remote file_id']

        # 更新品牌信息
        try:
            Brand.objects.filter(id=self.kwargs['pk'])\
                .update(name = request.data.get('name'),
                        logo = file_id,
                        first_letter = request.data.get('first_letter'),
                        )
        except:
            return Response({'msg':'数据更新失败'})

        # 响应结果
        return Response({
            'id':self.kwargs['pk'],
            'name':request.data.get('name'),
            'logo':file_id,
            'first_letter':request.data.get('first_letter')
        })
