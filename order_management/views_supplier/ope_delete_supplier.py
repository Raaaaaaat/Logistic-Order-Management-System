from django.http import JsonResponse
from order_management.models import SUPPLIER

from django.contrib.auth.decorators import login_required


@login_required
def ope_delete_supplier(request):
    ret = 0
    if not request.user.has_perm("order_management.delete_supplier"):
        ret = 2
    else:
        No = request.POST.get("No","")

        if No == "":
            ret = 0
        else:
            SUPPLIER.objects.get(No=No).delete()
            ret = 1

    return JsonResponse({'info':ret})