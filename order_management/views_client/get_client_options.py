from django.http import JsonResponse
from order_management.models import CLIENT
from django.db.models import Q


def get_client_options(request):
    if request.method == "GET":
        query = request.GET.get("q","")
        if query == "":
            all_client = CLIENT.objects.all()
        else:
            all_client = CLIENT.objects.filter(
                (Q(type=0) & Q(co_name__contains=query)) | (Q(type=1) & Q(contact_name__contains=query)) | Q(
                    No__contains=query))
        data = []
        for line in all_client:
            if line.type==0: #公司客户
                data.append({"id":line.id,"text":line.No+" - "+line.co_name})
            elif  line.type==1: #个人客户
                data.append({"id":line.id,"text":line.No+" - "+line.contact_name})
        return JsonResponse({"data":data})