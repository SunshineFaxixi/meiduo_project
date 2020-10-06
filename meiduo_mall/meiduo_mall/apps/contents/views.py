from collections import OrderedDict

from django.shortcuts import render
from django.views import View

from goods.models import GoodsChannel
from .models import ContentCategory

# Create your views here.
class IndexView(View):
    def get(self, request):
        # 准备商品分类对应的字典
        categories = OrderedDict()
        # 查询出所有的商品频道: 37个一级类别
        channels = GoodsChannel.objects.order_by('group_id', 'sequence')
        # 遍历所有频道
        for channel in channels:
            # 获取当前频道所在的组
            group_id = channel.group_id
            # 构造基本的数据框架：只有11个组
            if group_id not in categories:
                categories[group_id] = {"channels": [], "sub_cats": []}

            cat1 = channel.category
            categories[group_id]["channels"].append({
                "id": channel.id,
                "name": cat1.name,
                "url": channel.url
            })

            for cat2 in cat1.subs.all():
                cat2.sub_cats = []
                for cat3 in cat2.subs.all():
                    cat2.sub_cats.append(cat3)

                categories[group_id]["sub_cats"].append(cat2)

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