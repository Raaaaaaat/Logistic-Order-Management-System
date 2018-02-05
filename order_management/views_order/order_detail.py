from django.shortcuts import render

def order_detail(request):
    if request.method == "GET":
        No = request.GET.get('No', '')

        return render(request, 'order/detail.html', {'No': No})