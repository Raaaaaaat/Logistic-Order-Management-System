from django.shortcuts import render
from django.http import JsonResponse
import json
from order_management.models import ORDER
from order_management.models import CLIENT
from order_management.models import PAYABLES
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
import datetime,time
from django.utils.timezone import localtime


@login_required
@permission_required('order_management.view_trash_order', login_url='/error?info=没有查看废弃订单的权限，请联系管理员')
def get_order_dropped(request):

    if request.method == "GET":
        info = request.GET.get('info', '')
        return render(request, 'manage/trash_order.html', {'info':info})

    elif request.method == "POST":
        bo_data = json.loads(request.body.decode())
        #这里通过POST.get()不能获取数据，数据以字典的形式放在请求的body部分，所以只能手动解析body

        limit             = bo_data["limit"]
        offset            = bo_data["offset"]

        objs = ORDER.objects.filter(if_delete=1).values()[offset:offset+limit]
        total = ORDER.objects.filter(if_delete=1).count()
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
            if line['remark'] == None:
                line['remark'] = ""
            else:
                line['remark'] = line['remark'].replace("\r\n", "<br>")
            line["create_time"] = datetime.datetime.strftime(localtime(line["create_time"]), '%Y-%m-%d')
            if line["client_id"] in client_names:
                line["client_name"] = client_names[line["client_id"]]
            else:
                line["client_name"] = "已删除"
                line["client_id"] = 0
        #返回表格的数据
        data = {
            "total": total,
            "rows":  rows,
        }
        return JsonResponse(data)