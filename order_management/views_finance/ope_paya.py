from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from order_management.models import ORDER
from order_management.models import PAYABLES
from order_management.models import SUPPLIER
from order_management.models import CLIENT

def get_paya_list(request):
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
        return JsonResponse({"data":rows})

def mark_paya_invoice(request):
    #两个参数分别是数组为payables的id，以及要批量修改的票号
    if request.method == "POST":
        paya_ids = request.POST.get("paya_ids","")
        paya_ids = paya_ids.split(",")
        invoice  = request.POST.get("invoice")

        try:
            paya_obj = PAYABLES.objects.filter(id__in=paya_ids).update(invoice=invoice)
        except:
            return JsonResponse({"if_success": 0})
        return JsonResponse({"if_success": 1})

def mark_paya_paid(request):
    #三个参数分别是数组为payables的id，以及要type（0为现金，1为油卡）， 以及总的金额
    #action: 对于未付款的金额进行校对，如果金额大于最大金额就报错，否则对于数额依次进行修改
    if request.method == "POST":
        paya_ids = request.POST.get("paya_ids","")
        paya_ids = paya_ids.split(",")
        paid_ammount  = request.POST.get("paid_ammount")
        paid_type = request.POST.get("paid_type")
        paid_ammount = float(paid_ammount)
        total_to_be_paid = 0
        for single in paya_ids: #统计总的未付款
            paya_obj = PAYABLES.objects.get(id=single)
            total_to_be_paid = total_to_be_paid + paya_obj.payables - paya_obj.paid_cash - paya_obj.paid_oil
        if total_to_be_paid < paid_ammount:
            return JsonResponse({"if_success": 0, "info":"确认失败：付款金额大于应付款"})

        #可以进行付款操作
        for single in paya_ids:
            paya_obj = PAYABLES.objects.get(id=single)
            max_to_be_paid = paya_obj.payables - paya_obj.paid_cash - paya_obj.paid_oil
            if max_to_be_paid >= paid_ammount:
                #一次付清款，退出循环
                if paid_type=="0":
                    paya_obj.paid_cash += paid_ammount
                else:
                    paya_obj.paid_oil += paid_ammount
                paya_obj.save()
                break
            else:
                paid_ammount -= max_to_be_paid
                if paid_type=="0":
                    paya_obj.paid_cash += max_to_be_paid
                else:
                    paya_obj.paid_oil += max_to_be_paid
                paya_obj.save()
        return JsonResponse({"if_success": 1})

def paya_verify(request):
    # 以个参数是数组为payables的id
    # action: 逐条对于数据进行检查，如果付款完成就修改状态，否则不予理会，然后统计修改成功的条数
    if request.method == "POST":
        paya_ids = request.POST.get("paya_ids", "")
        paya_ids = paya_ids.split(",")
        count_suc = 0
        count_err = 0
        for single in paya_ids:
            try:
                paid_obj = PAYABLES.objects.get(id=single)
                if paid_obj.status==0 and paid_obj.payables == paid_obj.paid_oil + paid_obj.paid_cash:
                    paid_obj.status=1
                    paid_obj.save()
                    count_suc = count_suc + 1
                else:
                    count_err = count_err + 1
            except:
                count_err = count_err+1

        return JsonResponse({"if_success": 1, "count_suc": count_suc, "count_err":count_err})
    return JsonResponse({"if_success": 0})