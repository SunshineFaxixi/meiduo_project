from django.shortcuts import render
from django.views import View
from django import http
import logging

from . import models
from meiduo_mall.utils.response_code import RETCODE


logger = logging.getLogger('django')

# Create your views here.
class AreasView(View):
    """省市区三级联动"""
    def get(self, request):
        # 判断当前是查询省份数据还是市区数据
        area_id = request.GET.get('area_id')
        if not area_id:
            # 查询省份数据
            try:
                province_model_list = models.Areas.objects.filter(parent__isnull=True)
                province_list = []
                for province_model in province_model_list:
                    province_dict = {
                        'id': province_model.id,
                        'name': province_model.name
                    }
                    province_list.append(province_dict)
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
            except Exception as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询省份数据错误'})
        else:
            # 查询城市或区县数据
            try:
                parent_model = models.Areas.objects.get(id=area_id)
                # model_list = parent_model.areas_set.all()
                sub_model_list = parent_model.subs.all()
                subs = []
                for sub_model in sub_model_list:
                    sub_dict = {
                        'id': sub_model.id,
                        'name': sub_model.name,
                    }
                    subs.append(sub_dict)
                sub_data = {
                    'id': parent_model.id,
                    'name': parent_model.name,
                    'subs': subs
                }
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
            except Exception as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '查询城市或区县数据错误'})
