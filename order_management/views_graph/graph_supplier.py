from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


def graph_supplier(request):
#这个页面是供应商数据透视图的默认界面
    if request.method == "GET":
        return render(request, 'graph/supplier_graph.html')