from django.http import JsonResponse
from order_management.models import SUPPLIER
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

@login_required
@permission_required('order_management.view_supplier', login_url='/no_perm/')
def supplier_get_table_data(request):
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 10))
    search = request.GET.get('search','')
    total = SUPPLIER.objects.count()#获取总数

    if search=="":
        all_client = SUPPLIER.objects.all().values()[offset:offset+limit]
    else:
        all_client = SUPPLIER.objects.filter((Q(type=0) & Q(co_name__contains=search)) | (Q(type=1) & Q(contact_name__contains=search)) | Q(No__contains=search)).values()[offset:offset+limit]

    rows = []           #这里从数据库取回来的初始数据不是列表，而是ｑｕｅｒｙｓｅｔ，所以这里领建立一个列表ｒｏｗｓ然后重新过一遍数据，转存一下
    for line in all_client:
        rows.append(line)

    data = {
        "total": total,
        "rows" : rows
    }
    return JsonResponse(data)