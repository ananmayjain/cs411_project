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

    
    pending_trip = database.find_pending_trips(driver_details)
    pending_trip = make_trip_info_dict(pending_trip)

    if (request.GET.get('accept_trip')):
        database.confirm_trip(pending_trip["trip_id"])

    if len(avg_rating) == 0:
        if (len(pending_trip)):
            response = render(request, "driver.html", {
                "pending":pending_trip, "ind_email":pending_trip['ind_email']})
        else:
            response = render(request, "driver.html")
        return response


    stars = round(avg_rating[0]/100 * 5)
    if "update_successful" in request.GET:
        response = render(request, "driver.html", {"update_successful": 1, "stars": stars})
    else:
        if (len(pending_trip)):
            response = render(request, "driver.html", {
                              "stars": stars, "pending": pending_trip, "ind_email": pending_trip['ind_email']})
        else:
            response = render(request, "driver.html", {"stars":stars})

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

    args = get_args(request)
    # we will use key start_loc for driver email
    # this is because I could not compeltely figure out the js form
    if len(args) != 0:
        guy = {}
        guy["driver_email"] = args["start_loc"]
        guy["ind_email"] = user_data["emailid"]
        database.create_trip(guy)

    if len(avg_rating) == 0:
        response = render(request, "industry.html")
        return response
    
    stars = round(avg_rating[0]/100 * 5) 

    if "update_successful" in request.GET:
        response = render(request, "industry.html", {"update_successful": 1, "stars": stars})
    else:
        response = render(request, "industry.html", {"stars": stars})

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
            temp = make_driver_info_dict(results[i])
            success, driver_data = database.get_driver_info(temp)
            driver_details = make_driver_info_dict(driver_data)
            avg_rating = database.get_avg_driver_rating(driver_details)
            stars = round(avg_rating[0]/100 * 5, 2) if len(avg_rating)!=0 else 0
            temp["stars"] = stars
            driver_list[i] = temp

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

def make_trip_info_dict(data):
    d = {}
    if (not data):
        return {}
    d["trip_id"] = data[0]
    d["completed"] = data[1]
    d["driver_email"] = data[2]
    d["ind_email"] = data[3]
    d["rating_from_driver"] = data[4]
    d["rating_from_industry"] = data[5]
    d["comments_from_driver"] = data[6]
    d["comments_from_industry"] = data[7]
    d["status"] = "Completed" if d["completed"] else "Ongoing"
    #print("Look at me", d)
    return d


@csrf_exempt
def find_driver_past_rides(request):
    cookies = request.COOKIES
    if "session_id" not in cookies:
        return redirect("/?session_timeout=1")

    success, data = database.mod_active_session(cookies["session_id"])

    if not success:
        return redirect("/?session_timeout=1")


    if request.method == "GET":
        user_data = make_user_session_dict(data)
        success, driver_data = database.get_driver_info(user_data)
        driver_details = make_driver_info_dict(driver_data)
        results = database.get_all_driver_trips(driver_details)
        
        if len(results) == 0:
            response = render(request, "driver_past_rides.html", {"no_trips": 1})
            set_cookie(response, cookies["session_id"])
            return response

        trip_list = {}
        for i in range(len(results)):
            trip_list[i] = make_trip_info_dict(results[i])

        response = render(request, "driver_past_rides.html", {"trip_list": trip_list})
        set_cookie(response, cookies["session_id"])
        return response


@csrf_exempt
def find_industry_past_rides(request):
    cookies = request.COOKIES
    if "session_id" not in cookies:
        return redirect("/?session_timeout=1")

    success, data = database.mod_active_session(cookies["session_id"])

    if not success:
        return redirect("/?session_timeout=1")

    if request.method == "GET":
        user_data = make_user_session_dict(data)
        success, industry_data = database.get_industry_info(user_data)
        industry_details = make_industry_info_dict(industry_data)
        results = database.get_all_industry_trips(industry_details)
        
        if len(results) == 0:
            response = render(
                request, "ind_past_rides.html", {"no_trips": 1})
            set_cookie(response, cookies["session_id"])
            return response

        trip_list = {}
        for i in range(len(results)):
            trip_list[i] = make_trip_info_dict(results[i])

        response = render(request, "ind_past_rides.html",
                          {"trip_list": trip_list})
        set_cookie(response, cookies["session_id"])
        return response
    else:
        user_data = make_user_session_dict(data)
        success, industry_data = database.get_industry_info(user_data)
        industry_details = make_industry_info_dict(industry_data)

        data = request.POST.copy()
        trip_id = data.get('trip_id')
        rating_from_industry= data.get('rating_from_industry')
        database.make_ind_rating(trip_id, rating_from_industry, industry_details['emailid'])

        results = database.get_all_industry_trips(industry_details)

        if len(results) == 0:
            response = render(
                request, "ind_past_rides.html", {"no_trips": 1})
            set_cookie(response, cookies["session_id"])
            return response

        trip_list = {}
        for i in range(len(results)):
            trip_list[i] = make_trip_info_dict(results[i])
        response = render(request, "ind_past_rides.html",
                          {"trip_list": trip_list})
        set_cookie(response, cookies["session_id"])
        return response


@csrf_exempt
def book_driver_form(request):
    return render(request, 'book_driver_form.html')
