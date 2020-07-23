from django.shortcuts import render
from django.http import HttpResponse
from cs411_project import database


def login_page(request):
    return render(request, 'sign_up.html')

def register(request):
    if request.method == "GET":

        args = get_register_args(request)

        for elem in args.keys():
            if args[elem] == "":
                return render(request, "sign_up.html", {"invalid_login": 1})
        if database.add_user_account(args):
            return render(request, "index.html")

    return render(request, "sign_up.html", {"acc_exists": 1})

# ADD DATABASE INTEGRATION
def signin(request):
    if request.method == "POST":
        return render(request, "sign_up.html", {"invalid_login": 1})

    else:
        args = get_register_args(request)
        for elem in args.keys():
            if args[elem] == "":
                return render(request, "sign_up.html", {"invalid_login": 1})

        valid_login = database.check_user_account(args)

        if not valid_login:
            return render(request, "sign_up.html", {"invalid_login": 1})
        # elif unverified_login:
        #     mongo_client.resend_conf_email(request.args["emailid"])
        #     return render(request, "sign_up.html", {"unverified_login": 1})

        # VALID LOGIN
        # session = mongo_client.add_active_session(request.args)

        return render(request, "index.html")


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
    args = dict(request.GET)
    for key in args.keys():
        args[key] = args[key][0]
    return args
