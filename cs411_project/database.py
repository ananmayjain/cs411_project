#! /usr/bin/python

'''
TABLE SCHEMA REFERENCE

Create Table User_Accounts (
    emailid VarChar(120) NOT NULL,
    passwd VarChar(120) NOT NULL,
    type_of_acc VarChar(30) NOT NULL,
    Primary Key(emailid)
);

Create Table Driver_Info (
    emailid VarChar(120) NOT NULL,
    fname VarChar(120),
    lname VarChar(120),
    license_num INT,
    Primary Key(emailid),
    Foreign Key (emailid) References User_Accounts(emailid) On Delete Cascade
);

Create Table Ind_Info (
    emailid VarChar(120) NOT NULL,
    fname VarChar(120),
    lname VarChar(120),
    ind_name VarChar(120),
    Primary Key(emailid),
    Foreign Key (emailid) References User_Accounts(emailid) On Delete Cascade
);

Create Table Trips (
    trip_id VarChar(120) NOT NULL,
    completed boolean,
    driver_email VarChar(120) NOT NULL,
    ind_email VarChar(120) NOT NULL,
    rating_from_driver DECIMAL(3),
    rating_from_industry DECIMAL(3),
    comments_from_driver VarChar(300),
    comments_from_industry VarChar(300),
    Primary Key(trip_id),
    Foreign Key (driver_email) References Driver_Info(emailid) On Delete Cascade,
    Foreign Key (ind_email) References Ind_Info(emailid) On Delete Cascade
);

'''


''' Command TEMPLATES '''
insert_user_acc = "Insert Into User_Accounts values (%s, %s, %s, %s, %s, %d, %d)"

from django.db import connection
import hashlib
import datetime
import threading
import random
import string
from cs411_project.data_inserter import gen_random_trip_id


DEBUG = 1

session_counter = 0
session_counter_lock = threading.Lock()

