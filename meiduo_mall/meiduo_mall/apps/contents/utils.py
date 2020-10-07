from collections import OrderedDict

from goods.models import GoodsChannel


def get_categories():
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

    return categories
