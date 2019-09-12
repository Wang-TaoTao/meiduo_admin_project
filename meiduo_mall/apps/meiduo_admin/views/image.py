from fdfs_client.client import Fdfs_client
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SKUImage, SKU
from apps.meiduo_admin.serializers.image import SKUImageSerializer, SimpleSKUSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination



# 获取图片的视图集 ---新增、更新、删除功能
class ImageModelViewSet(ModelViewSet):

    queryset = SKUImage.objects.all()

    serializer_class = SKUImageSerializer

    pagination_class = CustomPageNumberPagination

    # 重写create 方法
    def create(self, request, *args, **kwargs):

        # 1. 通过Fdfs实现图片的保存 创建FastDFS连接对象
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 2. 获取图片资源 InMemoryUploadedFile
        data = request.FILES.get('image')
        # 2.2 将读取的二进制图片，上传到fastDFS服务器中
        result = client.upload_by_buffer(data.read())
        # 3.获取Remote file_id
        # 3.1 判断上传图片的状态
        if result.get('Status') != 'Upload successed.':
            return Response(status=status.HTTP_403_FORBIDDEN)
        # 如果成功，则可以获取file_id
        file_id = result.get('Remote file_id')
        # 4.保存到数据库中
        sku_image = SKUImage.objects.create(
            sku_id = request.data.get('sku'),
            image = file_id
        )
        # 5.响应结果
        return Response({
            'id':sku_image.id,
            'sku':sku_image.sku.id,
            'image':sku_image.image.url,
        },status=status.HTTP_201_CREATED)


# 新增图片时候的 获取SKU数据 视图集
class SimpleSKUListAPIView(ListAPIView):

    queryset = SKU.objects.all()

    serializer_class = SimpleSKUSerializer







# from fdfs_client.client import Fdfs_client
#
# # 1.创建客户端找到Tracker Server
# client = Fdfs_client('utils/fastdfs/client.conf')
# # 2.上传图片
# client.upload_by_filename('/home/python/Desktop/en.jpg')
# # 3.返回file_id