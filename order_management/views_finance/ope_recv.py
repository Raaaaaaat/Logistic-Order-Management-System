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
from order_management.models import OPERATE_LOG
from django.db.models import Sum

from django.contrib.auth.decorators import login_required


@login_required
def get_recv_list(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.view_order_finance"):
            return JsonResponse({"data":[]})
        bo_data             = json.loads(request.body.decode())
        f_order_No          = bo_data["f_order_No"]
        f_client            = bo_data["f_client"]
        f_pick_start_time   = bo_data["f_pick_start_time"]
        f_pick_end_time     = bo_data["f_pick_end_time"]
        f_clear_start_time  = bo_data["f_clear_start_time"]
        f_clear_end_time    = bo_data["f_clear_end_time"]
        f_if_total          = bo_data["f_if_total"] #这个参数用来过滤是否将已结账的分录也展示出来
        f_invoice           = bo_data["f_invoice"]
        f_status            = bo_data["f_status"]
        f_offset            = bo_data["offset"]
        f_limit             = bo_data["limit"]
        group_order_id      = bo_data["group_order"]
        group_client_id     = bo_data["group_client"]

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
        #if f_create_start_time != "":
        #    query = query & Q(create_time__gte=datetime.datetime.strptime(f_create_start_time, '%m/%d/%Y'))
        #if f_create_end_time != "":
        #    query = query & Q(create_time__lte=datetime.datetime.strptime(f_create_end_time, '%m/%d/%Y')+datetime.timedelta(days=1))

        if f_pick_end_time != "" or f_pick_start_time!="":
            sub_q = Q()
            if f_pick_start_time!="":
                sub_q = Q(pick_up_time__gte=datetime.datetime.strptime(f_pick_start_time, '%m/%d/%Y'))
            if f_pick_end_time!="":
                sub_q = sub_q&Q(pick_up_time__lte=datetime.datetime.strptime(f_pick_end_time, '%m/%d/%Y')+datetime.timedelta(days=1))
            order_ids = ORDER.objects.filter(sub_q).values("id")
            query = query & Q(order_id__in=order_ids)

        if f_clear_start_time != "":
            query = query & Q(clear_time__gte=datetime.datetime.strptime(f_clear_start_time, '%m/%d/%Y'))
        if f_clear_end_time != "":
            query = query & Q(clear_time__lte=datetime.datetime.strptime(f_clear_end_time, '%m/%d/%Y')+datetime.timedelta(days=1))
        if f_invoice != "":
            invoice_objs = RECV_INVOICE.objects.filter(invoice__contains=f_invoice)
            invoice_ids = []
            for single in invoice_objs:
                invoice_ids.append(single.id)
            query = query & Q(invoice__in=invoice_ids)
        if f_if_total == 1:
            query = query #搜索全部
        else:
            query = query & Q(status=0)
        if f_status != "0":
            if f_status == "1":
                query = query & Q(clear_time__isnull=False)
            else:
                query = query & Q(clear_time__isnull=True)
        else:
            query = query

        #修改于1/21/2019


        if group_order_id or group_client_id:
            if group_order_id:
                if group_client_id:
                    #11
                    recv_obj = RECEIVEABLES.objects.filter(query).values('order_id','client_id').annotate(receiveables=Sum('receiveables'), received=Sum('received'))[f_offset:f_offset+f_limit]
                    recv_count = RECEIVEABLES.objects.filter(query).values('order_id','client_id').annotate(receiveables=Sum('receiveables'), received=Sum('received')).count()
                else:
                    # 10
                    recv_obj = RECEIVEABLES.objects.filter(query).values('order_id').annotate(
                        receiveables=Sum('receiveables'), received=Sum('received'))[f_offset:f_offset + f_limit]
                    recv_count = RECEIVEABLES.objects.filter(query).values('order_id').annotate(
                        receiveables=Sum('receiveables'), received=Sum('received')).count()
            else:
                if group_client_id:
                    # 01
                    recv_obj = RECEIVEABLES.objects.filter(query).values('client_id').annotate(
                        receiveables=Sum('receiveables'), received=Sum('received'))[f_offset:f_offset + f_limit]
                    recv_count = RECEIVEABLES.objects.filter(query).values('client_id').annotate(
                        receiveables=Sum('receiveables'), received=Sum('received')).count()
        else:
            recv_obj = RECEIVEABLES.objects.filter(query).order_by('-id').values()[f_offset:f_offset + f_limit]
            recv_count = RECEIVEABLES.objects.filter(query).count()
            # 除了表内基本信息，还有联合查询step 以及supplier的信息（由id查询name）

        rows = []
        index = int(f_offset)+1
        for line in recv_obj:
            if 'order_id' in line:
                order_obj = ORDER.objects.get(id=line["order_id"])
                line["client_id"] = order_obj.client_id
                line["index"] = index
                index += 1
                line["order_No"] = order_obj.No
                line["order_create_time"] = datetime.datetime.strftime(localtime(order_obj.create_time), '%Y-%m-%d')
                line["order_pick_time"] = datetime.datetime.strftime(localtime(order_obj.pick_up_time), '%Y-%m-%d')
                line["dep_city"] = order_obj.dep_city
                line["des_city"] = order_obj.des_city
            else:
                line["order_No"]=""
            if 'client_id' in line:
                try:
                    client_obj = CLIENT.objects.get(id=line["client_id"])
                    if client_obj.type == 0:
                        line["client_name"] = client_obj.co_name
                    else:
                        line["client_name"] = client_obj.contact_name
                except:
                    line["client_name"] = "客户已删除"
            else:
                line["client_name"]=""
            if 'create_time' in line:
                line["create_time"] =datetime.datetime.strftime(localtime(line["create_time"]), '%Y-%m-%d')
                if line["clear_time"] != None:
                    line["clear_time"] = datetime.datetime.strftime(localtime(line["clear_time"]), '%Y-%m-%d %H:%M:%S')
                invoice_id = line["invoice"]
                if invoice_id!=None:
                    if invoice_id==0:
                        line["invoice"] = "不出票"
                    else:
                        try:
                            invoice_obj = RECV_INVOICE.objects.get(id=invoice_id)
                            line["invoice"]=invoice_obj.invoice
                        except:
                            line["invoice"]="已删除"
            else:
                line["description"] = ""

            rows.append(line)
        return JsonResponse({"total":recv_count,"rows":rows})

@login_required
def mark_recv_invoice(request):
    #两个参数分别是数组为payables的id，以及要批量修改的票号
    #应收款的发票专门存在另一个表里
    # 1. 检查是否已经出过这张发票
    # 1.1 检查所选择的应收分录是否有客户并且唯一
    # 2. 创建发票，插入表中
    # 3. 在应收款里填写发票主码
    # 4. 检查如果一个订单的所有发票都已经填写完成，就变更订单状态
    if request.method == "POST":
        if not request.user.has_perm("order_management.add_recv_invoice"):
            return JsonResponse({"if_success":0, "info":"没有进行此操作的权限，请联系管理员"})
        recv_ids = request.POST.get("recv_ids","")
        recv_ids = recv_ids.split(",")
        remark   = request.POST.get("remark")
        #invoice = None 代表没开票
        if RECEIVEABLES.objects.filter(Q(id__in=recv_ids) & ~Q(invoice=None)).count()!=0: #查看是否已经有分录标记开票信息
            return JsonResponse({"if_success": 0, "info": "不可重复开票"})

            #
        recv_objs = RECEIVEABLES.objects.filter(id__in=recv_ids)
        recv_objs_clients = []
        _list = []
        for single in recv_objs:
            _list.append(single.receiveables) #用于日志记录的详细信息
            #这里假设应收款的order_id一定可以查到order_obj
            order_obj = ORDER.objects.get(id=single.order_id)   #这里等待优化，首先确定order_id再检查他们对应的用户是否有重复
            recv_objs_clients.append(order_obj.client_id)
            if order_obj.status!=4:
                return JsonResponse({"if_success": 0, "info": "只有已签收状态的订单才可开票"})

        recv_objs_clients = list(set(recv_objs_clients))
        if len(recv_objs_clients) >1:
            return JsonResponse({"if_success": 0, "info": "一张发票只能对应单一供应商"})
        if len(recv_objs_clients) == 0:
            return JsonResponse({"if_success": 0, "info": "系统错误：请重新尝试"})
        client_id = recv_objs_clients[0]
        invoice_obj = RECV_INVOICE.objects.create(invoice="待开票", client_id=client_id, create_user=request.user.username, remark=remark)
        invoice_id = invoice_obj.id
        detail = "开 " + str(recv_objs.count()) + " 条应收款对应的发票: 备注: " + remark + " 应付款数目" + str(_list)
        OPERATE_LOG.objects.create(user=request.user.username, field="应收账款", detail=detail)
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
        return JsonResponse({"if_success": 1, "info": "添加成功"})

@login_required
def recv_verify(request):
    #三个参数分别是数组为payables的id，以及要type（0为现金，1为油卡）， 以及总的金额
    #action: 对于未付款的金额进行校对，如果金额大于最大金额就报错，否则对于数额依次进行修改
    #出票检查，只有已经出票的才能核销
    if request.method == "POST":
        if not request.user.has_perm("order_management.recv_verify"):
            return JsonResponse({"if_success": 0, "info":"没有进行此操作的权限"})
        recv_ids = request.POST.get("recv_ids","")
        recv_ids = recv_ids.split(",")
        received_ammount  = request.POST.get("received_ammount")
        t_received_ammount = received_ammount
        received_ammount = float(received_ammount)
        total_to_be_received = 0
        for single in recv_ids: #统计总的未付款
            recv_obj = RECEIVEABLES.objects.get(id=single)
            #检查是否有已经关闭的应收
            #if recv_obj.if_close == 1:
            #    return JsonResponse({"if_success": 0, "info":"无法更改已经关闭的订单的财务分录"})
            total_to_be_received = round(total_to_be_received + recv_obj.receiveables - recv_obj.received,2)
            #如果有未开票的就直接退出
            if recv_obj.invoice == None:
                return JsonResponse({"if_success": 0, "info": "核销失败：核销分录必须先开发票"})
        if total_to_be_received < received_ammount:
            return JsonResponse({"if_success": 0, "info":"确认失败：收款金额大于应收款"})

        # 获取这些记录对应的order号
        order_ids = []
        #可以进行付款操作
        _list = []
        for single in recv_ids:
            recv_obj = RECEIVEABLES.objects.get(id=single)
            order_ids.append(recv_obj.order_id)
            max_to_be_received = round(recv_obj.receiveables - recv_obj.received,2)
            if max_to_be_received >= received_ammount:
                #一次付清款，退出循环
                _list.append("描述：" + recv_obj.description + "：" + str(recv_obj.received) + "->" + str(round(recv_obj.received + received_ammount,2)))
                recv_obj.received += received_ammount
                if round(recv_obj.receiveables,2) == round(recv_obj.received,2):
                    recv_obj.clear_time=datetime.datetime.now()
                recv_obj.save()
                break
            else:
                _list.append("描述：" + recv_obj.description + "：" + str(recv_obj.received) + "->" + str(round(recv_obj.received + max_to_be_received,2)))
                received_ammount -= max_to_be_received
                recv_obj.received += max_to_be_received
                recv_obj.clear_time = datetime.datetime.now()
                recv_obj.save()
        #记录日志
        detail = "对 " + str(len(recv_ids)) + " 条应收款进行核销操作: 总金额： "+str(t_received_ammount)+" 核销前后变化分别为：" + str(_list)
        OPERATE_LOG.objects.create(user=request.user.username, field="应收账款", detail=detail)

        order_ids = list(set(order_ids))
        # 再对于order_ids进行遍历查看
        for single in order_ids:
            try:
                count_order_no_invoice = RECEIVEABLES.objects.filter(Q(order_id=single) & Q(clear_time=None)).count()
                if count_order_no_invoice == 0:
                    order_obj = ORDER.objects.get(id=single)
                    order_obj.status = 6
                    order_obj.save()
            except:
                continue
        return JsonResponse({"if_success": 1})

@login_required
def recv_cancel_verify(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.recv_verify"):
            return JsonResponse({"if_success": 0, "info":"没有进行此操作的权限"})
        recv_ids = request.POST.get("recv_ids", "")
        recv_ids = recv_ids.split(",")
        count_suc = 0


        #if RECEIVEABLES.objects.filter(Q(id__in=recv_ids) & Q(if_close=1)).count() != 0:
            #return JsonResponse({"if_success": 0, "info": "无法更改已经关闭的订单的财务分录"})

        #只有開票的分錄才可以反覈銷
        if RECEIVEABLES.objects.filter(Q(id__in=recv_ids) & Q(invoice=None)).count() != 0:
            return JsonResponse({"if_success": 0, "info": "核销失败：反核销分录必须先开发票"})

        recv_objs = RECEIVEABLES.objects.filter(id__in=recv_ids)
        log_list = []
        order_list = []
        for single in recv_objs:
            if single.status==0: #没有结账
                log_list.append("描述：" + single.description + " 应收：" + str(single.receiveables) + " 已收：" + str(
                    single.received))
                single.clear_time=None
                single.received=0
                single.save()
                order_list.append(single.order_id)
                count_suc += 1
        order_list = list(set(order_list))
        ORDER.objects.filter(id__in=order_list).update(status=5)
        detail = "对 " + str(recv_objs.count()) + " 条应收款进行反核销操作: 核销前金额分别为：" + str(log_list)
        OPERATE_LOG.objects.create(user=request.user.username, field="应收账款", detail=detail)
        return JsonResponse({"if_success": 1, "suc_num":count_suc})
