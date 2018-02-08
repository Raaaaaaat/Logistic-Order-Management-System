from django.shortcuts import redirect
import json,time, datetime
from django.http import JsonResponse
from order_management.models import LOG_TRACE

def ope_add_trace(request):
    if request.method=="POST":
        id = request.POST.get("id")
        status  = request.POST.get("status")
        time = request.POST.get("time")
        desc  = request.POST.get("desc")
        time = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
        LOG_TRACE.objects.create(
            order_id=id, status=status,
            time=time, desc=desc
        )

        return JsonResponse({'info': "suc"})

