
from django.http import JsonResponse
from order_management.models import LOG_TRACE, ORDER
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
import datetime

@login_required
def ope_edit_trace(request):
    if request.method=="POST":
        # 权限检查:
        if not request.user.has_perm("order_management.change_log_trace"):
            if_success = 0
            info = "操作失败：没有进行此操作的权限"
            return JsonResponse({'if_success': if_success, 'info': info})

        trace_id = request.POST.get("trace_id")
        desc  = request.POST.get("desc")
        date = request.POST.get("date")
        date = datetime.datetime.strptime(date, '%m/%d/%Y')

        trace_obj = LOG_TRACE.objects.get(id=trace_id)
        if trace_obj.status == "提货":
            order_obj = ORDER.objects.filter(id=trace_obj.order_id).first()
            if order_obj != None:
                order_obj.pick_up_time = date
                order_obj.save()
        elif trace_obj.status == "签收":
            order_obj = ORDER.objects.filter(id=trace_obj.order_id).first()
            if order_obj != None:
                order_obj.delivery_time = date
                order_obj.save()
        trace_obj.desc = desc
        trace_obj.select_time = date
        trace_obj.save()
        return JsonResponse({'if_success': 1, 'info': "suc"})

