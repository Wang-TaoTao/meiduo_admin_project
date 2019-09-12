from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token



from .views import user
from .views import sku
from .views import image
from .views import statistical
from .views import spu
from .views import order

urlpatterns = [

    # 后台管理登录
    url(r'^authorizations/$', obtain_jwt_token),

    # 统计用户总数
    url(r'^statistical/total_count/$', statistical.UserAllCountAPIView.as_view()),

    # 获取日增用户
    url(r'^statistical/day_increment/$', statistical.UserDailyCountAPIView.as_view()),

    # 获取日活跃用户
    url(r'^statistical/day_active/$', statistical.UserDailyActiveCountAPIView.as_view()),

    # 获取日下单用户
    url(r'^statistical/day_orders/$', statistical.UserDailyOrderCountAPIView.as_view()),

    # 获取月新增用户
    url(r'^statistical/month_increment/$', statistical.UserMonthCountAPIView.as_view()),

    # 获取日分类访问量
    url(r'^statistical/goods_day_views/$', statistical.UserCategoryCountAPIView.as_view()),


    ##############################用户######################################################

    # 用户信息的 查询和新增
    url(r'^users/$', user.UserListCreateView.as_view()),


    ##############################商品管理---图片######################################################

    # 新增图片时候的 获取SKU id数据
    url(r'^skus/simple/$', image.SimpleSKUListAPIView.as_view()),

    ##############################商品管理---SKU######################################################



    # 新增SKU数据时候的 获取三级分类数据
    url(r'^skus/categories/$', sku.SKUCategoriesListView.as_view()),

    # 新增SKU数据时候的 获取SPU商品规格信息
    url(r'^goods/(?P<pk>\d+)/specs/$', sku.SPUSpecView.as_view()),



    ##############################商品管理---SPU######################################################


    # 获取SPU表数据
    url(r'^goods/simple/$', spu.SPUGoodsListAPIView.as_view()),




]




from rest_framework.routers import DefaultRouter

router = DefaultRouter()


# 图片管理视图集的url
router.register(r'skus/images',image.ImageModelViewSet,basename='skus/images')
# SKU管理视图集的url
router.register(r'^skus',sku.SKUModelViewSet,basename='skus'),
# 订单管理视图集的url
router.register(r'^orders',order.OrderModelViewSet,basename='orders')

urlpatterns += router.urls





