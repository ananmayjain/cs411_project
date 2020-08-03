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
    phone_num VarChar(10),
    license_num VarChar(30),
    start_loc VarChar(30),
    end_loc VarChar(30),
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

Create Table active_sessions (
    session_id VarChar(256) NOT NULL,
    emailid VarChar(120) NOT NULL,
    valid_till DATETIME NOT NULL,
    Primary Key (session_id)
);

'''

from django.db import connection
import hashlib
import datetime
import threading
from cs411_project.dbs import server

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

        cmd = 'Insert Into User_Accounts Values ("%s", "%s", "%s")' % \
            (data["emailid"], data["passwd"], data["type_of_acc"])
        client_num = getClientNum(data["emailid"])
        server.pushData(client_num, cmd)
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

        cmd = 'Delete from User_Accounts where emailid = "%s"' % data["emailid"]
        client_num = getClientNum(data["emailid"])
        server.pushData(client_num, cmd)
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


        cmd = 'Insert Into Driver_Info Values ("%s", "%s", "%s", "%s", "%s", "%s", "%s")' % \
            (data["emailid"], data["fname"], data["lname"], data["phone_num"],
            data["license_num"], data["start_loc"], data["end_loc"])
        client_num = getClientNum(data["emailid"])
        server.pushData(client_num, cmd)

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

        client_num = getClientNum(data["emailid"])
        server.pushData(client_num, cmd)
        cursor.execute(cmd)
        return True

def get_driver_info(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from Driver_Info where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # Driver acc not present in database, SANITY CHECK
        if row == None:
            print("SANITY CHECK Driver info not present")

            cmd = 'Insert Into Driver_Info Values ("%s", "%s", "%s", "%s", "%s", "%s", "%s")' % \
                (data["emailid"], "", "", "", "", "", "")
            client_num = getClientNum(data["emailid"])
            server.pushData(client_num, cmd)
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

        cmd = 'Insert Into Ind_Info Values ("%s", "%s", "%s", "%s", "%s")' % \
            (data["emailid"], data["fname"], data["lname"], data["ind_name"], data["phone_num"])
        client_num = getClientNum(data["emailid"])
        server.pushData(client_num, cmd)
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

        client_num = getClientNum(data["emailid"])
        server.pushData(client_num, cmd)

        cursor.execute(cmd)
        return True

def get_industry_info(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from Ind_Info where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # Driver acc not present in database, SANITY CHECK
        if row == None:
            print("SANITY CHECK Driver info not present")

            cmd = 'Insert Into Ind_Info Values ("%s", "%s", "%s", "%s", "%s")' % \
                (data["emailid"], "", "", "", "")

            client_num = getClientNum(data["emailid"])
            server.pushData(client_num, cmd)

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

def getClientNum(data):
    hex = hashlib.sha256(str(data).encode()).hexdigest()
    return int(hex, 16) % 4

def importDataToClients():
    pass
