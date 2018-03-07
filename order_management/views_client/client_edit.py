from django.shortcuts import redirect
from django.shortcuts import render
from order_management.models import CLIENT
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


@login_required
@permission_required('order_management.change_client', login_url='/no_perm/')
def client_edit(request):
    if request.method == "POST":
        #检查是否有修改各个部分的权限
        perm_tax = False
        perm_contract = False
        if request.user.has_perm('order_management.change_client_tax'):
            perm_tax = True
        if request.user.has_perm('order_management.change_client_contract'):
            perm_contract = True

        No = request.POST.get("No")
        to_be_edit_obj = CLIENT.objects.filter(No=No).first()
        if to_be_edit_obj==None:
            return redirect('/error?info=查询对象不存在')
        return render(request, 'client/add.html', {
            'No'            : to_be_edit_obj.No,
            "type"          : to_be_edit_obj.type,
            "co_name"       : to_be_edit_obj.co_name,
            "co_addr"       : to_be_edit_obj.co_addr,
            "co_tel"        : to_be_edit_obj.co_tel,
            "tax_id"        : to_be_edit_obj.tax_id,
            "account_owner" : to_be_edit_obj.account_owner,
            "account_number": to_be_edit_obj.account_number,
            "account_bank"  : to_be_edit_obj.account_bank,
            "contact_name"  : to_be_edit_obj.contact_name,
            "contact_tel"   : to_be_edit_obj.contact_tel,
            "contact_role"  : to_be_edit_obj.contact_role,
            "contract_start": to_be_edit_obj.contract_start,
            "contract_end"  : to_be_edit_obj.contract_end,
            "contract_file" : to_be_edit_obj.contract_file,
            "perm_tax"      : perm_tax,
            "perm_contract" : perm_contract,
            "remark"        : to_be_edit_obj.remark,
        })
    else:
        #直接访问网址而不是通过跳转提交表单就会到这个页面，跳转到404
        return redirect('/404')