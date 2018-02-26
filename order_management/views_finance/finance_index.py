from django.shortcuts import render
def finance_index(request):

    if request.method == "GET":

        return render(request, 'finance/index.html')