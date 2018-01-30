from django.contrib.auth import logout
from django.http import JsonResponse


def log_out_request(request):
    logout(request)
    return JsonResponse({}) #从前端来看，只要有返回就说明登出成功，否则算登出失败
