from django.http import JsonResponse
from order_management.models import SUP_OP
from django.db.models import Q


def get_sup_ope_options(request):
    if request.method == "GET":
        all_client = SUP_OP.objects.all()
        data = []
        for line in all_client:
            data.append({"id":line.id,"text":line.name})
        return JsonResponse({"data":data})