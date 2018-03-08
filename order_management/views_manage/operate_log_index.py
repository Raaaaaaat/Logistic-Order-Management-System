from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
import json, datetime
from django.db.models import Q
from order_management.models import OPERATE_LOG
from django.http import JsonResponse
from django.utils.timezone import localtime

@login_required
@permission_required('order_management.view_operate_log', login_url='/error?info=没有查看操作日志的权限，请联系管理员')
def operate_log_index(request):

    if request.method == "GET":
        info = request.GET.get('info', '')
        return render(request, 'manage/operate_log.html', {'info':info})
    elif request.method == "POST":
        bo_data = json.loads(request.body.decode())
        time_start = bo_data["time_start"]
        time_end   = bo_data["time_end"]
        user       = bo_data["user"]
        field      = bo_data["field"]
        detail     = bo_data["detail"]
        limit      = bo_data["limit"]
        offset     = bo_data["offset"]
        query = Q()
        if user != "":
            query = query & Q(user=user)
        if time_start != "":
            query = query & Q(time__gte=datetime.datetime.strptime(time_start, '%m/%d/%Y'))
        if time_end != "":
            query = query & Q(time__lte=datetime.datetime.strptime(time_end, '%m/%d/%Y') + datetime.timedelta(days=1))
        if field != "":
            query = query & Q(field=field)
        if detail != "":
            query = query & Q(detail__contains=detail)

        data = OPERATE_LOG.objects.filter(query).values()[offset:offset+limit]
        total = OPERATE_LOG.objects.filter(query).count()
        rows = []
        index = 1
        for line in data:
            line["time"] = datetime.datetime.strftime(localtime(line["time"]), '%Y-%m-%d %H:%M:%S')
            line["index"] = index
            index += 1
            rows.append(line)
        return JsonResponse({"rows":rows, "total":total})