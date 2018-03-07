
from django.http import JsonResponse
from order_management.models import LOG_TRACE

def ope_edit_trace(request):
    if request.method=="POST":
        # 权限检查:
        if not request.user.has_perm("order_management.change_log_trace"):
            if_success = 0
            info = "操作失败：没有进行此操作的权限"
            return JsonResponse({'if_success': if_success, 'info': info})

        trace_id = request.POST.get("trace_id")
        desc  = request.POST.get("desc")

        trace_obj = LOG_TRACE.objects.get(id=trace_id)
        trace_obj.desc = desc
        trace_obj.save()
        return JsonResponse({'if_success': 1, 'info': "suc"})

