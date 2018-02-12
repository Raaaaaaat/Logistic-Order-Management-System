from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def page_index(reqeust):
    #对于用户进行判断，如果没有登录就跳转到login界面，否则跳转到订单界面
    return redirect("/order")