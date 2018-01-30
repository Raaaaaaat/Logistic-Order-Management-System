from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import logout



def log_in_index(request):
    if request.method == 'GET':
        #把已经登录的用户下线
        logout(request)
        return render(request, 'user/log_in.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:    #检查账号密码是否正确，如果没有问题就返回info为1， 否则返回info为0
            info = 1
            login(request, user)
        else:
            info = 0
        return JsonResponse({'info': info})