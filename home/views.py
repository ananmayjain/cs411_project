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
    if "session_id" not in cookies:
        return redirect("/?session_timeout=1")

    success, data = database.mod_active_session(cookies["session_id"])
    if not success:
        return redirect("/?session_timeout=1")

    user_data = make_user_session_dict(data)
    success, driver_data = database.get_driver_info(user_data)
    driver_details = make_driver_info_dict(driver_data)
    avg_rating = database.get_avg_driver_rating(driver_details)
    if "update_successful" in request.GET:
        response = render(request, "driver.html", {"update_successful": 1, "avg_rating": avg_rating[0]})
    else:
        response = render(request, "driver.html", {"avg_rating": avg_rating[0]})

    set_cookie(response, cookies["session_id"])
    return response

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
        set_cookie(response, cookies["session_id"])
        return response

    else:
        args = get_args(request)

        for elem in args.keys():
            if args[elem] == "":
                driver_details["invalid_data"] = 1
                response = render(request, "info_form.html", driver_details)
                set_cookie(response, cookies["session_id"])
                return response

        args["phone_num"] = get_digits(args["phone_num"])

        if len(args["phone_num"]) != 10:
            print("Phone Number not 10 digits")
            driver_details["invalid_data"] = 1
            response = render(request, "info_form.html", driver_details)
            set_cookie(response, cookies["session_id"])
            return response

        if database.update_driver_info(args):
            response = redirect("/home/driverhome?update_successful=1")
            set_cookie(response, cookies["session_id"])
            return response
        else:
            response = redirect("/home/driverhome?update_failed=1")
            set_cookie(response, cookies["session_id"])
            return response

@csrf_exempt
def delete_account(request):
    cookies = request.COOKIES
    if "session_id" not in cookies:
        return redirect("/?session_timeout=1")

    success, data = database.mod_active_session(cookies["session_id"])

    if not success:
        print("Something Weird Happened")
        return redirect("/?session_timeout=1")
    user_data = make_user_session_dict(data)

    database.delete_user_account(user_data)

    response = redirect("/?account_deleted=1")
    response.delete_cookie("session_id")
    return response

@csrf_exempt
def sign_out(request):
    cookies = request.COOKIES
    if "session_id" not in cookies:
        return redirect("/?session_timeout=1")

    response = redirect("/?sign_out=1")
    response.delete_cookie("session_id")
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
    d["start_loc"] = data[5]
    d["end_loc"] = data[6]

    return d

def get_digits(phone_num):
    number = ""
    for i in range(len(phone_num)):
        if phone_num[i].isdigit():
            number += phone_num[i]

    return number

def set_cookie(response, cookie_value):
    response.set_cookie("session_id", value=cookie_value, max_age= (5*60), domain=domain_name)

@csrf_exempt
def industry_home(request):

    cookies = request.COOKIES
    if "session_id" not in cookies:
        return redirect("/?session_timeout=1")

    success, data = database.mod_active_session(cookies["session_id"])
    if not success:
        return redirect("/?session_timeout=1")
    user_data = make_user_session_dict(data)
    success, industry_data = database.get_industry_info(user_data)
    industry_details = make_industry_info_dict(industry_data)
    avg_rating = database.get_avg_ind_rating(industry_details)

    if "update_successful" in request.GET:
        response = render(request, "industry.html", {"update_successful": 1, "avg_rating": avg_rating[0]})
    else:
        response = render(request, "industry.html", {"avg_rating": avg_rating[0]})

    set_cookie(response, cookies["session_id"])
    return response

@csrf_exempt
def modify_industry_info(request):

    cookies = request.COOKIES
    if "session_id" not in cookies:
        return redirect("/?session_timeout=1")

    success, data = database.mod_active_session(cookies["session_id"])

    if not success:
        return redirect("/?session_timeout=1")
    user_data = make_user_session_dict(data)

    success, data = database.get_industry_info(user_data)
    industry_details = make_industry_info_dict(data)

    if request.method == "GET":
        response = render(request, "info_form_industry.html", industry_details)
        set_cookie(response, cookies["session_id"])
        return response

    else:
        args = get_args(request)

        for elem in args.keys():
            if args[elem] == "":
                industry_details["invalid_data"] = 1
                response = render(request, "info_form_industry.html", industry_details)
                set_cookie(response, cookies["session_id"])
                return response

        args["phone_num"] = get_digits(args["phone_num"])

        if len(args["phone_num"]) != 10:
            print("Phone Number not 10 digits")
            industry_details["invalid_data"] = 1
            response = render(request, "info_form_industry.html", industry_details)
            set_cookie(response, cookies["session_id"])
            return response

        if database.update_industry_info(args):
            response = redirect("/home/industryhome?update_successful=1")
            set_cookie(response, cookies["session_id"])
            return response
        else:
            response = redirect("/home/industryhome?update_failed=1")
            set_cookie(response, cookies["session_id"])
            return response

@csrf_exempt
def find_drivers(request):

    cookies = request.COOKIES
    if "session_id" not in cookies:
        return redirect("/?session_timeout=1")

    success, data = database.mod_active_session(cookies["session_id"])

    if not success:
        return redirect("/?session_timeout=1")
    user_data = make_user_session_dict(data)

    # Find Drivers with Correct Start & End Points

    if request.method == "GET":
        response = render(request, "find_drivers.html")
        set_cookie(response, cookies["session_id"])
        return response

    else:
        args = get_args(request)

        for elem in args.keys():
            if args[elem] == "":
                response = render(request, "info_form_industry.html", {"invalid_data": 1})
                set_cookie(response, cookies["session_id"])
                return response


        results = database.get_relevant_drivers(args)
        if len(results) == 0:
            response = render(request, "find_drivers.html", {"no_driver": 1})
            set_cookie(response, cookies["session_id"])
            return response

        driver_list = {}
        for i in range(len(results)):
            driver_list[i] = make_driver_info_dict(results[i])

        response = render(request, "table.html", {"driver_list": driver_list})
        set_cookie(response, cookies["session_id"])
        return response


def make_industry_info_dict(data):
    d = {}
    d["emailid"] = data[0]
    d["fname"] = data[1]
    d["lname"] = data[2]
    d["ind_name"] = data[3]
    d["phone_num"] = data[4]
    return d
