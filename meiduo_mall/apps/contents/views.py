from collections import OrderedDict
from django.shortcuts import render
from django.views import View
from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories

class IndexView(View):
    """首页广告"""

    def get(self, request):
        """提供首页广告界面"""
        # 查询商品频道和分类
        categories=get_categories()
        #查询广告信息
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents':contents
        }
        return render(request, 'index.html',context=context)

