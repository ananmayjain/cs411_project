from django.db import connection
import random
import string
import names
from cs411_project.dbs import server
import hashlib

domains = [ "hotmail.com", "gmail.com", "aol.com", "mail.com" , "mail.kz", "yahoo.com"]
letters = ["a", "b", "c", "d","e", "f", "g", "h", "i", "j", "k", "l"]
cities = ["Chicago", "Champaign", "New York", "San Jose"]
industries = ["Microsoft", "Apple", "Uber", "Nvidia", "Cisco", "Lyft", "Tesla", "Amazon"]

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

def gen_random_trip_id():
    char_set = string.ascii_uppercase + string.digits
    return ''.join(random.sample(char_set*12, 12))

#I think it makes more sense if the ratings
# somewhat agree with eachother
def gen_rating_with_arg(x):
    return min(100, x + random.randint(-10, 10))

def gen_rating():
    return random.randint(5, 100)


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def getClientNum(data):
    hex = hashlib.sha256(str(data).encode()).hexdigest()
    return int(hex, 16) % 4


def add_data(num):

    global industries

    with connection.cursor() as cursor:
        # Input driver info
        for i in range(num):

            phone_num = gen_phone_num()
            license_num = gen_phone_num()
            start_loc = random.choice(cities)
            end_loc = random.choice(cities)

            while True:
                fname = names.get_first_name()
                lname = names.get_last_name()
                email = fname + "." + lname + "@" + str(get_one_random_domain(domains))

                cursor.execute("Select * from User_Accounts where emailid = %s", [email])
                row = cursor.fetchone()
                if row == None:
                    break

            # Add account to user account
            cmd = 'Insert into User_Accounts values ("%s", "%s", "%s")' % \
            (email, "ananmay", "driver")
            client_num = getClientNum(email)
            server.pushData(client_num, cmd)

            cursor.execute("Insert into User_Accounts values (%s, %s, %s)",
            [email, "ananmay", "driver"])

            # Add Driver Info
            cmd = 'Insert into Driver_Info values ("%s", "%s", "%s", "%s", "%s", "%s", "%s")' % \
            (email, fname, lname, phone_num, license_num, start_loc, end_loc)
            server.pushData(client_num, cmd)

            cursor.execute("Insert into Driver_Info values (%s, %s, %s, %s, %s, %s, %s)",
            [email, fname, lname, phone_num, license_num, start_loc, end_loc])

        # Input Industry Info
        for i in range(num):

            ind_name = random.choice(industries)

            while True:
                fname = names.get_first_name()
                lname = names.get_last_name()
                email = fname + "." + lname + "@" + str(get_one_random_domain(domains))

                cursor.execute("Select * from User_Accounts where emailid = %s", [email])
                row = cursor.fetchone()
                if row == None:
                    break

            # Add account to user account
            cmd = 'Insert into User_Accounts values ("%s", "%s", "%s")' % \
            (email, "ananmay", "industry")
            client_num = getClientNum(email)
            server.pushData(client_num, cmd)

            cursor.execute("Insert into User_Accounts values (%s, %s, %s)",
            [email, "ananmay", "industry"])

            # Add Industry Info
            cmd = 'Insert into Ind_Info values ("%s", "%s", "%s", "%s")' % \
                           (email, fname, lname, ind_name)
            server.pushData(client_num, cmd)
            cursor.execute("Insert into Ind_Info values (%s, %s, %s, %s)",
                           [email, fname, lname, ind_name])

        # Input Trips Info
        for i in range(num):
            trip_id = gen_random_trip_id()
            rating_from_driver = gen_rating()
            rating_from_ind = gen_rating_with_arg(rating_from_driver)

            cursor.execute("SELECT emailid FROM Driver_Info")
            drivers = cursor.fetchall()
            d_len = len(drivers)
            cursor.execute("SELECT emailid FROM Ind_Info")
            industries = cursor.fetchall()
            i_len = len(industries)

            cursor.execute("Insert Into Trips values (%s, %s, %s, %s, %s, %s, %s, %s)",
            [trip_id, '1', drivers[random.randint(0,d_len-1)][0],
             industries[random.randint(0, i_len-1)][0], str(rating_from_driver),
             str(rating_from_ind), "alright", "okay"])
