from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from order_management.models import ORDER
from order_management.models import PAYABLES
from order_management.models import SUPPLIER
from order_management.models import CLIENT
from order_management.models import OPERATE_LOG
import datetime,json
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import xlsxwriter #用来导出excel文件
import time
from django.http import FileResponse


@login_required
def get_paya_list(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.view_order_finance"):
            return JsonResponse({"data": []})
        bo_data             = json.loads(request.body.decode())
        f_order_No          = bo_data["f_order_No"]
        f_client            = bo_data["f_client"]
        f_supplier          = bo_data["f_supplier"]
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
        group_supplier_id   = bo_data["group_supplier"]
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
        if f_supplier != "":
            query = query & Q(supplier_id=f_supplier)
        #編輯與2018 5 29, 希望能通過次查詢篩選出訂單在此時間範圍內創建對應的記錄
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
            query = query & Q(invoice__contains=f_invoice)
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



        #add in 1/21/2019
        if group_order_id or group_client_id or group_supplier_id:
            if group_order_id:
                if group_client_id:
                    if group_supplier_id:
                        #111
                        pay_obj = PAYABLES.objects.filter(query).values('order_id','client_id','supplier_id').annotate(payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))[f_offset:f_offset+f_limit]
                        paya_count = PAYABLES.objects.filter(query).values('order_id','client_id','supplier_id').annotate(payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil')).count()
                    else:
                        #110
                        pay_obj = PAYABLES.objects.filter(query).values('order_id', 'client_id',).annotate(
                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))[
                                  f_offset:f_offset + f_limit]
                        paya_count = PAYABLES.objects.filter(query).values('order_id', 'client_id',).annotate(
                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil')).count()

                else:
                    if group_supplier_id:
                        #101
                        pay_obj = PAYABLES.objects.filter(query).values('order_id', 'supplier_id').annotate(
                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))[
                                  f_offset:f_offset + f_limit]
                        paya_count = PAYABLES.objects.filter(query).values('order_id','supplier_id').annotate(
                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil')).count()
                    else:
                        #100
                        pay_obj = PAYABLES.objects.filter(query).values('order_id').annotate(                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))[f_offset:f_offset + f_limit]
                        paya_count = PAYABLES.objects.filter(query).values('order_id').annotate(                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil')).count()
            else:
                if group_client_id:
                    if group_supplier_id:
                        #011
                        pay_obj = PAYABLES.objects.filter(query).values('client_id','supplier_id').annotate(
                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))[
                                  f_offset:f_offset + f_limit]
                        paya_count = PAYABLES.objects.filter(query).values('client_id','supplier_id').annotate(
                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil')).count()
                    else:
                        #010
                        pay_obj = PAYABLES.objects.filter(query).values('client_id').annotate(payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))[f_offset:f_offset + f_limit]
                        paya_count = PAYABLES.objects.filter(query).values('client_id').annotate(payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil')).count()

                else:
                    if group_supplier_id:
                        #001
                        pay_obj = PAYABLES.objects.filter(query).values('supplier_id').annotate(                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))[f_offset:f_offset + f_limit]
                        paya_count = PAYABLES.objects.filter(query).values('supplier_id').annotate(                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil')).count()
        else:
            pay_obj = PAYABLES.objects.filter(query).order_by('-id').values()[f_offset:f_offset + f_limit]
            paya_count = PAYABLES.objects.filter(query).count()
            # 除了表内基本信息，还有联合查询step 以及supplier的信息（由id查询name）


        supplier_obj = SUPPLIER.objects.all()
        supplier_dic = {}
        for line in supplier_obj:
            if line.type==0: #公司供应商
                supplier_dic[line.id] = line.co_name
            elif  line.type==1: #个人供应商
                supplier_dic[line.id] = line.contact_name
        rows = []
        index = int(f_offset)+1
        for line in pay_obj:
            line["payables"] = round(line["payables"],2)
            line["paid_oil"] = round(line["paid_oil"], 2)
            line["paid_cash"] = round(line["paid_cash"], 2)
            if 'order_id' in line:
                order_obj = ORDER.objects.get(id=line["order_id"])
                line["index"] = index
                index += 1
                line["order_No"] = order_obj.No
                line["dep_city"] = order_obj.dep_city
                line["des_city"] = order_obj.des_city
                line["order_create_time"] = datetime.datetime.strftime(order_obj.create_time, '%Y-%m-%d')
                if order_obj.pick_up_time != None:
                    line["order_pick_time"] = datetime.datetime.strftime(order_obj.pick_up_time, '%Y-%m-%d')
                line["client_id"] = order_obj.client_id
            else:
                line["order_No"]=""
            if 'client_id' in line:
                try:
                    client_obj = CLIENT.objects.get(id=line['client_id'])
                    if client_obj.type == 0:
                        line["client_name"] = client_obj.co_name
                    else:
                        line["client_name"] = client_obj.contact_name
                except:
                    line["client_name"] = "客户已删除"
            else:
                line["client_name"]=""
            if 'supplier_id' in line:
                if line["supplier_id"] in supplier_dic:
                    line["supplier_name"] = supplier_dic[line["supplier_id"]]
                else:
                    line["supplier_name"] = "供应商已删除"
            else:
                line["supplier_name"]=""

            if 'create_time' in line:
                line["create_time"] =datetime.datetime.strftime(line["create_time"], '%Y-%m-%d')
                if line["clear_time"] != None:
                    line["clear_time"] = datetime.datetime.strftime(line["clear_time"], '%Y-%m-%d %H:%M:%S')
                #如果没有分类组合，对于票号进行整合 编辑于2019 4 16
                invoice = line["invoice"]
                if len(invoice)>0 and invoice[0]=="|":
                    inv_des = "历史记录："
                    inv_show = ""
                    invoice = invoice[1:].split("|")
                    len_inv = len(invoice)
                    if len_inv%2 == 0:
                        for i in range(int(len_inv/2)):
                            inv_des = inv_des+"<br>" + invoice[i*2] + " : "+invoice[i*2+1]

                            if inv_show != "":
                                inv_show = inv_show+", "+invoice[i*2+1]
                            else:
                                inv_show = invoice[i * 2 + 1]
                        line["invoice"]     = inv_show
                        line["invoice_his"] = inv_des

            else: #说明是分类组合的结果，除了６个字段之外别的字段都不存在
                line["description"] = ""
                line["pay_log"]     = ""
            rows.append(line)
        return JsonResponse({"total":paya_count,"rows":rows})

@login_required
def mark_paya_invoice(request):
    #两个参数分别是数组为payables的id，以及要批量修改的票号
    if request.method == "POST":
        if not request.user.has_perm("order_management.paya_invoice"):
            return JsonResponse({"if_success":0, "info":"没有进行此操作的权限，请联系管理员"})
        paya_ids = request.POST.get("paya_ids","")
        paya_ids = paya_ids.split(",")
        invoice  = request.POST.get("invoice")
        paya_objs = PAYABLES.objects.filter(id__in=paya_ids)
        if invoice == "清空":#删除发票
            # 检查发票对应的应收账款，只要有一条有已收，就不允许删除发票
            list = []
            for single in paya_objs:
                if single.paid_oil != 0 or single.paid_cash!=0:
                    return JsonResponse({"if_success": 0, "info": "有已核销的发票不允许删除，请先反核销"})
                list.append(single.payables)
            paya_objs.update(invoice="")
            detail = "删除 " + str(paya_objs.count()) + " 条应付款对应的发票: "+str(list)
            OPERATE_LOG.objects.create(user=request.user.username, field="应付账款", detail=detail)
        elif invoice != "":#新增发票
            try:
                list = []
                for single in paya_objs:
                    list.append(single.payables)
                detail = "开 " + str(paya_objs.count()) + " 条应付款对应的发票: " +invoice+"应付款数目" + str(list)
                OPERATE_LOG.objects.create(user=request.user.username, field="应付账款", detail=detail)
                for single in paya_objs:
                    old_invoice = single.invoice
                    dateStr = datetime.datetime.strftime(datetime.datetime.now(), '%m/%d/%Y')
                    single.invoice=old_invoice+"|"+dateStr+"|"+invoice
                    single.save()
            except:
                return JsonResponse({"if_success": 0, "info":"更新失败"})
        else:
            return JsonResponse({"if_success": 0, "info": "不允许空发票号"})
        return JsonResponse({"if_success": 1,"info":"开票成功"})

@login_required
def paya_verify(request):
    #三个参数分别是数组为payables的id，以及要type（0为现金，1为油卡）， 以及总的金额
    #action: 对于未付款的金额进行校对，如果金额大于最大金额就报错，否则对于数额依次进行修改
    if request.method == "POST":
        if not request.user.has_perm("order_management.paya_verify"):
            return JsonResponse({"if_success":0, "info":"没有进行此操作的权限，请联系管理员"})
        paya_ids = request.POST.get("paya_ids","")
        paya_ids = paya_ids.split(",")
        paid_ammount  = request.POST.get("paid_ammount")
        t_paid_ammount = paid_ammount
        paid_type = request.POST.get("paid_type")
        paid_ammount = float(paid_ammount)
        total_to_be_paid = 0
        for single in paya_ids: #统计总的未付款
            paya_obj = PAYABLES.objects.get(id=single)
            #if paya_obj.if_close == 1:
            #    return JsonResponse({"if_success": 0, "info": "无法更改已经关闭的订单的财务分录"})
            total_to_be_paid = round(total_to_be_paid + paya_obj.payables - paya_obj.paid_cash - paya_obj.paid_oil, 2)
        if total_to_be_paid < paid_ammount:
            return JsonResponse({"if_success": 0, "info":"确认失败：付款金额大于应付款"})

        #可以进行付款操作
        list=[]
        for single in paya_ids:
            paya_obj = PAYABLES.objects.get(id=single)
            max_to_be_paid = round(paya_obj.payables - paya_obj.paid_cash - paya_obj.paid_oil, 2)
            if max_to_be_paid >= paid_ammount:
                #一次付清款，退出循环
                if paid_type=="0":
                    list.append("描述："+paya_obj.description+"："+str(paya_obj.paid_cash)+"->"+str(round(paya_obj.paid_cash+paid_ammount,2)))
                    paya_obj.paid_cash += paid_ammount
                    #加于2019 4 21
                    paya_obj.pay_log = paya_obj.pay_log + "|"+time.strftime("%Y/%m/%d: ", time.localtime())+"核销现金"+str(round(paid_ammount,2))
                else:
                    list.append("描述："+paya_obj.description+"："+str(paya_obj.paid_oil) + "->" + str(round(paya_obj.paid_oil + paid_ammount,2)))
                    paya_obj.paid_oil += paid_ammount
                    paya_obj.pay_log = paya_obj.pay_log + "|" + time.strftime("%Y/%m/%d: ",
                                                 time.localtime()) + "核销油卡" + str(round(paid_ammount, 2))
                if paya_obj.payables == round(paya_obj.paid_cash + paya_obj.paid_oil,2):
                    paya_obj.clear_time=datetime.datetime.now()
                paya_obj.save()
                break
            else:
                paid_ammount -= max_to_be_paid
                if paid_type=="0":
                    list.append("描述："+paya_obj.description+"："+str(paya_obj.paid_cash) + "->" + str(round(paya_obj.paid_cash + max_to_be_paid,2)))
                    paya_obj.paid_cash += max_to_be_paid
                    paya_obj.pay_log = paya_obj.pay_log + "|" + \
                                        time.strftime("%Y/%m/%d: ",time.localtime()) + "核销现金" + str(round(max_to_be_paid, 2))
                else:
                    list.append("描述："+paya_obj.description+"："+str(paya_obj.paid_oil) + "->" + str(round(paya_obj.paid_oil + max_to_be_paid,2)))
                    paya_obj.paid_oil += max_to_be_paid
                    paya_obj.pay_log = paya_obj.pay_log + "|" + \
                                       time.strftime("%Y/%m/%d: ", time.localtime()) + "核销油卡" + str(round(max_to_be_paid, 2))
                paya_obj.clear_time = datetime.datetime.now()
                paya_obj.save()
        if paid_type=="0":
            paid_type="现金"
        else:
            paid_type="油卡"
        detail = "对 " + str(len(paya_ids)) + " 条应付款进行核销操作: 总金额： "+str(t_paid_ammount)+" 类型： "+paid_type+"  变化金额分别为：" + str(list)
        OPERATE_LOG.objects.create(user=request.user.username, field="应付账款", detail=detail)
        return JsonResponse({"if_success": 1})

@login_required
def paya_cancel_verify(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.paya_verify"):
            return JsonResponse({"if_success":0, "info":"没有进行此操作的权限，请联系管理员"})
        paya_ids = request.POST.get("paya_ids", "")
        paya_ids = paya_ids.split(",")
        count_suc = 0
        list=[]

        #if PAYABLES.objects.filter(Q(id__in=paya_ids) & Q(if_close=1)).count() != 0:
            #return JsonResponse({"if_success": 0, "info": "无法更改已经关闭的订单的财务分录"})

        for single in paya_ids:
            paya_obj = PAYABLES.objects.get(id=single)
            if paya_obj.status==0:
                list.append("描述："+paya_obj.description+" 应付："+str(paya_obj.payables)+" 已付油卡："+str(paya_obj.paid_oil)+" 已付现金："+str(paya_obj.paid_cash))
                paya_obj.clear_time=None
                paya_obj.pay_log = paya_obj.pay_log + "|" + \
                                   time.strftime("%Y/%m/%d: ", time.localtime()) + "反核销"
                paya_obj.paid_cash=0
                paya_obj.paid_oil=0
                paya_obj.save()
                count_suc += 1
        detail = "对 " + str(len(paya_ids)) + " 条应付款进行反核销操作: 核销前金额分别为：" + str(list)
        OPERATE_LOG.objects.create(user=request.user.username, field="应付账款", detail=detail)
        return JsonResponse({"if_success": 1, "suc_num":count_suc})

def paya_settle_accounts(request):
    # 以个参数是数组为payables的id
    # action: 逐条对于数据进行检查，如果付款完成就修改状态，否则不予理会，然后统计修改成功的条数
    if request.method == "POST":
        paya_ids = request.POST.get("paya_ids", "")
        paya_ids = paya_ids.split(",")
        count_suc = 0
        count_err = 0
        for single in paya_ids:
            try:
                paid_obj = PAYABLES.objects.get(id=single)
                if paid_obj.status==0 and paid_obj.payables == round(paid_obj.paid_oil + paid_obj.paid_cash,2):
                    paid_obj.status=1
                    paid_obj.save()
                    count_suc = count_suc + 1
                else:
                    count_err = count_err + 1
            except:
                count_err = count_err+1

        return JsonResponse({"if_success": 1, "count_suc": count_suc, "count_err":count_err})
    return JsonResponse({"if_success": 0})

def get_paya_excel(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.view_order_finance"):
            return JsonResponse({"data": []})
        f_order_No          = request.POST.get("f_order_No","")
        f_client            = request.POST.get("f_client","")
        f_supplier          = request.POST.get("f_supplier","")
        f_pick_start_time   = request.POST.get("f_pick_start_time","")
        f_pick_end_time     = request.POST.get("f_pick_end_time","")
        f_clear_start_time  = request.POST.get("f_clear_start_time","")
        f_clear_end_time    = request.POST.get("f_clear_end_time","")
        f_if_total          = request.POST.get("f_if_total","")
        f_invoice           = request.POST.get("f_invoice","")
        f_status            = request.POST.get("f_status","")
        group_order_id      = request.POST.get("group_order","")
        group_supplier_id   = request.POST.get("group_supplier","")
        group_client_id     = request.POST.get("group_client","")

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
        if f_supplier != "":
            query = query & Q(supplier_id=f_supplier)
        #編輯與2018 5 29, 希望能通過次查詢篩選出訂單在此時間範圍內創建對應的記錄
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
            query = query & Q(invoice__contains=f_invoice)
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



        if group_supplier_id=='true':
            group_supplier_id=True
        else:
            group_supplier_id=False
        if group_client_id=='true':
            group_client_id=True
        else:
            group_client_id=False
        if group_order_id=='true':
            group_order_id=True
        else:
            group_order_id=False
        if group_order_id  or group_client_id or group_supplier_id:
            if group_order_id:
                if group_client_id:
                    if group_supplier_id:
                        #111
                        pay_obj = PAYABLES.objects.filter(query).values('order_id','client_id','supplier_id').annotate(payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))
                    else:
                        #110
                        pay_obj = PAYABLES.objects.filter(query).values('order_id', 'client_id',).annotate(
                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))


                else:
                    if group_supplier_id:
                        #101
                        pay_obj = PAYABLES.objects.filter(query).values('order_id', 'supplier_id').annotate(
                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))

                    else:
                        #100
                        pay_obj = PAYABLES.objects.filter(query).values('order_id').annotate(                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))

            else:
                if group_client_id:
                    if group_supplier_id:
                        #011
                        pay_obj = PAYABLES.objects.filter(query).values('client_id','supplier_id').annotate(
                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))

                    else:
                        #010
                        pay_obj = PAYABLES.objects.filter(query).values('client_id').annotate(payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))


                else:
                    if group_supplier_id:
                        #001
                        pay_obj = PAYABLES.objects.filter(query).values('supplier_id').annotate(                            payables=Sum('payables'), paid_cash=Sum('paid_cash'), paid_oil=Sum('paid_oil'))
        else:
            pay_obj = PAYABLES.objects.filter(query).order_by('-id').values()

            # 除了表内基本信息，还有联合查询step 以及supplier的信息（由id查询name）


        supplier_obj = SUPPLIER.objects.all()
        supplier_dic = {}
        for line in supplier_obj:
            if line.type==0: #公司供应商
                supplier_dic[line.id] = line.co_name
            elif  line.type==1: #个人供应商
                supplier_dic[line.id] = line.contact_name
        rows = []
        index = 0
        for line in pay_obj:
            if 'order_id' in line:
                order_obj = ORDER.objects.get(id=line["order_id"])
                line["index"] = index
                index += 1
                line["order_No"] = order_obj.No
                line["dep_city"] = order_obj.dep_city
                line["des_city"] = order_obj.des_city
                line["order_create_time"] = datetime.datetime.strftime(order_obj.create_time, '%Y-%m-%d')
                if order_obj.pick_up_time != None:
                    line["order_pick_time"] = datetime.datetime.strftime(order_obj.pick_up_time, '%Y-%m-%d')
                line["client_id"] = order_obj.client_id
            else:
                line["order_No"]=""
            if 'client_id' in line:
                try:
                    client_obj = CLIENT.objects.get(id=line['client_id'])
                    if client_obj.type == 0:
                        line["client_name"] = client_obj.co_name
                    else:
                        line["client_name"] = client_obj.contact_name
                except:
                    line["client_name"] = "客户已删除"
            else:
                line["client_name"]=""
            if 'supplier_id' in line:
                if line["supplier_id"] in supplier_dic:
                    line["supplier_name"] = supplier_dic[line["supplier_id"]]
                else:
                    line["supplier_name"] = "供应商已删除"
            else:
                line["supplier_name"]=""

            if 'create_time' in line:
                line["create_time"] =datetime.datetime.strftime(line["create_time"], '%Y-%m-%d')
                if line["clear_time"] != None:
                    line["clear_time"] = datetime.datetime.strftime(line["clear_time"], '%Y-%m-%d %H:%M:%S')
                #如果没有分类组合，对于票号进行整合 编辑于2019 4 16
                invoice = line["invoice"]
                if len(invoice)>0 and invoice[0]=="|":
                    inv_des = "历史记录："
                    inv_show = ""
                    invoice = invoice[1:].split("|")
                    len_inv = len(invoice)
                    if len_inv%2 == 0:
                        for i in range(int(len_inv/2)):
                            inv_des = inv_des+"<br>" + invoice[i*2] + " : "+invoice[i*2+1]

                            if inv_show != "":
                                inv_show = inv_show+", "+invoice[i*2+1]
                            else:
                                inv_show = invoice[i * 2 + 1]
                        line["invoice"]     = inv_show
                        line["invoice_his"] = inv_des

            else: #说明是分类组合的结果，除了６个字段之外别的字段都不存在
                line["description"] = ""
                line["pay_log"]     = ""
            rows.append(line)

        path = "/var/www/tmr/order_management/static/tmp_file/finance/"
        filename = "paya_export.xlsx"
        workbook = xlsxwriter.Workbook(path + filename)
        worksheet = workbook.add_worksheet('sheet')

        keys = ['接单时间', '提货时间', '单号', '客户', '供应商', '起运地', '目的地', '描述', '应收金额', '已收金额', '已收油卡', '收款时间', '票号', '状态']
        cell_format = workbook.add_format()

        cell_format.set_bold()  # Turns bold on.
        cell_format.set_font_size(12)
        worksheet.write_row('A1', keys, cell_format)

        num_row = 1

        for line in rows:
            if 'order_create_time' in line:
                worksheet.write(num_row, 0, line['order_create_time'])
            if 'order_pick_time' in line:
                worksheet.write(num_row, 1, line['order_pick_time'])
            if 'order_No' in line:
                worksheet.write(num_row, 2, line['order_No'])
            if 'client_name' in line:
                worksheet.write(num_row, 3, line['client_name'])
            if 'supplier_name' in line:
                worksheet.write(num_row, 4, line['supplier_name'])
            if 'dep_city' in line:
                worksheet.write(num_row, 5, line['dep_city'])
            if 'des_city' in line:
                worksheet.write(num_row, 6, line['des_city'])
            if 'description' in line:
                worksheet.write(num_row, 7, line['description'])
            #这两个值一定有，不用判断
            worksheet.write_number(num_row, 8, line['payables'])
            worksheet.write_number(num_row, 9, line['paid_cash'])
            worksheet.write_number(num_row, 10, line['paid_oil'])
            if 'order_pick_time' in line:
                worksheet.write(num_row, 11, line['order_pick_time'])
            if 'invoice' in line:
                worksheet.write(num_row, 12, line['invoice'])
            if 'status' in line:
                if line['status']=='0':
                    i_status = '未结账'
                else:
                    i_status = '已结账'
                worksheet.write(num_row, 13, i_status)
            num_row = num_row+1


        worksheet.set_column('A:B', 12)
        worksheet.set_column('C:C', 13)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 25)

        worksheet.set_column('H:H', 12)
        worksheet.set_column('L:L', 12)
        worksheet.set_column('I:K', 10)

        workbook.close()

        file = open(path+filename, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="'+filename+'"'
        return response