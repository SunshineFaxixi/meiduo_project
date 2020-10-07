from collections import OrderedDict

from django.shortcuts import render
from django.views import View

from goods.models import GoodsChannel
from .models import ContentCategory
from .utils import get_categories


# Create your views here.
class IndexView(View):
    def get(self, request):
        categories = get_categories()
        # 查询首页广告数据
        contents = {}
        # 查询所有的广告类别
        content_categories = ContentCategory.objects.all()
        # 使用广告类别查询出该类别对应的所有的广告内容
        for content_category in content_categories:
            contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')

        # 构造上下文
        context = {
            'categories': categories,
            'contents': contents
        }

        return render(request, 'index.html', context)