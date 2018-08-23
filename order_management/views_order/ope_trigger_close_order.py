
from order_management.models import ORDER,RECEIVEABLES,PAYABLES
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


@login_required
def ope_trigger_close_order(request):
    if not request.user.has_perm("order_management.close_order"):
        if_success = 0
        info = "操作失败：没有关账的权限，请联系管理员"
        return JsonResponse({'if_success': if_success, 'info': info})
    if request.method=="POST":
        order_No = request.POST.get("No")
        if_success = 1
        info = ""
        order_obj = ORDER.objects.get(No=order_No)
        if order_obj.if_close==1: #要进行开账
            order_obj.if_close=0
            PAYABLES.objects.filter(order_id=order_obj.id).update(if_close=0)
            RECEIVEABLES.objects.filter(order_id=order_obj.id).update(if_close=0)
            info = "已对"+order_No+"进行开账"
        else:
            #进行检查，需要同时设置应收以及应付 并且全部结清 才可进行关账
            pass_flag = True
            recv_check = False #标记是否有应付款
            recv_objs = RECEIVEABLES.objects.filter(order_id=order_obj.id)
            for single in recv_objs:
                recv_check = True
                if single.clear_time==None:
                    pass_flag = False
                    info = "不能关账：尚有应收账款未结清"
                    if_success = 0
            if not recv_check:
                pass_flag = False
                info = "不能关账：未设置应收款"
                if_success = 0

            paya_check = False  # 标记是否有应付款
            paya_objs = PAYABLES.objects.filter(order_id=order_obj.id)
            for single in paya_objs:
                paya_check = True
                if single.clear_time == None:
                    pass_flag = False
                    info = "不能关账：尚有应付账款未结清"
                    if_success = 0
            if not paya_check:
                pass_flag = False
                info = "不能关账：未设置应付款"
                if_success = 0

            if pass_flag:
                order_obj.if_close=1
                PAYABLES.objects.filter(order_id=order_obj.id).update(if_close=1)
                RECEIVEABLES.objects.filter(order_id=order_obj.id).update(if_close=1)
                info = "已对"+order_No+"进行关账"
        order_obj.save()

        return JsonResponse({'if_success':if_success, 'info': info})

