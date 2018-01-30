from django.shortcuts import render
from django.http import JsonResponse


from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


def order_index(request):

    if request.method == "GET":
        info = request.GET.get('info', '')
        return render(request, 'order/index.html', {'info':info})

    elif request.method == "POST":
        #返回表格的数据
        data = {
            "total": 100,
            "rows":  [],
        }
        return JsonResponse(data)