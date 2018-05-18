from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
import datetime
from order_management.models import RECEIVEABLES
from order_management.models import PAYABLES
from order_management.models import ORDER
from order_management.models import CLIENT
from order_management.models import SUPPLIER
from django.db.models import Sum
import pytz

@login_required
@permission_required('order_management.view_data_center', login_url='/error?info=没有查看数据中心的权限，请联系管理员')
def graph_supplier(request):
#这个页面是供应商数据透视图的默认界面
    if request.method == "GET":
        return render(request, 'graph/supplier_graph.html')


def graph_supplier_getbycost(request):
    if request.method == "POST":
        start_t = request.POST.get("start_t")
        end_t = request.POST.get("end_t")
        try:
            start_t = datetime.datetime.strptime(start_t, '%m/%d/%Y')
            end_t = datetime.datetime.strptime(end_t, '%m/%d/%Y')
        except:
            return JsonResponse({"if_success": 0, "info": "时间选择错误"})
        data= PAYABLES.objects.filter(create_time__lte=end_t, create_time__gte=start_t).values("supplier_id", "payables", "paid_oil", "paid_cash")


        #累加获得各个客户对应的总额
        supplier_objs = SUPPLIER.objects.all()
        supplier_list={}
        for line in supplier_objs:
            if line.type==0:
                supplier_list[line.id] = {"name":line.co_name, "payables":0.0, "paid_oil":0.0, "paid_cash":0.0}
            if line.type==1:
                supplier_list[line.id] = {"name":line.contact_name, "payables":0.0, "paid_oil":0.0, "paid_cash":0.0}

        for line in data:
            supplier_id = line["supplier_id"]
            supplier_list[supplier_id]["payables"] += line["payables"]
            supplier_list[supplier_id]["paid_oil"] += line["paid_oil"]
            supplier_list[supplier_id]["paid_cash"] += line["paid_cash"]

        rows = []
        for key in supplier_list:
            if supplier_list[key]["payables"]>0:
                rows.append(supplier_list[key])
        rows.sort(key=lambda x : x["payables"], reverse=True)

        ret_names = []
        ret_paya  = []
        ret_oil   = []
        ret_cash  = []
        for line in rows:
            ret_names.append(line["name"])
            ret_paya.append(round(line["payables"],2))
            ret_oil.append(round(line["paid_oil"],2))
            ret_cash.append(round(line["paid_cash"], 2))
        return  JsonResponse({"if_success":1, "data":{"names":ret_names, "paya":ret_paya, "oil":ret_oil, "cash":ret_cash}})


def graph_supplier_getbycardrate(request):
    if request.method == "POST":
        start_t = request.POST.get("start_t")
        end_t = request.POST.get("end_t")
        try:
            start_t = datetime.datetime.strptime(start_t, '%m/%d/%Y')
            end_t = datetime.datetime.strptime(end_t, '%m/%d/%Y')
        except:
            return JsonResponse({"if_success": 0, "info": "时间选择错误"})
        data= PAYABLES.objects.filter(create_time__lte=end_t, create_time__gte=start_t).values("supplier_id", "payables", "paid_oil", "paid_cash")


        #累加获得各个客户对应的总额
        supplier_objs = SUPPLIER.objects.all()
        supplier_list={}
        for line in supplier_objs:
            if line.type==0:
                supplier_list[line.id] = {"name":line.co_name, "paid_oil":0.0, "paid_cash":0.0, "rate":0.0}
            if line.type==1:
                supplier_list[line.id] = {"name":line.contact_name, "paid_oil":0.0, "paid_cash":0.0, "rate":0.0}

        for line in data:
            supplier_id = line["supplier_id"]
            supplier_list[supplier_id]["paid_oil"] += line["paid_oil"]
            supplier_list[supplier_id]["paid_cash"] += line["paid_cash"]

        rows = []
        for key in supplier_list:
            if supplier_list[key]["paid_oil"]>0 or supplier_list[key]["paid_cash"]>0:
                supplier_list[key]["rate"] = supplier_list[key]["paid_oil"] / (supplier_list[key]["paid_oil"] + supplier_list[key]["paid_cash"]) * 100
                rows.append(supplier_list[key])
        rows.sort(key=lambda x : x["rate"], reverse=True)

        ret_names = []
        ret_rate  = []
        for line in rows:
            ret_names.append(line["name"])
            ret_rate.append(round(line["rate"],4))
        return  JsonResponse({"if_success":1, "data":{"names":ret_names, "rate":ret_rate}})


def graph_supplier_getbytime(request):
    if request.method == "POST":
        supplier_id = request.POST.get("supplier_id")
        year = request.POST.get("year")

        #找出所有符合的收入
        start_time = datetime.datetime.strptime(year,"%Y")
        end_time = datetime.datetime.strptime(str(int(year)+1), "%Y")
        paya_objs = PAYABLES.objects.filter(supplier_id=supplier_id,create_time__gte=start_time,create_time__lt=end_time)

        #计算以下内容随时间的变化：应付，已付油卡，已付现金


        data_payables     = [0,0,0,0,0,0,0,0,0,0,0,0]
        data_paid_oil         = [0,0,0,0,0,0,0,0,0,0,0,0]
        data_paid_cash = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        base_2 = start_time = datetime.datetime.strptime(year + "02+0800", "%Y%m%z")
        base_3 = start_time = datetime.datetime.strptime(year + "03+0800", "%Y%m%z")
        base_4 = start_time = datetime.datetime.strptime(year + "04+0800", "%Y%m%z")
        base_5 = start_time = datetime.datetime.strptime(year + "05+0800", "%Y%m%z")
        base_6 = start_time = datetime.datetime.strptime(year + "06+0800", "%Y%m%z")
        base_7 = start_time = datetime.datetime.strptime(year + "07+0800", "%Y%m%z")
        base_8 = start_time = datetime.datetime.strptime(year + "08+0800", "%Y%m%z")
        base_9 = start_time = datetime.datetime.strptime(year + "09+0800", "%Y%m%z")
        base_10 = start_time = datetime.datetime.strptime(year+ "10+0800", "%Y%m%z")
        base_11 = start_time = datetime.datetime.strptime(year+ "11+0800", "%Y%m%z")
        base_12 = start_time = datetime.datetime.strptime(year + "12+0800", "%Y%m%z")

        for line in paya_objs:
            time=line.create_time
            if time<base_2:
                index = 0
            elif time<base_3:
                index = 1
            elif time<base_4:
                index = 2
            elif time<base_5:
                index = 3
            elif time<base_6:
                index = 4
            elif time<base_7:
                index = 5
            elif time<base_8:
                index = 6
            elif time<base_9:
                index = 7
            elif time<base_10:
                index = 8
            elif time<base_11:
                index = 9
            elif time<base_12:
                index = 10
            else:
                index = 11
            data_payables[index]  += line.payables
            data_paid_oil[index] += line.paid_oil
            data_paid_cash[index] += line.paid_cash

        for index in range(12):
            data_paid_oil[index]     = round(data_paid_oil[index],     2)
            data_payables[index]     = round(data_payables[index],     2)
            data_paid_cash[index]    = round(data_paid_cash[index],    2)

        return  JsonResponse({"if_success":1, "data":{"payables":data_payables,
                                                      "paid_oil":data_paid_oil,
                                                      "paid_cash":data_paid_cash}})