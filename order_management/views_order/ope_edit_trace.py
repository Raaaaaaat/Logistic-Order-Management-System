
from django.http import JsonResponse
from order_management.models import LOG_TRACE

def ope_edit_trace(request):
    if request.method=="POST":
        trace_id = request.POST.get("trace_id")
        desc  = request.POST.get("desc")

        trace_obj = LOG_TRACE.objects.get(id=trace_id)
        trace_obj.desc = desc
        trace_obj.save()
        return JsonResponse({'info': "suc"})

