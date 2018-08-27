
from order_management.models import ORDER,RECEIVEABLES,PAYABLES
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


@login_required
def ope_trigger_close_order(request):
    if not request.user.has_perm("order_management.close_order"):
        if_success = 0
        info = "操作失败：没有关闭订单的权限，请联系管理员"
        return JsonResponse({'if_success': if_success, 'info': info})
    if request.method=="POST":
        order_No = request.POST.get("No")
        if_success = 1
        info = ""
        order_obj = ORDER.objects.get(No=order_No)
        if order_obj.if_close==1: #要进行开账
            if not request.user.has_perm("order_management.open_order"):
                if_success = 0
                info = "操作失败：没有重新打开订单的权限，请联系管理员"
                return JsonResponse({'if_success': if_success, 'info': info})
            order_obj.if_close=0
            #PAYABLES.objects.filter(order_id=order_obj.id).update(if_close=0)
            #RECEIVEABLES.objects.filter(order_id=order_obj.id).update(if_close=0)
            info = "已将"+order_No+"重新打开"
        else:

            #进行检查，需要同时设置应收以及应付  才可进行关账
            pass_flag = True
            recv_num = RECEIVEABLES.objects.filter(order_id=order_obj.id).count()
            if recv_num==0:
                pass_flag = False
                info = "不能关闭该订单：未设置应收款"
                if_success = 0
            paya_num = PAYABLES.objects.filter(order_id=order_obj.id).count()
            if paya_num==0:
                pass_flag = False
                info = "不能关闭该订单：未设置应付款"
                if_success = 0

            if order_obj.status<4: #签收之前不能关闭
                pass_flag = False
                info = "必须在订单签收之后才可进行关闭订单的操作"
                if_success = 0
            if pass_flag:
                order_obj.if_close=1
                if_success = 1
                #PAYABLES.objects.filter(order_id=order_obj.id).update(if_close=1)
                #RECEIVEABLES.objects.filter(order_id=order_obj.id).update(if_close=1)
                info = "已将"+order_No+"关闭"
        order_obj.save()

        return JsonResponse({'if_success':if_success, 'info': info})

