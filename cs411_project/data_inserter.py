from django.db import connection
import random
import names

domains = [ "hotmail.com", "gmail.com", "aol.com", "mail.com" , "mail.kz", "yahoo.com"]
letters = ["a", "b", "c", "d","e", "f", "g", "h", "i", "j", "k", "l"]
cities = ["Chicago", "Champaign", "New York", "San Jose"]

def get_one_random_domain(domains):
        return random.choice(domains)


def get_one_random_name(letters):
    email_name = ""
    for i in range(7):
        email_name = email_name + letters[random.randint(0,11)]
    return email_name

def generate_random_email():
    one_name = str(get_one_random_name(letters))
    one_domain = str(get_one_random_domain(domains))
    return one_name  + "@" + one_domain

def gen_phone_num():
    n = '0000000000'
    while '9' in n[3:6] or n[3:6]=='000' or n[6]==n[7]==n[8]==n[9]:
        n = str(random.randint(10**9, 10**10-1))
    return n[:3] + n[3:6] + n[6:]

def add_data(num):

    with connection.cursor() as cursor:
        for i in range(num):
            email = generate_random_email()
            # Add account to user account
            cursor.execute("Insert into User_Accounts values (%s, %s, %s)",
            [email, "ananmay", "driver"])

            # Add Driver Info
            cursor.execute("Insert into Driver_Info values (%s, %s, %s, %s, %s, %s, %s)",
            [email, names.get_first_name(), names.get_last_name(), gen_phone_num(),
            gen_phone_num(), random.choice(cities), random.choice(cities)])
