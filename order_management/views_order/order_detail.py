from django.shortcuts import render, get_object_or_404
from order_management.models import ORDER
from order_management.models import CLIENT
from order_management.models import PAYABLES
from django.utils.timezone import localtime
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


@login_required
@permission_required('order_management.view_order', login_url='/error?info=没有查看订单的权限，请联系管理员')
def order_detail(request):
    if request.method == "GET":
        No = request.GET.get('No', '')
        order_obj = get_object_or_404(ORDER, No=No)

        try:
            client_obj = CLIENT.objects.get(id=order_obj.client_id)
            if client_obj.type==0:
                client_name = client_obj.co_name
                client_tel = client_obj.co_tel
            else:
                client_name = client_obj.contact_name
                client_tel = client_obj.contact_tel
        except:
            client_name=""
            client_tel=""


        if order_obj.remark==None:
            remark=""
        else:
            remark = order_obj.remark.replace("\r\n", "-rrr-") #这个-r-代表换行，前段可以对于这个组合进行转义
        return render(request, 'order/detail.html', {
            'id':          order_obj.id,
            'No':          No,
            'status':      order_obj.status,
            'create_time': datetime.datetime.strftime(localtime(order_obj.create_time), '%Y-%m-%d %H:%M:%S'),
            'dep_city':    order_obj.dep_city,
            'des_city':    order_obj.des_city,
            'dep_place':   order_obj.dep_place,
            'des_place':   order_obj.des_place,
            'cargo_quantity': order_obj.cargo_quantity,
            'cargo_name':     order_obj.cargo_name,
            'cargo_weight':   order_obj.cargo_weight,
            'cargo_size':     order_obj.cargo_size,
            'remark':         remark,
            'rec_name':       order_obj.rec_name,
            'rec_tel':        order_obj.rec_tel,
            'client_name':    client_name,
            'client_tel':     client_tel,
        })