from django.shortcuts import redirect
import json
def ope_edit_order(request):
    if request.method=="POST":
        supplier_list = request.POST.get("path")
        data = json.loads(supplier_list)
        info = "添加成功"
        return redirect('/order?info=' + info)