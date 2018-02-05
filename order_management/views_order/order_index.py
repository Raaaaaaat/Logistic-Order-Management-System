from django.shortcuts import render
from django.http import JsonResponse
import json
from order_management.models import ORDER
from order_management.models import CLIENT
from order_management.models import ORDER_SUP_ALLO
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
import datetime,time

def order_index(request):

    if request.method == "GET":
        info = request.GET.get('info', '')
        return render(request, 'order/index.html', {'info':info})

    elif request.method == "POST":
        bo_data = json.loads(request.body.decode())
        #这里通过POST.get()不能获取数据，数据以字典的形式放在请求的body部分，所以只能手动解析body
        filter_No         = bo_data["filter_No"];
        filter_client     = bo_data["filter_client"];
        filter_supplier   = bo_data["filter_supplier"];
        filter_dep_city   = bo_data["filter_dep_city"];
        filter_des_city   = bo_data["filter_des_city"];
        filter_pay_status = bo_data["filter_pay_status"];
        filter_status     = json.loads(bo_data["filter_status"]);
        filter_start_time = bo_data["filter_start_time"];
        filter_end_time   = bo_data["filter_end_time"];
        limit             = bo_data["limit"];
        offset            = bo_data["offset"];
        for i in range(len(filter_status)):
            filter_status[i] = int(filter_status[i])

        query = Q()
        if filter_No != "":
            query = query & Q(No__contains=filter_No)
        if filter_client != "":
            query = query & Q(client_id=filter_client)
        if filter_start_time != "":
            query = query & Q(create_time__gte=datetime.datetime.strptime(filter_start_time,'%m/%d/%Y'))
        if filter_end_time != "":
            query = query & Q(create_time__lte=datetime.datetime.strptime(filter_end_time,'%m/%d/%Y'))
        if filter_dep_city != "":
            query = query & Q(dep_city=filter_dep_city)
        if filter_des_city != "":
            query = query & Q(des_city=filter_des_city)
        if len(filter_status) != 0:
            query = query & Q(status__in=filter_status)
        if filter_pay_status != "":
            order_ids = ORDER_SUP_ALLO.objects.filter(status=int(filter_pay_status))
            order_ids = order_ids.values_list("order_id", flat=True).distinct()
            temp = []       #循环将对象从queryset变成list对象
            for line in order_ids:
                temp.append(line)
            order_ids = temp
            query = query & Q(id__in=order_ids)
        if filter_supplier != "":
            order_ids = ORDER_SUP_ALLO.objects.filter(supplier_id=int(filter_supplier))
            order_ids = order_ids.values_list("order_id", flat=True).distinct()
            temp = []       #循环将对象从queryset变成list对象
            for line in order_ids:
                temp.append(line)
            order_ids = temp
            query = query & Q(id__in=order_ids)

        objs = ORDER.objects.filter(query).values()[offset:offset+limit]
        total = objs.count()
        rows = []  # 这里从数据库取回来的初始数据不是列表，而是ｑｕｅｒｙｓｅｔ，所以这里领建立一个列表ｒｏｗｓ然后重新过一遍数据，转存一下
        client_ids = []
        for line in objs:
            rows.append(line)
            #获取需要获得的客户信息的id set
            client_ids.append(line["client_id"])
        client_ids = list(set(client_ids))
        client_objs = CLIENT.objects.filter(id__in=client_ids)
        client_names = {}
        for line in client_objs:
            if line.type==0: #公司客户
                client_names[line.id] = line.co_name
            elif line.type==1:
                client_names[line.id] = line.contact_name
        for line in rows:
            line["client_name"] = client_names[line["client_id"]]
        #返回表格的数据
        data = {
            "total": total,
            "rows":  rows,
        }
        return JsonResponse(data)