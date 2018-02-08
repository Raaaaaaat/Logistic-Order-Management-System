from django.http import JsonResponse
from order_management.models import LOG_TRACE
import json,time, datetime

def get_trace_data(request):
    id = request.POST.get("id")
    objs = LOG_TRACE.objects.filter(order_id=id)
    rows = []
    for line in objs:
        rows.append({
            "status": line.status,
            "time": datetime.datetime.strftime(line.time, '%Y-%m-%d %H:%M:%S'),
            "desc": line.desc,
        })
    return JsonResponse({
        "rows": rows,
    });