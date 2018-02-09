from django.shortcuts import render, get_object_or_404
from order_management.models import ORDER
from order_management.models import PAYABLES
import datetime

def order_detail(request):
    if request.method == "GET":
        No = request.GET.get('No', '')
        order_obj = get_object_or_404(ORDER, No=No)

        return render(request, 'order/detail.html', {
            'id':          order_obj.id,
            'No':          No,
            'status':      order_obj.status,
            'create_time': datetime.datetime.strftime(order_obj.create_time, '%Y-%m-%d %H:%M:%S'),
            'dep_city':    order_obj.dep_city,
            'des_city':    order_obj.des_city,
            'dep_place':   order_obj.dep_place,
            'des_place':   order_obj.des_place,
            'cargo_quantity': order_obj.cargo_quantity,
            'cargo_name':     order_obj.cargo_name,
            'cargo_weight':   order_obj.cargo_weight,
            'note':           order_obj.note,
        })