from django.http import JsonResponse
from order_management.models import CLIENT

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

@login_required
def ope_delete_client(request):
    ret = 0
    if not request.user.has_perm("order_management.delete_client"):
        ret = 2
    else:
        No = request.POST.get("No","")

        if No == "":
            ret = 0
        else:
            CLIENT.objects.get(No=No).delete()
            ret = 1

    return JsonResponse({'info':ret})