from django.shortcuts import render, redirect
from django.http import HttpResponse
from cs411_project import database
from django.views.decorators.csrf import csrf_exempt
import copy
import hashlib
import datetime
import random

domain_name = "localhost"

default_dict = {"emailid": "ananmay3@illinois.edu", "fname": "Ananmay", "lname": "Jain", "phone_num": "4156700582",
        "license_num": "983983829218398", "invalid_data": 0}

@csrf_exempt
def driver_home(request):
    cookies = request.COOKIES

    if "session_id" in cookies:
        expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
        response = render(request, "driver.html")
        response.set_cookie("session_id", value=cookies["session_id"],
            expires=expiry_time, domain=domain_name)

        return response

    else:
        return redirect("/?session_timeout=1")

@csrf_exempt
def industry_home(request):
    return render(request, "info_form.html", default_dict)

@csrf_exempt
def modify_driver_info(request):
    if request.method == "GET":
        # Get Session ID, and render page with correct info from database
        pass

    else:
        args = get_args(request)
        return_dict = copy.deepcopy(default_dict)

        for elem in args.keys():
            if args[elem] == "":
                return_dict["invalid_data"] = 1
                return render(request, "info_form.html", return_dict)

        if len(args["phone_num"] != 10):
            return_dict["invalid_data"] = 1
            return render(request, "info_form.html", return_dict)

        database.update_driver_info()



def get_args(request):

    if request.method == "GET":
        args = dict(request.GET)
        for key in args.keys():
            args[key] = args[key][0]
        return args
    else:
        args = dict(request.POST)
        for key in args.keys():
            args[key] = args[key][0]
        return args
