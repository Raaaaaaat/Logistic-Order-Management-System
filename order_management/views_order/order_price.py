from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from order_management.models import ORDER
from order_management.models import RECEIVEABLES
from order_management.models import PAYABLES
from order_management.models import SUP_STEP
from order_management.models import SUPPLIER

def index_price(request):
    if request.method == "GET":
        No = request.GET.get('No', '')
        order_obj = get_object_or_404(ORDER, No=No)
        return render(request, "order/price.html", {
            "No": No,
            "order_id": order_obj.id,
        })

def get_receiveables(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        rec_obj = RECEIVEABLES.objects.filter(order_id=order_id).values()
        rows = []
        for line in rec_obj:
            rows.append(line)
        return JsonResponse({"rows":rows})

def add_receiveables(request):
    if request.method == "POST":
        #如果订单状态是5或者6则需要变更回来到4
        order_id = request.POST.get("order_id")
        order_obj = ORDER.objects.filter(id=order_id).first()
        if order_obj == None:
            if_success = 0
            info = "订单对象不存在"
        else:
            if order_obj.status != 4:
                order_obj.status=4
                order_obj.save()
            description = request.POST.get("description","")
            price = request.POST.get("price")
            RECEIVEABLES.objects.create(status=0, order_id=order_id,description=description,
                                    receiveables=price, received=0)
            if_success = 1
            info = "添加成功"
        return JsonResponse({"if_success":if_success, "info":info})

def delete_receiveables(request):
    if request.method == "POST":
        rec_id = request.POST.get("rec_id",0)
        #确定是否开票，如果是则不允许删除
        try:
            rec_obj = RECEIVEABLES.objects.get(id=rec_id)
            if rec_obj.invoice == None:
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

def update_receiveables_desc(request):
    if request.method == "POST":
        rec_id = request.POST.get("rec_id",0)
        desc = request.POST.get("desc","")
        if_success = 0
        info = ""
        try:
            rec_obj = RECEIVEABLES.objects.get(id=rec_id)
            rec_obj.description = desc
            rec_obj.save()
            if_success = 1
            info = "修改成功"
        except:
            info = "修改失败：记录不存在"
        return JsonResponse({"if_success":if_success, "info":info})

def update_receiveables_price(request):
    if request.method == "POST":
        rec_id = request.POST.get("rec_id")
        price = request.POST.get("price")
        if_success = 0
        info = ""
        try:
            rec_obj = RECEIVEABLES.objects.get(id=rec_id)
            if rec_obj.invoice == None:
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
def get_payables(request):
    if request.method == "POST":
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

def add_payables(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        step = request.POST.get("step")
        supplier_id = request.POST.get("supplier_id")
        description = request.POST.get("description")
        price = request.POST.get("price")
        PAYABLES.objects.create(status=0, order_id=order_id,description=description,
                                payables=price, paid_cash=0, paid_oil=0, step=step, supplier_id=supplier_id)
        return JsonResponse({"if_success":1, "info":"添加成功"})

def delete_payables(request):
    if request.method == "POST":
        pay_id = request.POST.get("pay_id",0)
        try:
            pay_obj = PAYABLES.objects.get(id=pay_id)
            if pay_obj.invoice == None or pay_obj.invoice=="":
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

def update_payables_info(request):
    if request.method == "POST":
        pay_id = request.POST.get("pay_id",0)
        desc = request.POST.get("desc","")
        supplier_id = request.POST.get("supplier_id")
        if_success = 0
        info = ""
        try:
            pay_obj = PAYABLES.objects.get(id=pay_id)
            pay_obj.description = desc
            pay_obj.supplier_id = supplier_id
            pay_obj.save()
            if_success = 1
            info = "修改成功"
        except:
            info = "修改失败：记录不存在"
        return JsonResponse({"if_success":if_success, "info":info})

def update_payables_price(request):
    if request.method == "POST":
        pay_id = request.POST.get("pay_id")
        price = request.POST.get("price")
        if_success = 0
        info = ""
        try:
            pay_obj = PAYABLES.objects.get(id=pay_id)
            if pay_obj.invoice == None or pay_obj.invoice == "":
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