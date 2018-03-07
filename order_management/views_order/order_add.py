from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


@login_required
@permission_required('order_management.add_order', login_url='/error?info=没有添加订单的权限，请联系管理员')
def order_add(request):
    if request.method == "GET": #这是通过点击添加按钮进来的地方
        return render(request, 'order/add.html')
