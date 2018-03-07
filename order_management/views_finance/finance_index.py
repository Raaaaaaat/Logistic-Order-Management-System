from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


@login_required
@permission_required('order_management.view_order_finance', login_url='/error?info=没有查看财务中心的权限，请联系管理员')
def finance_index(request):

    if request.method == "GET":
        type = request.GET.get("type","recv")
        return render(request, 'finance/index.html', {'type':type})