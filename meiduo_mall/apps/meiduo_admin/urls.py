from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token



from .views import user
from .views import sku
from .views import image
from .views import statistical
from .views import spu
from .views import order
from .views import spec
from .views import option
from .views import brand
from .views import channel
from .views import permission
from .views import group
from .views import admin


urlpatterns = [

    # 后台管理登录
    url(r'^authorizations/$', obtain_jwt_token),

    ############################## 数据统计 ######################################################

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


    ############################## 用户 ######################################################

    # 用户信息的 查询和新增
    url(r'^users/$', user.UserListCreateView.as_view()),


    ############################## 商品管理---图片######################################################

    # 新增图片时候的 获取SKU id数据
    url(r'^skus/simple/$', image.SimpleSKUListAPIView.as_view()),

    ############################## 商品管理---SKU ######################################################



    # 新增SKU数据时候的 获取三级分类数据
    url(r'^skus/categories/$', sku.SKUCategoriesListView.as_view()),

    # 新增SKU数据时候的 获取SPU商品规格信息
    url(r'^goods/(?P<pk>\d+)/specs/$', sku.SPUSpecView.as_view()),



    ############################## 商品管理---SPU ######################################################


    # 获取SPU表名数据
    url(r'^goods/simple/$', spu.SPUGoodsListAPIView.as_view()),

    # 新增SKU数据---获取品牌信息
    url(r'^goods/brands/simple/$', spu.SPUBrandView.as_view()),

    # 新增SPU数据---获取一级分类信息
    url(r'^goods/channel/categories/$', spu.ChannelCategorysView.as_view()),

    # 新增SPU数据---获取二级三级分类信息
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', spu.Channel23CategorysView.as_view()),

    ############################## 规格选项管理 ######################################################

    # 新增规格选项数据---获取规格信息
    url(r'^goods/specs/simple/$', option.OptionSimpleView.as_view()),


    ############################## 频道管理 ######################################################

    # 新增频道数据----获取频道组信息
    url(r'^goods/channel_types/$', channel.GoodsChannelModelView.as_view({'get':'channel_types'})),

    # 新增频道数据----获取一级分类信息
    url(r'^goods/categories/$', channel.GoodsChannelModelView.as_view({'get':'categories'})),



    ############################## 权限管理 ######################################################

    # 新增权限信息----获取权限类别信息
    url(r'^permission/content_types/$', permission.ContentTypeAPIView.as_view()),


    ############################## 用户组管理 ######################################################


    # 新增用户组----获取权限类别信息
    url(r'^permission/simple/$', group.GroupSimpleListView.as_view()),




############################## 管理员管理 ######################################################

    # 新增管理员---获取用户组信息
    url(r'^permission/groups/simple/$', admin.GroupSimpleView.as_view()),

]




from rest_framework.routers import DefaultRouter

router = DefaultRouter()


# 图片管理视图集的url
router.register(r'skus/images',image.ImageModelViewSet,basename='skus/images')
# SKU管理视图集的url
router.register(r'^skus',sku.SKUModelViewSet,basename='skus'),
# 订单管理视图集的url
router.register(r'^orders',order.OrderModelViewSet,basename='orders'),


# 频道管理的url
router.register(r'^goods/channels',channel.GoodsChannelModelView,basename='channels')
# 品牌管理的url
router.register(r'^goods/brands',brand.BrandModelView,basename='brands')
# 规格选项管理的url
router.register(r'^goods/options',option.OptionModelView,basename='options')
# 规格管理的url
router.register(r'^goods/specs', spec.SPUSpecModelView,basename='specs')
# SPU管理的url
router.register(r'^goods',spu.SPUGoodsView,basename='goods')

# 管理员管理的url
router.register(r'^permission/admins',admin.AdminModelView,basename='admins')
# 权限管理的url
router.register(r'^permission/perms',permission.PermissionView,basename='perms')

# 用户组管理的url
router.register(r'^permission/groups', group.GroupModelView,basename='groups')

urlpatterns += router.urls





