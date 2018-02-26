from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from order_management.models import ORDER
from order_management.models import PAYABLES
from order_management.models import SUPPLIER
from order_management.models import CLIENT

def get_papa_list(request):
    if request.method == "POST":

        pay_obj = PAYABLES.objects.filter().values()
        #除了表内基本信息，还有联合查询step 以及supplier的信息（由id查询name）


        supplier_obj = SUPPLIER.objects.all()
        supplier_dic = {}
        for line in supplier_obj:
            if line.type==0: #公司供应商
                supplier_dic[line.id] = line.No+" - "+line.co_name
            elif  line.type==1: #个人供应商
                supplier_dic[line.id] = line.No+" - "+line.contact_name
        rows = []
        for line in pay_obj:
            order_obj = ORDER.objects.get(id=line["order_id"])
            client_id = order_obj.client_id
            client_obj = CLIENT.objects.get(id=client_id)
            if client_obj.type == 0:
                line["client_name"] = client_obj.No + " - " + client_obj.co_name
            else:
                line["client_name"] = client_obj.No + " - " + client_obj.contact_name
            line["order_No"] = order_obj.No
            line["dep_city"] = order_obj.dep_city
            line["des_city"] = order_obj.des_city
            line["supplier_name"] = supplier_dic[line["supplier_id"]]
            rows.append(line)
        return JsonResponse({"rows":rows})