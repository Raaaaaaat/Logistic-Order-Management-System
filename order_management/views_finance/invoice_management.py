from django.shortcuts import render
from django.http import JsonResponse
from order_management.models import RECV_INVOICE
from order_management.models import CLIENT
from django.db.models import Q
from django.utils.timezone import localtime
import datetime

def invoice_management(request):

    if request.method == "GET":

        return render(request, 'finance/invoice.html')

def get_invoice_list(request):
    if request.method == "GET":
        f_invoice    = request.GET.get("f_invoice")
        f_client     = request.GET.get('f_client')
        f_start_time = request.GET.get('f_start_time')
        f_end_time   = request.GET.get('f_end_time')
        limit        = request.GET.get("limit");
        offset       = request.GET.get("offset");

        query = Q()
        if f_start_time != "":
            query = query & Q(create_time__gte=datetime.datetime.strptime(f_start_time, '%m/%d/%Y'))
        if f_end_time != "":
            query = query & Q(create_time__lte=datetime.datetime.strptime(f_end_time, '%m/%d/%Y')+datetime.timedelta(days=1))
        if f_client != "":
            query = query & Q(client_id=f_client)
        if f_invoice != "":
            query = query & Q(invoice__contains=f_invoice)

        total = RECV_INVOICE.objects.filter(query).count()
        invoice_objs = RECV_INVOICE.objects.filter(query).values()
        rows = []
        index = 1
        for line in invoice_objs:
            try:
                client_obj = CLIENT.objects.get(id=line["client_id"])
                if client_obj.type == 0:
                    line["client_name"] = client_obj.No + " - " + client_obj.co_name
                else:
                    line["client_name"] = client_obj.No + " - " + client_obj.contact_name
            except:
                line["client_name"] = "客户已删除"
            line["create_time"] = datetime.datetime.strftime(localtime(line["create_time"]), '%Y-%m-%d %H:%M:%S')
            line["index"] = index
            index += 1
            rows.append(line)
        return  JsonResponse({'rows':rows})

def edit_invoice(request):
    if request.method == "POST":
        return  JsonResponse({})

def delete_invoice(request):
    if request.method == "POST":
        return  JsonResponse({})