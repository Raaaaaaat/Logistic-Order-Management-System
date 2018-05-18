from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from order_management.models import ORDER
from order_management.models import PAYABLES
from order_management.models import SUPPLIER
from order_management.models import CLIENT
from order_management.models import OPERATE_LOG
import datetime,json
from django.db.models import Q
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required


@login_required
def get_paya_list(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.view_order_finance"):
            return JsonResponse({"data": []})
        bo_data             = json.loads(request.body.decode())
        f_order_No          = bo_data["f_order_No"]
        f_client            = bo_data["f_client"]
        f_supplier          = bo_data["f_supplier"]
        f_create_start_time = bo_data["f_create_start_time"]
        f_create_end_time   = bo_data["f_create_end_time"]
        f_clear_start_time  = bo_data["f_clear_start_time"]
        f_clear_end_time    = bo_data["f_clear_end_time"]
        f_if_total          = bo_data["f_if_total"] #这个参数用来过滤是否将已结账的分录也展示出来
        f_invoice           = bo_data["f_invoice"]
        f_status = bo_data["f_status"]


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
        if f_create_start_time != "":
            query = query & Q(create_time__gte=datetime.datetime.strptime(f_create_start_time, '%m/%d/%Y'))
        if f_create_end_time != "":
            query = query & Q(create_time__lte=datetime.datetime.strptime(f_create_end_time, '%m/%d/%Y')+datetime.timedelta(days=1))
        if f_clear_start_time != "":
            query = query & Q(clear_time__gte=datetime.datetime.strptime(f_clear_start_time, '%m/%d/%Y'))
        if f_clear_end_time != "":
            query = query & Q(clear_time__lte=datetime.datetime.strptime(f_clear_end_time, '%m/%d/%Y')+datetime.timedelta(days=1))
        if f_invoice != "":
            query = query & Q(invoice__contains=f_invoice)
        if f_if_total == "1":
            query = query #搜索全部
        if f_status != "0":
            if f_status == "1":
                query = query & Q(clear_time__isnull=False)
            else:
                query = query & Q(clear_time__isnull=True)
        else:
            query = query & Q(status=0)

        pay_obj = PAYABLES.objects.filter(query).order_by('-id').values()
        #除了表内基本信息，还有联合查询step 以及supplier的信息（由id查询name）


        supplier_obj = SUPPLIER.objects.all()
        supplier_dic = {}
        for line in supplier_obj:
            if line.type==0: #公司供应商
                supplier_dic[line.id] = line.No+" - "+line.co_name
            elif  line.type==1: #个人供应商
                supplier_dic[line.id] = line.No+" - "+line.contact_name
        rows = []
        index = 1
        for line in pay_obj:
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
            if line["supplier_id"] in supplier_dic:
                line["supplier_name"] = supplier_dic[line["supplier_id"]]
            else:
                line["supplier_name"] = "供应商已删除"



            line["create_time"] =datetime.datetime.strftime(localtime(line["create_time"]), '%Y-%m-%d')
            if line["clear_time"] != None:
                line["clear_time"] = datetime.datetime.strftime(localtime(line["clear_time"]), '%Y-%m-%d %H:%M:%S')
            rows.append(line)
        return JsonResponse({"data":rows})

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
        if invoice == "":#删除发票
            # 检查发票对应的应收账款，只要有一条有已收，就不允许删除发票
            list = []
            for single in paya_objs:
                if single.paid_oil != 0 or single.paid_cash!=0:
                    return JsonResponse({"if_success": 0, "info": "有已核销的发票不允许删除，请先反核销"})
                list.append(single.payables)
            paya_objs.update(invoice=None)
            detail = "删除 " + str(paya_objs.count()) + " 条应付款对应的发票: "+str(list)
            OPERATE_LOG.objects.create(user=request.user.username, field="应付账款", detail=detail)
        else:#新增发票
            try:
                list = []
                for single in paya_objs:
                    list.append(single.payables)
                detail = "开 " + str(paya_objs.count()) + " 条应付款对应的发票: " +invoice+"应付款数目" + str(list)
                OPERATE_LOG.objects.create(user=request.user.username, field="应付账款", detail=detail)
                paya_objs.update(invoice=invoice)
            except:
                return JsonResponse({"if_success": 0, "info":"更新失败"})
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
                else:
                    list.append("描述："+paya_obj.description+"："+str(paya_obj.paid_oil) + "->" + str(round(paya_obj.paid_oil + paid_ammount,2)))
                    paya_obj.paid_oil += paid_ammount
                if paya_obj.payables == paya_obj.paid_cash + paya_obj.paid_oil:
                    paya_obj.clear_time=datetime.datetime.now()
                paya_obj.save()
                break
            else:
                paid_ammount -= max_to_be_paid
                if paid_type=="0":
                    list.append("描述："+paya_obj.description+"："+str(paya_obj.paid_cash) + "->" + str(round(paya_obj.paid_cash + max_to_be_paid,2)))
                    paya_obj.paid_cash += max_to_be_paid
                else:
                    list.append("描述："+paya_obj.description+"："+str(paya_obj.paid_oil) + "->" + str(round(paya_obj.paid_oil + max_to_be_paid,2)))
                    paya_obj.paid_oil += max_to_be_paid
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
        for single in paya_ids:
            paya_obj = PAYABLES.objects.get(id=single)
            if paya_obj.status==0:
                list.append("描述："+paya_obj.description+" 应付："+str(paya_obj.payables)+" 已付油卡："+str(paya_obj.paid_oil)+" 已付现金："+str(paya_obj.paid_cash))
                paya_obj.clear_time=None
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
                if paid_obj.status==0 and paid_obj.payables == paid_obj.paid_oil + paid_obj.paid_cash:
                    paid_obj.status=1
                    paid_obj.save()
                    count_suc = count_suc + 1
                else:
                    count_err = count_err + 1
            except:
                count_err = count_err+1

        return JsonResponse({"if_success": 1, "count_suc": count_suc, "count_err":count_err})
    return JsonResponse({"if_success": 0})
