from django.shortcuts import render, redirect
from django.http import HttpResponse
from cs411_project import database
from django.views.decorators.csrf import csrf_exempt
import datetime
import random
import hashlib

domain_name = "localhost"

def login_page(request):

    if "session_timeout" in request.GET:
        return render(request, "sign_up.html", {"session_timeout": 1})

    return render(request, 'sign_up.html')

@csrf_exempt
def register(request):
    if request.method == "GET":

        args = get_register_args(request)

        for elem in args.keys():
            if args[elem] == "":
                return render(request, "sign_up.html", {"invalid_login": 1})
        if database.add_user_account(args):
            return render(request, "sign_up.html", {"register_success": 1})

    return render(request, "sign_up.html", {"acc_exists": 1})

# ADD DATABASE INTEGRATION
@csrf_exempt
def signin(request):
    if request.method == "GET":
        return render(request, "sign_up.html", {"invalid_login": 1})

    else:
        args = get_register_args(request)
        print(args)

        for elem in args.keys():
            if args[elem] == "":
                return render(request, "sign_up.html", {"invalid_login": 1})

        valid_login, data = database.check_user_account(args)

        if not valid_login:
            return render(request, "sign_up.html", {"invalid_login": 1})
        # elif unverified_login:
        #     mongo_client.resend_conf_email(request.args["emailid"])
        #     return render(request, "sign_up.html", {"unverified_login": 1})

        # VALID LOGIN
        user_data = make_user_acc_dict(data)

        session_id, expiry_time = database.add_active_session(user_data)

        if user_data["type_of_acc"] == "driver":

            response = redirect("/home/driverhome")
            response.set_cookie("session_id", value=session_id,
                expires=expiry_time, domain=domain_name)

            return response

        elif user_data["type_of_acc"] == "industry":
            return redirect("/home/industryhome")
        else:
            print("ERROR SANITY CHECK type_of_acc")

        return redirect("/")


# ADD DATABASE INTEGRATION
def confirm_account(request, token_emailid):

    if request.method == "POST":
        print(request.form)

    else:
        token = token_emailid[0:64]
        emailid = token_emailid[64:]
        # mongo_client.verify_account(emailid, token)

    return render(request, "index.html")


def get_register_args(request):

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

def make_user_acc_dict(data):
    d = {}
    d["emailid"] = data[0]
    d["passwd"] = data[1]
    d["type_of_acc"] = data[2]

    return d
