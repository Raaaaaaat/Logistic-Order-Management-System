from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from order_management.models import ORDER
from order_management.models import RECEIVEABLES
from order_management.models import PAYABLES
from order_management.models import SUP_STEP
from order_management.models import SUPPLIER
from order_management.models import OPERATE_LOG
from order_management.models import EDIT_PRICE_REQUEST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
import json,time, datetime
import pytz

@login_required
@permission_required('order_management.view_order', login_url='/error?info=没有查看订单的权限，请联系管理员')
def index_price(request):
    if request.method == "GET":
        No = request.GET.get('No', '')
        order_obj = get_object_or_404(ORDER, No=No)
        return render(request, "order/price.html", {
            "No": No,
            "order_id": order_obj.id,
        })

@login_required
def get_receiveables(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.view_order"):
            return JsonResponse({'rows': []})
        order_id = request.POST.get("order_id")
        rec_obj = RECEIVEABLES.objects.filter(order_id=order_id).values()
        rows = []
        for line in rec_obj:
            rows.append(line)
        return JsonResponse({"rows":rows})
@login_required
def add_receiveables(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.recv_manage"):
            return JsonResponse({"if_success":0, "info":"没有管理应收账款的权限"})
        #如果订单状态是5或者6则需要变更回来到4
        order_id = request.POST.get("order_id")
        order_obj = ORDER.objects.filter(id=order_id).first()
        if order_obj == None:
            if_success = 0
            info = "订单对象不存在"
        else:
            if order_obj.status > 4:
                order_obj.status = 4
                order_obj.save()
            description = request.POST.get("description","")
            price = request.POST.get("price")
            RECEIVEABLES.objects.create(status=0, order_id=order_id,description=description,
                                    receiveables=price, received=0)
            detail = "增加 "+order_obj.No+" 应收款："+str(price)+" 描述："+description
            OPERATE_LOG.objects.create(user=request.user.username, field="应收账款", detail=detail)
            if_success = 1
            info = "添加成功"
        return JsonResponse({"if_success":if_success, "info":info})
@login_required
def delete_receiveables(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.recv_manage"):
            return JsonResponse({"if_success":0, "info":"没有管理应收账款的权限"})
        rec_id = request.POST.get("rec_id",0)
        #确定是否开票，如果是则不允许删除
        try:
            rec_obj = RECEIVEABLES.objects.get(id=rec_id)
            if rec_obj.invoice == None:
                devider = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 1, tzinfo=pytz.timezone('Asia/Shanghai'))
                if rec_obj.create_time < devider:
                    EDIT_PRICE_REQUEST.objects.create(user=request.user.username, type="recv_delete",target_id=rec_obj.id,target_price=0)
                    # 增加日志
                    order_obj = ORDER.objects.filter(id=rec_obj.order_id).first()
                    if order_obj == None:
                        detail = "申请删除应收款：发生错误"
                    else:
                        detail = "申请删除 " + order_obj.No + " 应收款：" + str(
                            rec_obj.receiveables) + " 描述：" + rec_obj.description
                    OPERATE_LOG.objects.create(user=request.user.username, field="应收账款", detail=detail)
                    if_success = 2
                    info = "由于分录创建时间为上个月，无法直接删除应付，已经向财务部门递交申请"
                else:
                    order_obj = ORDER.objects.filter(id=rec_obj.order_id).first()
                    if order_obj == None:
                        detail = "删除应收款：发生错误"
                    else:
                        detail = "删除 " + order_obj.No + " 应收款：" + str(rec_obj.receiveables) + " 描述：" + rec_obj.description
                    OPERATE_LOG.objects.create(user=request.user.username, field="应收账款", detail=detail)
                    rec_obj.delete()
                    if_success = 1
                    info = "删除成功"
            else:
                if_success = 0
                info = "已开票的分录无法删除，请先删除发票信息"
        except:
            info = "删除失败：记录不存在"
            if_success = 0
        return JsonResponse({"if_success":if_success, "info":info})
    return JsonResponse({})
@login_required
def update_receiveables_desc(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.recv_manage"):
            return JsonResponse({"if_success":0, "info":"没有管理应收账款的权限"})
        rec_id = request.POST.get("rec_id",0)
        desc = request.POST.get("desc","")
        if_success = 0
        info = ""
        try:
            rec_obj = RECEIVEABLES.objects.get(id=rec_id)
            order_obj = ORDER.objects.filter(id=rec_obj.order_id).first()
            if order_obj == None:
                detail = "更新应收款描述：发生错误"
            else:
                detail = "更新 " + order_obj.No + " 应收款描述：" + str(rec_obj.receiveables) + " 旧描述：" + rec_obj.description +" 为新描述："+str(desc)
            OPERATE_LOG.objects.create(user=request.user.username, field="应收账款", detail=detail)
            rec_obj.description = desc
            rec_obj.save()
            if_success = 1
            info = "修改成功"
        except:
            info = "修改失败：记录不存在"
        return JsonResponse({"if_success":if_success, "info":info})
@login_required
def update_receiveables_price(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.recv_manage"):
            return JsonResponse({"if_success":0, "info":"没有管理应收账款的权限"})
        rec_id = request.POST.get("rec_id")
        price = request.POST.get("price")
        if_success = 0
        info = ""
        try:

            rec_obj = RECEIVEABLES.objects.get(id=rec_id)
            if rec_obj.invoice == None:
                # 检查创建时间是否是上个月，如果不是就直接修改，否则递交申请给财务
                devider = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 1,tzinfo=pytz.timezone('Asia/Shanghai'))
                if rec_obj.create_time < devider:
                    EDIT_PRICE_REQUEST.objects.create(user=request.user.username, type="recv", target_id=rec_obj.id,
                                                      target_price=price)
                    # 增加日志
                    order_obj = ORDER.objects.filter(id=rec_obj.order_id).first()
                    if order_obj == None:
                        detail = "申请更新应收款价格：发生错误"
                    else:
                        detail = "申请更新 " + order_obj.No+" 应收款价格："+rec_obj.description + " 旧价格：" + str(rec_obj.receiveables) + " 为新价格：" + str(price)
                    OPERATE_LOG.objects.create(user=request.user.username, field="应收账款", detail=detail)
                    if_success = 2
                    info = "由于分录创建时间为上个月，无法直接修改价格，已经向财务部分递交申请"
                else:
                    order_obj = ORDER.objects.filter(id=rec_obj.order_id).first()
                    if order_obj == None:
                        detail = "更新应收款价格：发生错误"
                    else:
                        detail = "更新 " + order_obj.No + " 应收款价格：" + rec_obj.description + " 旧价格：" + str(rec_obj.receiveables) + " 为新价格：" + str(price)
                    OPERATE_LOG.objects.create(user=request.user.username, field="应收账款", detail=detail)
                    rec_obj.receiveables = price
                    rec_obj.save()
                    if_success = 1
                    info = "修改成功"
            else:
                if_success = 0
                info = "已开票的分录无法修改价格，请先删除发票信息"
        except:
            info = "修改失败：记录不存在"
        return JsonResponse({"if_success":if_success, "info":info})



#应付账款part
@login_required
def get_payables(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.view_order"):
            return JsonResponse({'rows': []})
        order_id = request.POST.get("order_id")
        pay_obj = PAYABLES.objects.filter(order_id=order_id).values()
        #除了表内基本信息，还有联合查询step 以及supplier的信息（由id查询name）
        step_objs = SUP_STEP.objects.all()
        step_dic = {}
        for line in step_objs:
            step_dic[line.id] = line.name

        supplier_obj = SUPPLIER.objects.all()
        supplier_dic = {}
        for line in supplier_obj:
            if line.type==0: #公司供应商
                supplier_dic[line.id] = line.No+" - "+line.co_name
            elif  line.type==1: #个人供应商
                supplier_dic[line.id] = line.No+" - "+line.contact_name
        rows = []
        for line in pay_obj:
            line["step_name"]= step_dic[line["step"]]
            if line["supplier_id"] in supplier_dic:
                line["supplier_name"] = supplier_dic[line["supplier_id"]]
            else:
                line["supplier_name"] = "该供应商已删除"
            rows.append(line)
        return JsonResponse({"rows":rows})
@login_required
def add_payables(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.paya_manage"):
            return JsonResponse({"if_success":0, "info":"没有管理应付账款的权限"})
        order_id = request.POST.get("order_id")

        step = request.POST.get("step")
        supplier_id = request.POST.get("supplier_id")
        #检查供应商的有效其是否生效
        sup_obj = SUPPLIER.objects.filter(id=supplier_id).first()
        if sup_obj==None:
            return JsonResponse({"if_success": 0, "info": "供应商不存在"})
        else:
            start_time = sup_obj.contract_start
            end_time = sup_obj.contract_end
            now = datetime.datetime.now()
            if start_time != "":
                start_time = datetime.datetime.strptime(start_time, "%m/%d/%Y")
                if now < start_time:
                    return JsonResponse({"if_success": 0, "info": "供应商不在有效期"})

            if end_time != "":
                end_time = datetime.datetime.strptime(end_time, "%m/%d/%Y") + datetime.timedelta(days=1)
                if now > end_time:
                    return JsonResponse({"if_success": 0, "info": "供应商不在有效期"})
        description = request.POST.get("description")
        price = request.POST.get("price")
        PAYABLES.objects.create(status=0, order_id=order_id,description=description,
                                payables=price, paid_cash=0, paid_oil=0, step=step, supplier_id=supplier_id)
        order_obj = ORDER.objects.get(id=order_id)
        detail = "增加 " + order_obj.No + " 应付款：" + str(price) + " 供应商：" + sup_obj.No + " 描述：" + description
        OPERATE_LOG.objects.create(user=request.user.username, field="应收账款", detail=detail)
        return JsonResponse({"if_success":1, "info":"添加成功"})

@login_required
def delete_payables(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.paya_manage"):
            return JsonResponse({"if_success":0, "info":"没有管理应付账款的权限"})
        pay_id = request.POST.get("pay_id",0)
        try:
            pay_obj = PAYABLES.objects.get(id=pay_id)
            if pay_obj.invoice == None or pay_obj.invoice=="":
                devider = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 1, tzinfo=pytz.timezone('Asia/Shanghai'))
                if pay_obj.create_time < devider:
                    EDIT_PRICE_REQUEST.objects.create(user=request.user.username, type="paya_delete", target_id=pay_obj.id,
                                                      target_price=0)
                    # 增加日志
                    order_obj = ORDER.objects.filter(id=pay_obj.order_id).first()
                    if order_obj == None:
                        detail = "申请删除应收款：发生错误"
                    else:
                        detail = "申请删除 " + order_obj.No + " 应付款：" + str(pay_obj.payables) + " 描述：" + pay_obj.description
                    OPERATE_LOG.objects.create(user=request.user.username, field="应付账款", detail=detail)
                    if_success = 2
                    info = "由于分录创建时间为上个月，无法直接删除应付，已经向财务部分递交申请"
                else:
                    order_obj = ORDER.objects.filter(id=pay_obj.order_id).first()
                    if order_obj == None:
                        detail = "删除应收款：发生错误"
                    else:
                        detail = "删除 " + order_obj.No + " 应付款：" + str(pay_obj.payables) + " 描述：" + pay_obj.description
                    OPERATE_LOG.objects.create(user=request.user.username, field="应付账款", detail=detail)
                    pay_obj.delete()
                    if_success = 1
                    info = "删除成功"
            else:
                if_success = 0
                info = "已经开票的分录无法删除，请先清空发票信息"
        except:
            info = "删除失败：记录不存在"
            if_success = 0
        return JsonResponse({"if_success":if_success, "info":info})
    return JsonResponse({})

@login_required
def update_payables_info(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.paya_manage"):
            return JsonResponse({"if_success":0, "info":"没有管理应付账款的权限"})
        pay_id = request.POST.get("pay_id",0)
        desc = request.POST.get("desc","")
        supplier_id = request.POST.get("supplier_id")
        # 检查供应商的有效其是否生效
        sup_obj = SUPPLIER.objects.filter(id=supplier_id).first()
        if sup_obj == None:
            return JsonResponse({"if_success": 0, "info": "供应商不存在"})
        else:
            start_time = sup_obj.contract_start
            end_time = sup_obj.contract_end
            now = datetime.datetime.now()
            if start_time != "":
                start_time = datetime.datetime.strptime(start_time, "%m/%d/%Y")
                if now < start_time:
                    return JsonResponse({"if_success": 0, "info": "供应商不在有效期"})

            if end_time != "":
                end_time = datetime.datetime.strptime(end_time, "%m/%d/%Y") + datetime.timedelta(days=1)
                if now > end_time:
                    return JsonResponse({"if_success": 0, "info": "供应商不在有效期"})
        if_success = 0
        info = ""
        try:
            pay_obj = PAYABLES.objects.get(id=pay_id)
            order_obj = ORDER.objects.filter(id=pay_obj.order_id).first()
            if order_obj == None:
                detail = "更新应收款价格：发生错误"
            else:
                detail = "更新 " + order_obj.No + " 应付款信息：" + str(pay_obj.payables) + " 旧描述：" + pay_obj.description + " 为新描述：" + desc + " 旧供应商：" + SUPPLIER.objects.get(id=pay_obj.supplier_id).No + " 为新供应商：" + SUPPLIER.objects.get(id=supplier_id).No
            OPERATE_LOG.objects.create(user=request.user.username, field="应付账款", detail=detail)
            pay_obj.description = desc
            pay_obj.supplier_id = supplier_id
            pay_obj.save()
            if_success = 1
            info = "修改成功"
        except:
            info = "修改失败：记录不存在"
        return JsonResponse({"if_success":if_success, "info":info})

@login_required
def update_payables_price(request):
    if request.method == "POST":
        if not request.user.has_perm("order_management.paya_manage"):
            return JsonResponse({"if_success":0, "info":"没有管理应付账款的权限"})
        pay_id = request.POST.get("pay_id")
        price = request.POST.get("price")
        if_success = 0
        info = ""
        try:
            pay_obj = PAYABLES.objects.get(id=pay_id)
            if pay_obj.invoice == None or pay_obj.invoice == "":
                #检查创建时间是否是上个月，如果不是就直接修改，否则递交申请给财务
                devider = datetime.datetime(datetime.date.today().year,datetime.date.today().month,1, tzinfo=pytz.timezone('Asia/Shanghai'))
                if pay_obj.create_time < devider:
                    EDIT_PRICE_REQUEST.objects.create(user=request.user.username, type="paya", target_id=pay_obj.id, target_price=price)
                    # 增加日志
                    order_obj = ORDER.objects.filter(id=pay_obj.order_id).first()
                    if order_obj == None:
                        detail = "申请更新应收款价格：发生错误"
                    else:
                        detail = "申请更新 " + order_obj.No + " 应付款价格：" + pay_obj.description + " 旧价格：" + str(
                            pay_obj.payables) + " 为新价格：" + str(price)
                    OPERATE_LOG.objects.create(user=request.user.username, field="应付账款", detail=detail)
                    if_success = 2
                    info = "由于分录创建时间为上个月，无法直接修改价格，已经向财务部分递交申请"
                else:
                    #增加日志
                    order_obj = ORDER.objects.filter(id=pay_obj.order_id).first()
                    if order_obj == None:
                        detail = "更新应收款价格：发生错误"
                    else:
                        detail = "更新 " + order_obj.No + " 应付款价格：" + pay_obj.description + " 旧价格：" + str(pay_obj.payables) + " 为新价格：" + str(price)
                    OPERATE_LOG.objects.create(user=request.user.username, field="应付账款", detail=detail)
                    pay_obj.payables = price
                    pay_obj.save()
                    if_success = 1
                    info = "修改成功"
            else:
                if_success = 0
                info = "已经开票的分录无法修改价格，请先清空发票信息"
        except:
            info = "修改失败：记录不存在"
        return JsonResponse({"if_success":if_success, "info":info})