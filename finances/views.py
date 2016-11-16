from django.shortcuts import render


def index(request):
    return render(request, 'purchase_log/left_navbar_test.html')