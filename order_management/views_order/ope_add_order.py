from django.shortcuts import redirect
import json,time, datetime
from order_management.models import ORDER, CLIENT
from order_management.models import PAYABLES

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


@login_required
@permission_required('order_management.add_order', login_url='/error?info=没有添加订单的权限，请联系管理员')
def ope_add_order(request):
    if request.method=="POST":
        client_id = request.POST.get("client_id")
        dep_city  = request.POST.get("dep_city")
        dep_place = request.POST.get("dep_place")
        des_city  = request.POST.get("des_city")
        des_place = request.POST.get("des_place")
        cargo_name     = request.POST.get("cargo_name")
        cargo_weight   = request.POST.get("cargo_weight")
        cargo_quantity = request.POST.get("cargo_quantity")
        cargo_size     = request.POST.get("cargo_size")
        remark         = request.POST.get("remark")
        rec_name       = request.POST.get("rec_name", "")
        rec_tel        = request.POST.get("rec_tel", "")
        if_edit        = request.POST.get("if_edit")

        #检查是否在有效期内：
        client_obj = CLIENT.objects.filter(id=client_id).first()
        if client_obj==None:
            return redirect('/order?info=所选择的客户不存在')
        else:
            start_time = client_obj.contract_start
            end_time = client_obj.contract_end
            now = datetime.datetime.now()
            if start_time!="":
                start_time = datetime.datetime.strptime(start_time, "%m/%d/%Y")
                if now < start_time:
                    return redirect('/order?info=所选择的客户未到合同有效期')

            if end_time!="":
                end_time = datetime.datetime.strptime(end_time, "%m/%d/%Y")+datetime.timedelta(days=1)
                if now > end_time:
                    return redirect('/order?info=所选择的客户已过合同有效期')


        if if_edit=="0": #添加模式
            # 自动生成下一个该有的客户编号
            last_one = ORDER.objects.first()
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
                                 cargo_quantity=cargo_quantity, if_delete=0,cargo_size=cargo_size,
                                 remark=remark, rec_name=rec_name, rec_tel=rec_tel)

            info = "添加成功"
        return redirect('/price_management?No=' + No+"&info="+info)

