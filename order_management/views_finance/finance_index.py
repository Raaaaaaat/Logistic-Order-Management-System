from django.shortcuts import render
def finance_index(request):

    if request.method == "GET":
        type = request.GET.get("type","recv")
        return render(request, 'finance/index.html', {'type':type})