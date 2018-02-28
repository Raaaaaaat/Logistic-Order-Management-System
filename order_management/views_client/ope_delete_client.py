from django.http import JsonResponse
from order_management.models import CLIENT

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

@login_required
def ope_delete_client(request):
    if_success = 0
    if not request.user.has_perm("order_management.delete_client"):
        if_success = 0
        info = "操作失败：没有进行此操作的权限"
    else:
        No = request.POST.get("No","")

        if No == "":
            if_success = 0
            info = "操作失败：参数错误"
        else:
            try:
                CLIENT.objects.get(No=No).delete()
                if_success = 1
                info=""
            except:
                if_success = 0
                info = "删除操作失败"

    return JsonResponse({'if_success':if_success, 'info':info})