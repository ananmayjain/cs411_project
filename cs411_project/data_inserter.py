from django.db import connection
import random
import string
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


def add_data(num):

    with connection.cursor() as cursor:
        # Input driver info
        for i in range(num):
            email = generate_random_email()
            # Add account to user account
            cursor.execute("Insert into User_Accounts values (%s, %s, %s)",
            [email, "ananmay", "driver"])
            # Add Driver Info
            cursor.execute("Insert into Driver_Info values (%s, %s, %s, %s, %s, %s, %s)",
            [email, names.get_first_name(), names.get_last_name(), gen_phone_num(),
            gen_phone_num(), random.choice(cities), random.choice(cities)])

        # Input Industry Info
        for i in range(num):
            email = generate_random_email()
            # Add account to user account
            cursor.execute("Insert into User_Accounts values (%s, %s, %s)",
            [email, "ananmay", "industry"])
            # Add Industry Info
            cursor.execute("Insert into Ind_Info values (%s, %s, %s, %s)",
                           [email, names.get_first_name(), names.get_last_name(), gen_phone_num()
                            ])

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
            

