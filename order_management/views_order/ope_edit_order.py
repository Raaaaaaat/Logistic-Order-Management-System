from django.shortcuts import redirect
import json,time, datetime
from order_management.models import ORDER
from order_management.models import ORDER_SUP_ALLO

def ope_edit_order(request):



    if request.method=="POST":
        client_id = request.POST.get("client_id")
        dep_city  = request.POST.get("dep_city")
        dep_place = request.POST.get("dep_place")
        des_city  = request.POST.get("des_city")
        des_place = request.POST.get("des_place")
        cargo_name     = request.POST.get("cargo_name")
        cargo_weight   = request.POST.get("cargo_weight")
        cargo_quantity = request.POST.get("cargo_quantity")
        note           = request.POST.get("note")
        supplier_allo  = request.POST.get("supplier_allo")
        supplier_allo  = json.loads(supplier_allo)
        rec_name       = request.POST.get("rec_name", "")
        rec_tel        = request.POST.get("rec_tel", "")
        if_edit        = request.POST.get("if_edit")

        if if_edit=="0": #添加模式
            No = ""  # 自动生成下一个该有的客户编号
            last_one = ORDER.objects.last()
            currentMonth = time.strftime("%Y%m", time.localtime())

            if last_one != None:  # 说明之前已经有记录
                if last_one.No[2:8]==currentMonth:
                    No = last_one.No[8:]
                    No = int(No) + 1
                    No = "PO" + currentMonth + str(No).zfill(3)
                else:
                    No = "PO" + currentMonth + "001"
            else:
                No = "PO" + currentMonth + "001"
            obj = ORDER.objects.create(No=No, status=1, client_id=client_id,
                                 dep_city=dep_city, dep_place=dep_place,
                                 des_city=des_city, des_place=des_place,
                                 cargo_name=cargo_name, cargo_weight=cargo_weight,
                                 cargo_quantity=cargo_quantity, if_delete=0,
                                 note=note, rec_name=rec_name, rec_tel=rec_tel)
            id = obj.id
            #下面对于供应商分配方案进行添加
            for line in supplier_allo:
                operation = line['operation']
                price = line['price']
                supplier_id = line['supplier']
                ORDER_SUP_ALLO.objects.create(status=0, order_id=id,
                                              operation=operation, supplier_id=supplier_id)
            info = "添加成功"
        return redirect('/order?info=' + info)

