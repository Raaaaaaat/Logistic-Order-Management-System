from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

@login_required
@permission_required('order_management.add_supplier', login_url='/error?info=操作失败：没有添加供应商的权限')
#这个是增加的页面，  ope_edit_supplier是增加的操作
def supplier_add(request):
    if request.method == "GET": #这是通过点击添加按钮进来的地方
        return render(request, 'supplier/add.html')
