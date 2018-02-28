from django.shortcuts import render, redirect
from order_management.models import ORDER
from order_management.models import CLIENT

def order_edit(request):
    if request.method == "GET": #这是通过点击添加按钮进来的地方
        No = request.GET.get("No","")
        try:
            to_be_edit_obj = ORDER.objects.get(No=No)
        except:
            return redirect("/order?info=客户不存在")

        try:
            client_obj = CLIENT.objects.get(id=to_be_edit_obj.client_id)
            if client_obj.type==0:
                client_name = client_obj.No + " - "+ client_obj.co_name
            else:
                client_name = client_obj.No + " - "+ client_obj.contact_name
        except:
            client_name="客户已删除"
        return render(request, 'order/edit.html', {
            'No': to_be_edit_obj.No,
            'client_name': client_name,
            'dep_city': to_be_edit_obj.dep_city,
            'des_city': to_be_edit_obj.des_city,
            'dep_place': to_be_edit_obj.dep_place,
            'des_place': to_be_edit_obj.des_place,
            'cargo_quantity': to_be_edit_obj.cargo_quantity,
            'cargo_name': to_be_edit_obj.cargo_name,
            'cargo_weight': to_be_edit_obj.cargo_weight,
            'cargo_size': to_be_edit_obj.cargo_size,
            'remark':     to_be_edit_obj.remark,
            'rec_name':   to_be_edit_obj.rec_name,
            'rec_tel':    to_be_edit_obj.rec_tel,
        })
    elif request.method=="POST":
        No = request.POST.get("No", "")
        rec_name = request.POST.get("rec_name", "")
        rec_tel = request.POST.get("rec_tel", "")
        dep_city = request.POST.get("dep_city", "")
        dep_place = request.POST.get("dep_place", "")
        des_city = request.POST.get("des_city", "")
        des_place = request.POST.get("des_place", "")
        cargo_name = request.POST.get("cargo_name", "")
        cargo_weight = request.POST.get("cargo_weight", "")
        cargo_quantity = request.POST.get("cargo_quantity", "")
        cargo_size = request.POST.get("cargo_size", "")
        remark = request.POST.get("remark", "")
        try:
            order_obj = ORDER.objects.get(No=No)
            order_obj.rec_name = rec_name
            order_obj.rec_tel = rec_tel
            order_obj.dep_city = dep_city
            order_obj.dep_place = dep_place
            order_obj.des_city = des_city
            order_obj.des_place = des_place
            order_obj.cargo_name = cargo_name
            order_obj.cargo_weight = cargo_weight
            order_obj.cargo_quantity = cargo_quantity
            order_obj.cargo_size = cargo_size
            order_obj.remark = remark
            order_obj.save()

        except:
            return redirect("/order?info=修改失败：订单不存在")

        return redirect('/order?info=修改成功')