def add_user_account(data):
    with connection.cursor() as cursor:

        if DEBUG:
            print(data)

        cursor.execute("Select * from User_Accounts where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # User Account already present
        if row != None:
            return False

        cursor.execute("Insert Into User_Accounts Values (%s, %s, %s)",
            [data["emailid"], data["passwd"], data["type_of_acc"]]
        )

        return True

def delete_user_account(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from User_Accounts where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # User not present in database, SANITY CHECK
        if row == None:
            print("Sanity CHECK user not present in delete data")
            return False

        cursor.execute("Delete from User_Accounts where emailid = %s", [data["emailid"]])
        return True

def check_user_account(data): # Used for login
    with connection.cursor() as cursor:

        cursor.execute("Select * from User_Accounts \
                        where emailid = %s and passwd = %s",
                        [data["emailid"], data["passwd"]]
        )

        row = cursor.fetchone()

        if DEBUG:
            print(data)
            print(row)

        # User Account already present
        if row == None:
            return False, None

        return True, row

def print_user_account(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from User_Accounts where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # Driver acc not present in database, SANITY CHECK
        if row == None:
            return False

        print(row)
        return True

def add_driver_info(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from Driver_Info where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # Driver acc already present in database, SANITY CHECK
        if row != None:
            return False

        cursor.execute("Insert Into Driver_Info Values (%s, %s, %s, %s, %s, %s, %s)",
            [data["emailid"], data["fname"], data["lname"], data["phone_num"],
            data["license_num"], data["start_loc"], data["end_loc"]]
        )

        return True

def update_driver_info(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from Driver_Info where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # Driver acc not present in database, SANITY CHECK
        if row == None:
            print("Something Weird Happened Sanity Check")
            return False

        cmd = "Update Driver_Info set "
        for key in data.keys():
            if key != "emailid":
                cmd += str(key) + " = " + '"' + str(data[key]) + '"' + ","
        cmd = cmd[0:-1]
        cmd += " where emailid = " + '"' + str(data["emailid"]) + '"'

        if DEBUG:
            print(cmd)

        cursor.execute(cmd)
        return True

def get_driver_info(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from Driver_Info where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # Driver acc not present in database, SANITY CHECK
        if row == None:
            print("SANITY CHECK Driver info not present")
            cursor.execute("Insert Into Driver_Info Values (%s, %s, %s, %s, %s, %s, %s)",
                [data["emailid"], "", "", "", "", "", ""]
            )
            return True, [data["emailid"], "", "", "", "", "", ""]

        return True, row

def print_driver_info(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from Driver_Info where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # Driver acc not present in database, SANITY CHECK
        if row == None:
            return False

        print(row)
        return True

def add_active_session(data):
    global session_counter

    while True:

        with session_counter_lock:
            session_id = hashlib.sha256(str(session_counter).encode()).hexdigest()
            session_counter += 1
        with connection.cursor() as cursor:
            # Make sure no other session is active with the same ID
            cursor.execute("Select * from active_sessions where session_id = %s", [session_id])
            row = cursor.fetchone()

            if row != None:
                continue

            expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
            sql_time = expiry_time.strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("Insert into active_sessions values (%s, %s, %s)",
            [session_id, data["emailid"], sql_time])

            return session_id, expiry_time

def mod_active_session(session_id):
    global session_counter

    while True:

        with connection.cursor() as cursor:
            # Make sure no other session is active with the same ID
            cursor.execute("Select * from active_sessions where session_id = %s", [session_id])
            row = cursor.fetchone()

            if row == None:
                return False, None

            expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
            sql_time = expiry_time.strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("Update active_sessions set valid_till = %s where session_id = %s",
            [sql_time, session_id])

            return True, row

def add_industry_info(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from Ind_Info where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # Driver acc already present in database, SANITY CHECK
        if row != None:
            return False

        cursor.execute("Insert Into Ind_Info Values (%s, %s, %s, %s, %s)",
            [data["emailid"], data["fname"], data["lname"], data["ind_name"], data["phone_num"]]
        )

        return True

def update_industry_info(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from Ind_Info where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # Driver acc not present in database, SANITY CHECK
        if row == None:
            print("Something Weird Happened Sanity Check")
            return False

        cmd = "Update Ind_Info set "
        for key in data.keys():
            if key != "emailid":
                cmd += str(key) + " = " + '"' + str(data[key]) + '"' + ","
        cmd = cmd[0:-1]
        cmd += " where emailid = " + '"' + str(data["emailid"]) + '"'

        if DEBUG:
            print(cmd)

        cursor.execute(cmd)
        return True

def get_industry_info(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from Ind_Info where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # Driver acc not present in database, SANITY CHECK
        if row == None:
            print("SANITY CHECK Driver info not present")
            cursor.execute("Insert Into Ind_Info Values (%s, %s, %s, %s, %s)",
                [data["emailid"], "", "", "", ""]
            )
            return True, [data["emailid"], "", "", "", ""]

        return True, row

def get_relevant_drivers(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from Driver_Info where start_loc = %s and end_loc = %s",
            [data["start_loc"], data["end_loc"]])

        rows = cursor.fetchall()
        return rows

def get_avg_driver_rating(data):
    # assume this is called from the driver page
    # I can't do multiline queries it complains
    # I can put it in comments for readability
    with connection.cursor() as cursor:
        '''
            SELECT avg(rating_from_industry) AS value 
            FROM Trips WHERE driver_email = %s 
            GROUP BY driver_email
        ''' 
        cursor.execute(
            "SELECT avg(rating_from_industry) AS value FROM Trips WHERE driver_email = %s GROUP BY driver_email", 
            [data["emailid"]] )
        row = cursor.fetchone()
        #No trips then return -1
        if row == None:
            print("This driver has no previous trips")
            return {}

        return row  

def get_avg_ind_rating(data):
    with connection.cursor() as cursor:
        '''
            SELECT avg(rating_from_driver) AS value 
            FROM Trips WHERE ind_email = %s 
            GROUP BY ind_email
        '''
        cursor.execute(
            "SELECT avg(rating_from_driver) AS value FROM Trips WHERE ind_email = %s GROUP BY ind_email",
            [data["emailid"]])
        row = cursor.fetchone()
        #No trips then return -1
        if row == None:
            print("This industry has no previous trips")
            return {}

        return row

def get_driver_with_similar_rating(data):
    ind_rating = get_avg_ind_rating(data)
    return get_driver_with_rating(data, ind_rating)

def get_driver_with_rating_gte(data, value):
    with connection.cursor() as cursor:
        '''
            Select emailid, fname, lname, phone_num
            FROM Driver_Info where start_loc = %s and end_loc = %s amd emailid IN (
            SELECT d.emailid as emailid
            FROM Driver_Info d join Trips t on d.emailid = t.driver_email
            GROUP BY d.emailid
            HAVING avg(rating_from_industry) >= ind_rating
            )

        '''
        cursor.execute(
            "Select * FROM Driver_Info where start_loc= %s and end_loc = %s amd emailid IN ( SELECT d.emailid as emailid FROM Driver_Info d join Trips t on d.emailid=t.driver_email GROUP BY d.emailid HAVING avg(rating_from_industry) >= %s )",
            [data["start_loc"], data["end_loc"], str(value)]
        )

        rows = cursor.fetchall()
        return rows

def get_all_driver_trips(data):
    with connection.cursor() as cursor:
        '''
        SELECT *
        FROM Driver_Info d join Trips t on d.emailid = t.driver_email
        WHERE d.emailid = %s
        '''
        cursor.execute(
            "SELECT * FROM Trips WHERE driver_email= %s",
             [data["emailid"]]
        )
        rows = cursor.fetchall()
        return rows

def get_all_industry_trips(data):
    with connection.cursor() as cursor:
        '''
        SELECT *
        FROM Trips
        WHERE ind_email = %s
        '''
        cursor.execute(
            "SELECT * FROM Trips WHERE ind_email = %s",
            [data["emailid"]]
        )
        rows = cursor.fetchall()
        return rows

# In this we are only creating the trip
# the comments and ratings should come in the update
def create_trip(data):
    trip_id = gen_random_trip_id()
    with connection.cursor() as cursor:
        # on the super off chance that the trip id is duplicate redo
        cursor.execute("SELECT * FROM Trips where trip_id = %s", [trip_id])
        row = cursor.fetchall()
        if row != None:
            return create_trip(data)

        cursor.execute(
            "INSERT Into Trips(trip_id, completed, driver_email, ind_email) values(%s, 0, %s, %s)",
            [trip_id, data["driver_email"], data["ind_email"]]
        )
    return True
#In this we update completion, ratings, and comments
def update_trip(data):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Trips WHERE trip_id = %s", [data["trip_id"]])
        row = cursor.fetchall()
        if row == None:
            print("This trip does not exist")
            return False

        cursor.execute(
            "UPDATE Trips SET complete = 1, SET rating_from_driver = %s, SET rating_from_ind = %s, SET comments_from_driver = %s, SET comments_from_ind = %s WHERE trip_id = %s",
            [data["rating_from_driver"], data["rating_from_industry"],
             data["comments_from_driver"], data["comments_from_industry"], data["trip_id"]]
        )

        return True
