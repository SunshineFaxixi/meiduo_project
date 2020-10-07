from django.shortcuts import render
from django.views import View

from contents.utils import get_categories

# Create your views here.
class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        categories = get_categories()
        context = {
            'categories': categories,
        }
        return render(request, 'list.html', context)