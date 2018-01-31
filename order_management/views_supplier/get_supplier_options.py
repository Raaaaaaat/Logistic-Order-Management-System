from django.http import JsonResponse
from order_management.models import SUPPLIER
from django.db.models import Q


def get_supplier_options(request):
    if request.method == "GET":
        query = request.GET.get("q","")
        if query == "":
            all_supplier = SUPPLIER.objects.all()
        else:
            all_supplier = SUPPLIER.objects.filter(
                (Q(type=0) & Q(co_name__contains=query)) | (Q(type=1) & Q(contact_name__contains=query)) | Q(
                    No__contains=query))
        data = []
        for line in all_supplier:
            if line.type==0: #公司供应商
                data.append({"id":line.id,"text":line.No+" - "+line.co_name})
            elif  line.type==1: #个人供应商
                data.append({"id":line.id,"text":line.No+" - "+line.contact_name})
        return JsonResponse({"data":data})