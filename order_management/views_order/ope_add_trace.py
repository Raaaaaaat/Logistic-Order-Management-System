from django.shortcuts import redirect, get_object_or_404
import json,time, datetime
from django.http import JsonResponse
from order_management.models import LOG_TRACE
from order_management.models import ORDER
from django.contrib.auth.decorators import login_required

@login_required
def ope_add_trace(request):
    if request.method=="POST":
        #权限检查:
        if not request.user.has_perm("order_management.add_log_trace"):
            if_success = 0
            info = "操作失败：没有进行此操作的权限"
            return JsonResponse({'if_success': if_success, 'info': info})

        order_id = request.POST.get("order_id","")
        try:
            order_obj = ORDER.objects.get(id=order_id)
        except (ORDER.DoesNotExist, ValueError):
            return JsonResponse({'success':0, 'info': "添加失败：订单不存在"})

        current_order_status = order_obj.status

        # 订单状态1-6分别对应的6个状态
        #未发货
        #已提货
        #在途中
        #已签收
        #已出票
        #已收款
        status  = request.POST.get("status")
        create_time    = request.POST.get("create_time")
        select_time    = request.POST.get("select_time")
        desc    = request.POST.get("desc","")
        create_time    = datetime.datetime.strptime(create_time,'%Y-%m-%d %H:%M:%S')
        select_time    = datetime.datetime.strptime(select_time, '%m/%d/%Y')

        if_success = 0
        if_update_status = False
        info       = ""
        if (status == "提货"):
            if current_order_status == 1:
                if_success = 1
                order_obj.pick_up_time=select_time
                order_obj.save()
                if_update_status = True
            else:
                info = "添加失败：对于’未提货‘的订单才能进行提货操作"
        elif (status == "出发"):
            if current_order_status == 2 or current_order_status == 3:
                if_success = 1
                if current_order_status == 2: #如果是已经在途中的状态，则不需要对于订单状态进行重复更新
                    if_update_status = True
            else:
                info = "添加失败：货物不能在此时出发"
        elif (status == "途径"):
            if current_order_status == 3:
                if_success = 1
            else:
                info = "添加失败：对于‘在途中’的订单才可添加途径信息"
        elif (status == "到达"):
            if current_order_status == 3:
                if_success = 1
            else:
                info = "添加失败：对于‘在途中’的订单才可添加途径信息"
        elif (status == "签收"):
            if current_order_status == 3:
                #这里要进行判断，如果所有出发的车辆都已经到达目的地，则可以确定签收
                count_dep = 0 #分别对于出发的数量以及到达的数量进行签收
                count_arr = 0
                trace_objs = LOG_TRACE.objects.filter(order_id=order_id)
                for single_obj in trace_objs:
                    if single_obj.status=="出发":
                        count_dep += 1
                    elif single_obj.status == "到达":
                        count_arr += 1
                if count_arr == count_dep:
                    if_update_status = True
                    if_success = 1
                    order_obj.delivery_time = select_time
                    order_obj.save()
                else:
                    info = "添加失败：只有当所有车辆都已到达目的地才可确定签收"
            else:
                info = "添加失败：对于‘在途中’的订单才可确认签收"
        elif (status == "异常"):
            if_success = 1
        else:
            info = "添加失败：参数错误"

        t_id = ""
        if if_success==1:
            obj = LOG_TRACE.objects.create(
                order_id=order_id, status=status,
                create_time=create_time, desc=desc,
                create_user= request.user.username,
                select_time=select_time,
            )
            t_id = obj.id
            if if_update_status:    #可以对于订单状态进行更新
                order_obj.status = order_obj.status + 1
                order_obj.save()
            info = "添加成功"


        return JsonResponse({'if_success':if_success, 'info': info, 'order_status':order_obj.status, 'trace_id': t_id})

