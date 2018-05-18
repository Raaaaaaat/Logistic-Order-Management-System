from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
import datetime
from order_management.models import RECEIVEABLES
from order_management.models import PAYABLES
from order_management.models import ORDER
from order_management.models import CLIENT
from django.db.models import Sum
import pytz

@login_required
@permission_required('order_management.view_data_center', login_url='/error?info=没有查看数据中心的权限，请联系管理员')
def graph_client(request):
#这个页面是客户数据透视图的默认界面
    if request.method == "GET":
        return render(request, 'graph/client_graph.html')

def graph_client_getbyincome(request):
    if request.method == "POST":
        start_t = request.POST.get("start_t")
        end_t = request.POST.get("end_t")
        try:
            start_t = datetime.datetime.strptime(start_t, '%m/%d/%Y')
            end_t = datetime.datetime.strptime(end_t, '%m/%d/%Y')
        except:
            return JsonResponse({"if_success": 0, "info": "时间选择错误"})
        data= RECEIVEABLES.objects.filter(create_time__lte=end_t, create_time__gte=start_t).values("order_id", "receiveables", "received")

        #找出order对应的client
        order_objs = ORDER.objects.all().values("client_id", "id")
        order_dic={}
        for line in order_objs:
            order_dic[line["id"]]=line["client_id"]

        #累加获得各个客户对应的总额
        client_objs = CLIENT.objects.all()
        client_list={}
        for line in client_objs:
            if line.type==0:
                client_list[line.id] = {"name":line.co_name, "receiveables":0.0, "received":0.0}
            if line.type==1:
                client_list[line.id] = {"name":line.contact_name, "receiveables":0.0, "received":0.0}

        for line in data:
            client_id = order_dic[line["order_id"]]
            client_list[client_id]["receiveables"] += line["receiveables"]
            client_list[client_id]["received"] += line["received"]

        rows = []
        for key in client_list:
            if client_list[key]["receiveables"]>0:
                rows.append(client_list[key])
        rows.sort(key=lambda x : x["receiveables"], reverse=True)

        ret_names = []
        ret_recv = []
        ret_recd = []
        for line in rows:
            ret_names.append(line["name"])
            ret_recv.append(round(line["receiveables"],2))
            ret_recd.append(round(line["received"],2))
        return  JsonResponse({"if_success":1, "data":{"names":ret_names, "receiveables":ret_recv, "received":ret_recd}})


def graph_client_getbypincome(request):
    if request.method == "POST":
        start_t = request.POST.get("start_t")
        end_t = request.POST.get("end_t")
        try:
            start_t = datetime.datetime.strptime(start_t, '%m/%d/%Y')
            end_t = datetime.datetime.strptime(end_t, '%m/%d/%Y')
        except:
            return JsonResponse({"if_success": 0, "info": "时间选择错误"})
        income_data= RECEIVEABLES.objects.filter(create_time__lte=end_t, create_time__gte=start_t).values("order_id", "receiveables")
        cost_data = PAYABLES.objects.filter(create_time__lte=end_t, create_time__gte=start_t).values("order_id", "payables")
        #找出order对应的client
        order_objs = ORDER.objects.all().values("client_id", "id")
        order_dic={}
        for line in order_objs:
            order_dic[line["id"]]=line["client_id"]

        #累加获得各个客户对应的总额
        client_objs = CLIENT.objects.all()
        client_list={}
        for line in client_objs:
            if line.type==0:
                client_list[line.id] = {"name":line.co_name, "receiveables":0.0, "payables":0.0}
            if line.type==1:
                client_list[line.id] = {"name":line.contact_name, "receiveables":0.0, "payables":0.0}

        for line in income_data:
            client_id = order_dic[line["order_id"]]
            client_list[client_id]["receiveables"] += line["receiveables"]

        for line in cost_data:
            client_id = order_dic[line["order_id"]]
            client_list[client_id]["payables"] += line["payables"]

        rows = []
        for key in client_list:
            pincome = round(client_list[key]["receiveables"]-client_list[key]["payables"], 2)
            if pincome != 0:
                rows.append({"name":client_list[key]["name"], "pincome":pincome})
        rows.sort(key=lambda x : x["pincome"], reverse=True)

        ret_names = []
        ret_pinc = []
        for line in rows:
            ret_names.append(line["name"])
            ret_pinc.append(line["pincome"])
        return  JsonResponse({"if_success":1, "data":{"names":ret_names, "pincome":ret_pinc}})

def graph_client_getbytime(request):
    if request.method == "POST":
        client_id = request.POST.get("client_id")
        year = request.POST.get("year")

        #找出这个客户的所有order_id
        order_ids = ORDER.objects.filter(client_id=client_id).values("id")
        t_a = []
        for line in order_ids:
            t_a.append(line["id"])
        #找出所有符合orderid的收入
        start_time = datetime.datetime.strptime(year,"%Y")
        end_time = datetime.datetime.strptime(str(int(year)+1), "%Y")
        recv_objs = RECEIVEABLES.objects.filter(order_id__in=order_ids,create_time__gte=start_time,create_time__lt=end_time)
        #找出所有符合orderid的成本
        paya_objs = PAYABLES.objects.filter(order_id__in=order_ids,create_time__gte=start_time,create_time__lt=end_time)
        #计算以下内容随时间的变化：应收，已收，应付，已付油卡，已付现金，利润

        data_receiveables = [0,0,0,0,0,0,0,0,0,0,0,0]
        data_received     = [0,0,0,0,0,0,0,0,0,0,0,0]
        data_payables     = [0,0,0,0,0,0,0,0,0,0,0,0]
        data_paid         = [0,0,0,0,0,0,0,0,0,0,0,0]
        data_pincome      = [0,0,0,0,0,0,0,0,0,0,0,0]

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

        for line in recv_objs:
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
            data_receiveables[index] += line.receiveables
            data_received[index] += line.received

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
            data_paid[index] += line.paid_cash + line.paid_oil

        for index in range(12):
            data_pincome[index] = round(data_receiveables[index] - data_payables[index],2)
            data_receiveables[index] = round(data_receiveables[index], 2)
            data_received[index]     = round(data_received[index],     2)
            data_payables[index]     = round(data_payables[index],     2)
            data_paid[index]         = round(data_paid[index],         2)

        return  JsonResponse({"if_success":1, "data":{"receiveables":data_receiveables,
                                                      "received":data_received,
                                                      "payables":data_payables,
                                                      "paid":data_paid,
                                                      "pincome":data_pincome}})