from django.http import JsonResponse
from order_management.models import LOG_TRACE
import json,time, datetime
from django.utils.timezone import localtime

def get_trace_data(request):
    id = request.POST.get("id")
    objs = LOG_TRACE.objects.filter(order_id=id)
    rows = []
    for line in objs:
        rows.append({
            "trace_id":line.id,
            "status": line.status,
            "create_time": datetime.datetime.strftime(localtime(line.create_time), '%Y-%m-%d %H:%M:%S'),
            "desc": line.desc,
            "create_user": line.create_user,
        })
    return JsonResponse({
        "rows": rows,
    })