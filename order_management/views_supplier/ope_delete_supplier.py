from django.http import JsonResponse
from order_management.models import SUPPLIER

from django.contrib.auth.decorators import login_required


@login_required
def ope_delete_supplier(request):
    if_success = 0
    if not request.user.has_perm("order_management.delete_supplier"):
        if_success = 0
        info = "操作失败：没有进行此操作的权限"
    else:
        No = request.POST.get("No", "")

        if No == "":
            if_success = 0
            info = "操作失败：参数错误"
        else:
            try:
                SUPPLIER.objects.get(No=No).delete()
                if_success = 1
                info = ""
            except:
                if_success = 0
                info = "删除操作失败"

    return JsonResponse({'if_success': if_success, 'info': info})