from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from order_management.models import ORDER
from order_management.models import RECEIVEABLES

def index_price(request):
    if request.method == "GET":
        No = request.GET.get('No', '')
        order_obj = get_object_or_404(ORDER, No=No)
        return render(request, "order/price.html", {
            "No": No,
            "order_id": order_obj.id,
        })

def get_receiveables(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        rec_obj = RECEIVEABLES.objects.filter(order_id=order_id).values()
        rows = []
        for line in rec_obj:
            rows.append(line)
        return JsonResponse({"rows":rows})

def add_receiveables(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        description = request.POST.get("description")
        price = request.POST.get("price")
        RECEIVEABLES.objects.create(status=0, order_id=order_id,description=description,
                                    receiveables=price, received=0)
        return JsonResponse({"if_success":1, "info":"添加成功"})

def delete_receiveables(request):
    if request.method == "POST":
        rec_id = request.POST.get("rec_id",0)
        try:
            rec_obj = RECEIVEABLES.objects.get(id=rec_id)
            rec_obj.delete()
            if_success = 1
            info = "删除成功"
        except:
            info = "删除失败：记录不存在"
            if_success = 0
        return JsonResponse({"if_success":if_success, "info":info})
    return JsonResponse({})

def update_receiveables_desc(request):
    if request.method == "POST":
        rec_id = request.POST.get("rec_id",0)
        desc = request.POST.get("desc","")
        if_success = 0
        info = ""
        try:
            rec_obj = RECEIVEABLES.objects.get(id=rec_id)
            rec_obj.description = desc
            rec_obj.save()
            if_success = 1
            info = "修改成功"
        except:
            info = "修改失败：记录不存在"
    return JsonResponse({"if_success":if_success, "info":info})

def update_receiveables_price(request):
    if request.method == "POST":
        rec_id = request.POST.get("rec_id")
        price = request.POST.get("price")
        if_success = 0
        info = ""
        try:
            rec_obj = RECEIVEABLES.objects.get(id=rec_id)
            rec_obj.receiveables = price
            rec_obj.save()
            if_success = 1
            info = "修改成功"
        except:
            info = "修改失败：记录不存在"
    return JsonResponse({"if_success":if_success, "info":info})