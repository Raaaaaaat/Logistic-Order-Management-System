from django.shortcuts import render
from django.http import JsonResponse
from order_management.models import RECV_INVOICE
from order_management.models import CLIENT
from order_management.models import ORDER
from order_management.models import RECEIVEABLES
from django.db.models import Q
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from order_management.models import OPERATE_LOG

@login_required
@permission_required('order_management.recv_invoice', login_url='/error?info=没有访问票务管理的权限，请联系管理员')
def invoice_management(request):

    if request.method == "GET":
        return render(request, 'finance/invoice.html')

@login_required
def get_invoice_list(request):
    if request.method == "GET":
        if not request.user.has_perm("order_management.recv_invoice"):
            return JsonResponse({'rows': [],'total':0})
        f_invoice    = request.GET.get("f_invoice")
        f_client     = request.GET.get('f_client')
        f_start_time = request.GET.get('f_start_time')
        f_end_time   = request.GET.get('f_end_time')
        f_status     = request.GET.get('f_status')
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
        invoice_objs = RECV_INVOICE.objects.filter(query).order_by('-id').values()[offset:offset+limit]
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
            line["create_time"] = datetime.datetime.strftime(line["create_time"], '%Y-%m-%d %H:%M:%S')
            line["index"] = index
            index += 1
            #统计总已收款以及应收款
            recv_objs = RECEIVEABLES.objects.filter(invoice=line["id"])
            tot_receiveables = 0
            tot_received  = 0
            for single in recv_objs:
                tot_receiveables += single.receiveables
                tot_received+= single.received
            line["tot_receiveables"]=round(tot_receiveables,2)
            line["tot_received"] = round(tot_received,2)
            line["tot_torecv"] = round(tot_receiveables-tot_received,2)
            if f_status == "1": #已结清
                if line["tot_torecv"]==0:
                    rows.append(line)
            elif f_status == "2": #未结清
                if line["tot_torecv"]!=0:
                    rows.append(line)
            else:
                rows.append(line)
        return  JsonResponse({'rows':rows, 'total':total})

@login_required
def edit_invoice(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.change_recv_invoice"):
            return JsonResponse({"if_success":0, "info":"没有进行此操作的权限，请联系管理员"})
        invoice_id = request.POST.get("invoice_id")
        invoice    = request.POST.get("invoice")
        remark     = request.POST.get("remark")
        try:
            invoice_obj = RECV_INVOICE.objects.get(id=invoice_id)
            detail = "修改应收账款发票: 开票时间： " + datetime.datetime.strftime(invoice_obj.create_time, '%Y-%m-%d %H:%M:%S') + " 修改前票号：" + str(invoice_obj.invoice) + " 修改后票号： " + str(invoice) + " 修改前备注：" + str(invoice_obj.remark) + " 修改后备注： " + str(remark)
            OPERATE_LOG.objects.create(user=request.user.username, field="票务中心", detail=detail)
            invoice_obj.invoice = invoice
            invoice_obj.remark = remark
            invoice_obj.save()
            if_success = 1
            info = "修改成功"
        except:
            if_success = 0
            info = "修改失败"
        return  JsonResponse({"if_success":if_success, "info":info})

@login_required
def delete_invoice(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.delete_recv_invoice"):
            return JsonResponse({"if_success":0, "info":"没有进行此操作的权限，请联系管理员"})
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
        #检查发票对应的应收账款，只要有一条有已收，就不允许删除发票
        for single in recv_objs:
            if single.received != 0:
                return JsonResponse({"if_success": 0, "info": "有已核销的发票不允许删除，请先反核销"})
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
        detail = "删除应收账款发票: 开票时间： " + datetime.datetime.strftime(invoice_obj.create_time, '%Y-%m-%d %H:%M:%S') + "删除前票号：" + str(invoice_obj.invoice) + " 删除前备注：" + str(invoice_obj.remark)
        OPERATE_LOG.objects.create(user=request.user.username, field="票务中心", detail=detail)
        invoice_obj.delete()
        return  JsonResponse({"if_success":1})

@login_required
def get_invoice_recv_bill(request):
    if request.method == "POST":
        invoice_id = request.POST.get('invoice_id')
        recv_objs = RECEIVEABLES.objects.filter(invoice=invoice_id).order_by('order_id').values()
        for line in recv_objs:
            order_obj = ORDER.objects.get(id=line["order_id"])
            line["dep_city"] = order_obj.dep_city
            line["des_city"] = order_obj.des_city
            line["order_No"] = order_obj.No
            line["pick_up_time"]  = datetime.datetime.strftime(order_obj.pick_up_time, '%Y-%m-%d')
            line["delivery_time"] = datetime.datetime.strftime(order_obj.delivery_time, '%Y-%m-%d')
        data = []
        for line in recv_objs:
            data.append(line)
        return JsonResponse({"data": data})