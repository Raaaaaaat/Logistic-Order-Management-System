from django.shortcuts import render
from django.http import JsonResponse
from order_management.models import RECV_INVOICE
from order_management.models import CLIENT
from order_management.models import ORDER
from order_management.models import RECEIVEABLES
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
        limit        = int(request.GET.get("limit"))
        offset       = int(request.GET.get("offset"))

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
        invoice_objs = RECV_INVOICE.objects.filter(query).values()[offset:offset+limit]
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
        return  JsonResponse({'rows':rows, 'total':total})

def edit_invoice(request):
    if request.method == "POST":
        invoice_id = request.POST.get("invoice_id")
        remark     = request.POST.get("remark")
        try:
            invoice_obj = RECV_INVOICE.objects.get(id=invoice_id)
            invoice_obj.remark = remark
            invoice_obj.save()
            if_success = 1
            info = ""
        except:
            if_success = 0
            info = ""
        return  JsonResponse({"if_success":if_success, "info":info})

def delete_invoice(request):
    if request.method == "POST":
        invoice_id = request.POST.get("invoice_id")
        #查看invoidobj是否存在
        # 筛选出来invoice对应的所有的receiveables
        #筛选出来receiveables对应的所有的order_id
        #逐条检查order_id的状态，如果需要就变更状态，最后删除invoice_obj
        try:
            invoice_obj = RECV_INVOICE.objects.get(id=invoice_id)
        except:
            return JsonResponse({"if_success":0, "info":"发票不存在"})

        recv_objs = RECEIVEABLES.objects.filter(invoice=invoice_id)
        order_ids = []
        for single in recv_objs:
            order_ids.append(single.order_id)
            single.invoice = None
            single.save()
        order_ids = list(set(order_ids))
        for single in order_ids:
            try:
                order_obj = ORDER.objects.get(id=single)
                if order_obj.status==5:
                    order_obj.status=4
                    order_obj.save()
                    #待办，此处应增加对于完成订单的控制
            except:
                continue
        invoice_obj.delete()
        return  JsonResponse({"if_success":1})