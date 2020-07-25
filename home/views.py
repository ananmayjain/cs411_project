from django.shortcuts import render, redirect
from django.http import HttpResponse
from cs411_project import database
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def driver_home(request):
    return render(request, "driver.html")

@csrf_exempt
def industry_home(request):
    return render(request, "info_form.html", {"fname": "Ananmay"})

@csrf_exempt
def modify_driver_info(request):
    if request.method == "GET":
        print(request.GET)

    else:
        print(request.POST)
