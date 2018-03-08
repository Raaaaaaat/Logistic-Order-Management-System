from django.http import JsonResponse
from django.shortcuts import redirect
from order_management.models import CLIENT
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Q

@login_required
def ope_edit_client(request):     #这个方法可以用来增加单条数据或者修改数据
    if request.method == "POST":
        if_edit     = request.POST.get("if_edit")       #是否是编辑模式 0代表新建，不是0代表编辑并且此值为客户编号
        if_refile   = request.POST.get("if_refile")     #是否重新载入文件
        type        = request.POST.get("type")
        co_name     = request.POST.get("co_name")
        co_addr     = request.POST.get("co_addr")
        co_tel      = request.POST.get("co_tel")
        tax_id      = request.POST.get("tax_id")
        account_owner  = request.POST.get("account_owner")
        account_number = request.POST.get("account_number")
        account_bank   = request.POST.get("account_bank")
        contact_name   = request.POST.get("contact_name")
        contact_tel    = request.POST.get("contact_tel")
        contact_role   = request.POST.get("contact_role")
        contract_start = request.POST.get("contract_start")
        contract_end   = request.POST.get("contract_end")
        remark         = request.POST.get("remark")
        if if_edit=="0":
            #新增模式
            if not request.user.has_perm("order_management.add_client"):
                info = "操作失败：没有进行此操作的权限"
                return redirect('/supplier?info=' + info)
            # 检查重复
            if type == "0":
                conflict_check = CLIENT.objects.filter(co_name=co_name).exists()
            else:
                conflict_check = CLIENT.objects.filter(contact_name=contact_name).exists()
            if not conflict_check:  # 没有重复冲突
                No = ""  #自动生成下一个该有的客户编号
                last_one = CLIENT.objects.last()
                if last_one != None:    #说明之前已经有记录
                    No = last_one.No[1:]
                    No = int(No)+1
                    No = "C"+str(No).zfill(3)
                else:
                    No = "C001"
                contract_file = request.FILES.get("contract_file", None)
                file_path = ""
                if contract_file != None:
                    if contract_file.size > 10485760:
                        info = "文件过大,不可大于10M"
                        return redirect('/supplier?info=' + info)
                    file_path = contract_file._name #获取到源文件的名字
                    file_path = file_path.split(".").pop() #获取文件后缀
                    file_path = "/static/tmp_file/client/"+No+"."+file_path
                    destination = open("/var/www/tmr/order_management"+file_path, 'wb+')
                    for chunk in contract_file.chunks():
                        destination.write(chunk)
                    destination.close()
                CLIENT.objects.create(No=No,type=int(type), tax_id=tax_id,
                                      co_name=co_name, co_addr=co_addr, co_tel=co_tel,
                                      account_owner=account_owner, account_number=account_number,
                                      account_bank=account_bank, contact_name=contact_name,
                                      contact_tel=contact_tel, contact_role=contact_role,
                                      contract_start=contract_start, contract_end=contract_end,
                                      contract_file=file_path, remark=remark)
                info = "添加成功"
            else:
                info = "添加失败，该客户已存在"
        else:
            #编辑模式
            if not request.user.has_perm("order_management.change_client"):
                info = "操作失败：没有进行此操作的权限"
                return redirect('/supplier?info=' + info)
            # 检查重复
            if type == "0":
                conflict_check = CLIENT.objects.filter(~Q(No=if_edit)&Q(co_name=co_name)).exists()
            else:
                conflict_check = CLIENT.objects.filter(~Q(No=if_edit)&Q(contact_name=contact_name)).exists()
            if not conflict_check:  # 没有重复冲突
                No = if_edit
                try:
                    target_obj = CLIENT.objects.get(No=No)
                except:
                    return redirect('/client?info=客户不存在！')
                target_obj.co_name = co_name
                target_obj.co_addr = co_addr
                target_obj.co_tel = co_tel
                if request.user.has_perm("order_management.change_client_tax"): #二次检查，防止没有权限的用户越过界面伪造表单修改数据
                    target_obj.tax_id = tax_id
                target_obj.account_owner = account_owner
                target_obj.account_number = account_number
                target_obj.account_bank = account_bank
                target_obj.contact_name = contact_name
                target_obj.contact_tel = contact_tel
                target_obj.contact_role = contact_role
                target_obj.remark      =remark
                if request.user.has_perm("order_management.change_client_contract"): #二次检查，防止没有权限的用户越过界面伪造表单修改数据
                    target_obj.contract_start = contract_start
                    target_obj.contract_end = contract_end
                    if(if_refile == "1" or target_obj.contract_file==""):
                        contract_file = request.FILES.get("contract_file", None)
                        file_path = ""
                        if contract_file != None:
                            if contract_file.size > 10485760:
                                info = "文件过大"
                                return redirect('/supplier?info=' + info)
                            file_path = contract_file._name  # 获取到源文件的名字
                            file_path = file_path.split(".").pop()  # 获取文件后缀
                            file_path = "/static/tmp_file/client/" + No + "." + file_path
                            destination = open("/var/www/tmr/order_management"+file_path, 'wb+')
                            for chunk in contract_file.chunks():
                                destination.write(chunk)
                            destination.close()
                        target_obj.contract_file = file_path
                target_obj.save()
                info = "修改成功"
            else:
                info = "修改失败，该客户已经存在"
        return redirect('/client?info='+info)
    else:
        return redirect('/404')
