from django.shortcuts import render


def order_add(request):
    if request.method == "GET": #这是通过点击添加按钮进来的地方
        return render(request, 'order/add.html')
