from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token



from .views import user
from .views import sku
from .views import image
from .views import statistical
from .views import spu


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

    # 查询用户信息
    url(r'^users/$', user.UserListCreateView.as_view()),


    ##############################商品管理---图片######################################################



    ##############################商品管理---SKU######################################################

    # 新增图片时获取SKU数据的视图集
    url(r'^skus/simple/$', image.SimpleSKUListAPIView.as_view()),
    # 获取三级分类数据
    url(r'^skus/categories/$', sku.SKUCategoriesListView.as_view()),

    ##############################商品管理---SPU######################################################


    # 获取spu数据
    url(r'^goods/simple/$', spu.SPUGoodsListAPIView.as_view()),
]



# 图片管理视图集的url
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'skus/images',image.ImageModelViewSet,basename='skus/images')

urlpatterns += router.urls


# SKU管理视图集的url
router = DefaultRouter()

router.register(r'^skus',sku.SKUModelViewSet,basename='skus')

urlpatterns += router.urls