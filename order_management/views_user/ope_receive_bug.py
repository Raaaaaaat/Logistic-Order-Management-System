from django.http import JsonResponse
from order_management.models import USER_FEEDBACK
from django.contrib.auth.decorators import login_required

@login_required
def ope_receive_bug(request):
    if request.method=="POST":
        bug = request.POST.get("bug","")
        USER_FEEDBACK.objects.create(user=request.user.username, description=bug)
        return JsonResponse({'if_success':1, 'info': "创建成功"})

