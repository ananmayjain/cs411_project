from django.shortcuts import render
from django.http import HttpResponse


def login_page(request):
    return render(request, 'sign_up.html')

def register(request):
    if request.method == "GET":
        for elem in request.args:
            if request.args[elem] == "":
                return render(request, "sign_up.html", {"invalid_login": 1})
        if True: # if mongo_client.add_account(request.args):
            return render(request, "index.html")

    return render(request, "sign_up.html", acc_exists=1)

# ADD DATABASE INTEGRATION
def signin(request):
    if request.method == "POST":
        return render(request, "sign_up.html", {"invalid_login": 1})

    else:
        print(request.GET)
        # if len(request.args) == 0:
        #     return render(request, "sign_up.html", {"invalid_login": 1})

        for elem in request.GET:
            if request.GET[elem] == "":
                return render(request, "sign_up.html", {"invalid_login": 1})

    invalid_login, unverified_login = 0, 0 # mongo_client.get_account(request.args)

    if invalid_login:
        return render(request, "sign_up.html", {"invalid_login": 1})
    elif unverified_login:
        mongo_client.resend_conf_email(request.args["emailid"])
        return render(request, "sign_up.html", {"unverified_login": 1})

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
