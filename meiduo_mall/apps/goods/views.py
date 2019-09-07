from datetime import datetime

from django import http
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from apps.contents.utils import get_categories
from apps.goods.models import GoodsCategory, SKU, GoodsVisitCount
from apps.goods.utils import get_breadcrumb
from utils.response_code import RETCODE


class ListView(View):

    def get(self,request,category_id,page_num):
        """
        1.判断category_id
        2.获取分类数据
        3.获取面包屑数据
        4.组织排序字段
        5.分页
        6.组织数据
        7.返回相应
        """
        # 1.判断category_id
        try:
            category=GoodsCategory.objects.get(pk=category_id)
        except Exception as e:
            return http.HttpResponseNotFound('分类数据错误')
        # 2.获取分类数据
        categories = get_categories()
        # 3.获取面包屑数据
        breadcrumb=get_breadcrumb(category)
        # 4.组织排序字段
        sort = request.GET.get('sort')
        order_field=''
        if sort == 'price':
            order_field='price'
        elif sort == 'hot':
            order_field='-sales'
        else:
            sort='default'
            order_field='create_time'
        skus = SKU.objects.filter(category=category, is_launched=True).order_by(order_field)
        # 5.分页
        paginator=Paginator(skus,per_page=5)
        try:
            page_num=int(page_num)
            page_skus = paginator.page(page_num)
        except Exception as e:
            return http.HttpResponseNotFound('empty page')
        #总页数
        total_page=paginator.num_pages
        # 6.组织数据
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sort': sort,               # 排序字段
            'category': category,       # 第三级分类
            'page_skus': page_skus,     # 分页后数据
            'total_page': total_page,   # 总页数
            'page_num': page_num,       # 当前页码
        }
        # 7.返回相应
        return render(request, 'list.html',context=context)

class HotView(View):

    def get(self,request,category_id):
        """
         1.根据分类查询数据
         2.将对象列表转换为字典列表
         3.返回相应
        """
        skus=SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')[:2]

        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})

class DetailView(View):

    def get(self,request,sku_id):
        """
        1.根据sku_id,进行查询
        2.获取面包屑
        3.获取分类数据
        """
        # 1.根据sku_id,进行查询
        try:
            sku=SKU.objects.get(pk=sku_id)
        except Exception as e:
            return render(request,'404.html')
        # 2.获取面包屑
        breadcrumb=get_breadcrumb(sku.category)
        # 3.获取分类数据
        categories=get_categories()

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs':goods_specs
        }

        return render(request,'detail.html',context=context)

class VisitView(View):

    def post(self,request,category_id):
        """
        1.组织生成当天的时间 yyyy-mm-dd
        2.保存数据
        3.返回相应
        """

        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseBadRequest('缺少必传参数')

        # 1.获取当天的时间
        now = datetime.now()
        today_str = '%s-%s-%s'%(now.year,now.month,now.day)
        today_date=datetime.strptime(today_str,'%Y-%m-%d')

        # 2.保存数据
        try:
            gvc=GoodsVisitCount.objects.get(date=today_date,category=category)
        except GoodsVisitCount.DoesNotExist:
            gvc=GoodsVisitCount()
        try:
            gvc.category=category
            gvc.count+=1
            gvc.save()
        except Exception as e:
            return http.HttpResponseServerError('服务器异常')

        # 3.返回相应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
