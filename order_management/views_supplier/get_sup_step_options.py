from django.http import JsonResponse
from order_management.models import SUP_STEP
from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required
def get_sup_step_options(request):
    if request.method == "GET":
        step_objs = SUP_STEP.objects.all()
        data = []
        for line in step_objs:
            data.append({"id":line.id,"text":line.name})
        return JsonResponse({"data":data})