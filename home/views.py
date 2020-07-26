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

    cookies = request.COOKIES
    if "session_id" not in cookies:
        return redirect("/?session_timeout=1")

    success, data = database.mod_active_session(cookies["session_id"])

    if not success:
        return redirect("/?session_timeout=1")
    user_data = make_user_session_dict(data)

    success, data = database.get_driver_info(user_data)
    driver_details = make_driver_info_dict(data)

    if request.method == "GET":
        response = render(request, "info_form.html", driver_details)
        return response

    else:
        args = get_args(request)

        for elem in args.keys():
            if args[elem] == "":
                driver_details["invalid_data"] = 1
                return render(request, "info_form.html", driver_details)

        args["phone_num"] = get_digits(args["phone_num"])

        if len(args["phone_num"]) != 10:
            print("Phone Number not 10 digits")
            driver_details["invalid_data"] = 1
            return render(request, "info_form.html", driver_details)

        if database.update_driver_info(args):
            response = redirect("/home/driverhome?update_successful=1")
            return response
        else:
            response = redirect("/home/driverhome?update_failed=1")
            return response

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

def make_user_session_dict(data):
    d = {}
    d["session_id"] = data[0]
    d["emailid"] = data[1]
    d["valid_till"] = data[2]

    return d

def make_driver_info_dict(data):
    d = {}
    d["emailid"] = data[0]
    d["fname"] = data[1]
    d["lname"] = data[2]
    d["phone_num"] = data[3]
    d["license_num"] = data[4]

    return d

def get_digits(phone_num):
    number = ""
    for i in range(len(phone_num)):
        if phone_num[i].isdigit():
            number += phone_num[i]

    return number
