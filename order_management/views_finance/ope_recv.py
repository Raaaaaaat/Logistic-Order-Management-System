from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from order_management.models import ORDER
from order_management.models import RECEIVEABLES
from order_management.models import SUPPLIER
from order_management.models import CLIENT
import datetime,json
from django.db.models import Q
from django.utils.timezone import localtime
from order_management.models import RECV_INVOICE

def get_recv_list(request):
    if request.method == "POST":
        bo_data             = json.loads(request.body.decode())
        f_order_No          = bo_data["f_order_No"]
        f_client            = bo_data["f_client"]
        f_create_start_time = bo_data["f_create_start_time"]
        f_create_end_time   = bo_data["f_create_end_time"]
        f_clear_start_time  = bo_data["f_clear_start_time"]
        f_clear_end_time    = bo_data["f_clear_end_time"]
        f_if_total          = bo_data["f_if_total"] #这个参数用来过滤是否将已结账的分录也展示出来


        query = Q()
        if f_order_No != "":
            #搜索order表，然后找到编号包含搜索内容的obj，然后整理出其【id】再进行搜索
            t_order_objs = ORDER.objects.filter(No__contains=f_order_No)
            ids = []
            for single in t_order_objs:
                ids.append(single.id)
            query = query & Q(order_id__in=ids)
        if f_client != "":
            t_order_objs = ORDER.objects.filter(client_id=f_client)
            ids = []
            for single in t_order_objs:
                ids.append(single.id)
            query = query & Q(order_id__in=ids)
        if f_create_start_time != "":
            query = query & Q(create_time__gte=datetime.datetime.strptime(f_create_start_time, '%m/%d/%Y'))
        if f_create_end_time != "":
            query = query & Q(create_time__lte=datetime.datetime.strptime(f_create_end_time, '%m/%d/%Y')+datetime.timedelta(days=1))
        if f_clear_start_time != "":
            query = query & Q(clear_time__gte=datetime.datetime.strptime(f_clear_start_time, '%m/%d/%Y'))
        if f_clear_end_time != "":
            query = query & Q(clear_time__lte=datetime.datetime.strptime(f_clear_end_time, '%m/%d/%Y')+datetime.timedelta(days=1))
        if f_if_total == "1":
            query = query #搜索全部
        else:
            query = query & Q(status=0)

        recv_obj = RECEIVEABLES.objects.filter(query).values()
        #除了表内基本信息，还有联合查询step 以及supplier的信息（由id查询name）

        rows = []
        index = 1
        for line in recv_obj:
            order_obj = ORDER.objects.get(id=line["order_id"])
            client_id = order_obj.client_id
            try:
                client_obj = CLIENT.objects.get(id=client_id)
                if client_obj.type == 0:
                    line["client_name"] = client_obj.No + " - " + client_obj.co_name
                else:
                    line["client_name"] = client_obj.No + " - " + client_obj.contact_name
            except:
                line["client_name"] = "客户已删除"
            line["index"] = index
            index += 1
            line["order_No"] = order_obj.No
            line["dep_city"] = order_obj.dep_city
            line["des_city"] = order_obj.des_city


            line["create_time"] =datetime.datetime.strftime(localtime(line["create_time"]), '%Y-%m-%d %H:%M:%S')
            if line["clear_time"] != None:
                line["clear_time"] = datetime.datetime.strftime(localtime(line["clear_time"]), '%Y-%m-%d %H:%M:%S')
            rows.append(line)
        return JsonResponse({"data":rows})

