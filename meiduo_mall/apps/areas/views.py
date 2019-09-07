from django import http
from django.core.cache import cache
from django.shortcuts import render
from django.views import View
from apps.areas.models import Area
from utils.response_code import RETCODE
import logging
logger = logging.getLogger('django')

class AreaView(View):

    def get(self,request):
        """
         1.获取参数
         2.根据参数判断是获取省份信息还是市,区县信息
         3.省份信息获取
            3.1 将对象列表转换为字典列表
            3.2 返回数据
         4.市,区县数据获取
            4.1 获取上一级某一个省份(市)信息
            4.2 根据省份(市)信息获取市(区县)信息
            4.3 将市,区县数据对象列表转换为字典列表
            4.4 返回数据
        """
        # 1.获取参数
        area_id = request.GET.get('area_id')
        # 2.根据参数判断是获取省份信息还是市,区县信息
        if area_id is None:

            #先获取数据
            provience_list = cache.get('provience_list')

            if provience_list is None:

                # 3.省份信息获取
                try:
                    areas = Area.objects.filter(parent=None)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})

                #    3.1 将对象列表转换为字典列表
                provience_list=[]
                for item in areas:
                    provience_list.append({
                        'id':item.id,
                        'name':item.name
                    })
                # 设置缓存
                cache.set('provience_list',provience_list,3600)
            #    3.2 返回数据
            return http.JsonResponse({'code':RETCODE.OK,'errmsg':"ok",'provience_list':provience_list})

        else:
            # 4.市,区县数据获取

            sub_data = cache.get('sub_area_%s'%area_id)
            if not sub_data:
                try:
                    #    4.1 获取上一级某一个省份(市)信息
                    parent_model = Area.objects.get(id=area_id)
                    #    4.2 根据省份(市)信息获取市(区县)信息
                    sub_areas = parent_model.subs.all()
                    #    4.3 将市,区县数据对象列表转换为字典列表
                    subs_list = []
                    for area in sub_areas:
                        subs_list.append({
                            'id': area.id,
                            'name': area.name
                        })

                    sub_data = {
                        'id':parent_model.id,
                        'name':parent_model.name,
                        'subs':subs_list
                    }
                    #设置缓存
                    cache.set('sub_area_%s'%area_id,sub_data,3600)
                except Exception as e:
                    logging.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '获取数据错误'})

            #    4.4 返回数据
            return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok','sub_data':sub_data})
