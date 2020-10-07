from django.shortcuts import render
from django.views import View


# Create your views here.
class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        return render(request, 'list.html')