def mark_recv_invoice(request):
    #两个参数分别是数组为payables的id，以及要批量修改的票号
    #应收款的发票专门存在另一个表里
    # 1. 检查是否已经出过这张发票
    # 1.1 检查所选择的应收分录是否有供应商并且唯一
    # 2. 创建发票，插入表中
    # 3. 在应收款里填写发票主码
    # 4. 检查如果一个订单的所有发票都已经填写完成，就变更订单状态
    if request.method == "POST":
        recv_ids = request.POST.get("recv_ids","")
        recv_ids = recv_ids.split(",")
        invoice  = request.POST.get("invoice")

        if RECEIVEABLES.objects.filter(Q(id__in=recv_ids) & ~Q(invoice=None) & ~Q(invoice=0)).count()!=0:
            return JsonResponse({"if_success": 0, "info": "不可重复开票"})
        if invoice != "不出票":
            check_if_exist_invoice = RECV_INVOICE.objects.filter(invoice=invoice).count()
            if check_if_exist_invoice!=0:
                return JsonResponse({"if_success": 0, "info":"此发票已被使用"})

            #
            recv_objs = RECEIVEABLES.objects.filter(id__in=recv_ids)
            recv_objs_clients = []
            for single in recv_objs:
                #这里假设应收款的order_id一定可以查到order_obj
                order_obj = ORDER.objects.get(id=single.order_id)   #这里等待优化，首先确定order_id再检查他们对应的用户是否有重复
                recv_objs_clients.append(order_obj.client_id)
            recv_objs_clients = list(set(recv_objs_clients))
            if len(recv_objs_clients) >1:
                return JsonResponse({"if_success": 0, "info": "一张发票只能对应单一供应商"})
            if len(recv_objs_clients) == 0:
                return JsonResponse({"if_success": 0, "info": "系统错误：请重新尝试"})
            client_id = recv_objs_clients[0]
            invoice_obj = RECV_INVOICE.objects.create(invoice=invoice, client_id=client_id, create_user=request.user.username)
            invoice_id = invoice_obj.id
        else:
            recv_objs = RECEIVEABLES.objects.filter(id__in=recv_ids)
            invoice_id = 0
        try:
            recv_objs.update(invoice=invoice_id)
        except:
            return JsonResponse({"if_success": 0, "info": "添加失败：请重新尝试"})
        #获取这些记录对应的order号
        order_ids = []
        for single in recv_objs:
            order_ids.append(single.order_id)
        order_ids = list(set(order_ids))
        #再对于order_ids进行遍历查看
        for single in order_ids:
            try:
                count_order_no_invoice = RECEIVEABLES.objects.filter(Q(order_id=single) & Q(invoice=None)).count()
                if count_order_no_invoice == 0:
                    order_obj = ORDER.objects.get(id=single)
                    order_obj.status=5
                    order_obj.save()
            except:
                continue
        return JsonResponse({"if_success": 1})

def recv_verify(request):
    #三个参数分别是数组为payables的id，以及要type（0为现金，1为油卡）， 以及总的金额
    #action: 对于未付款的金额进行校对，如果金额大于最大金额就报错，否则对于数额依次进行修改
    if request.method == "POST":
        recv_ids = request.POST.get("recv_ids","")
        recv_ids = recv_ids.split(",")
        received_ammount  = request.POST.get("received_ammount")
        received_ammount = float(received_ammount)
        total_to_be_received = 0
        for single in recv_ids: #统计总的未付款
            recv_obj = RECEIVEABLES.objects.get(id=single)
            total_to_be_received = total_to_be_received + recv_obj.receiveables - recv_obj.received
        if total_to_be_received < received_ammount:
            return JsonResponse({"if_success": 0, "info":"确认失败：收款金额大于应收款"})

        #可以进行付款操作
        for single in recv_ids:
            recv_obj = RECEIVEABLES.objects.get(id=single)
            max_to_be_received = recv_obj.receiveables - recv_obj.received
            if max_to_be_received >= received_ammount:
                #一次付清款，退出循环
                recv_obj.received += received_ammount
                if recv_obj.receiveables == recv_obj.received:
                    recv_obj.clear_time=datetime.datetime.now()
                recv_obj.save()
                break
            else:
                received_ammount -= max_to_be_received
                recv_obj.paid_oil += max_to_be_received
                recv_obj.clear_time = datetime.datetime.now()
                recv_obj.save()
        return JsonResponse({"if_success": 1})

def recv_cancel_verify(request):
    if request.method == "POST":
        recv_ids = request.POST.get("recv_ids", "")
        recv_ids = recv_ids.split(",")
        count_suc = 0
        for single in recv_ids:
            recv_obj = RECEIVEABLES.objects.get(id=single)
            if recv_obj.status==0:
                recv_obj.clear_time=None
                recv_obj.received=0
                recv_obj.save()
                count_suc += 1
        return JsonResponse({"if_success": 1, "suc_num":count_suc})
