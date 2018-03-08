from django.http import JsonResponse
from order_management.models import CLIENT
from django.contrib.auth.decorators import login_required

@login_required
def get_client_details(request):
    if request.method == "POST":
        client_id = request.POST.get("client_id")

        client_obj = CLIENT.objects.get(id=client_id)

        return JsonResponse({
                'No'            : client_obj.No,
                "type"          : client_obj.type,
                "co_name"       : client_obj.co_name,
                "co_addr"       : client_obj.co_addr,
                "co_tel"        : client_obj.co_tel,
                "tax_id"        : client_obj.tax_id,
                "account_owner" : client_obj.account_owner,
                "account_number": client_obj.account_number,
                "account_bank"  : client_obj.account_bank,
                "contact_name"  : client_obj.contact_name,
                "contact_tel"   : client_obj.contact_tel,
                "contact_role"  : client_obj.contact_role,
                "contract_start": client_obj.contract_start,
                "contract_end"  : client_obj.contract_end,
        })