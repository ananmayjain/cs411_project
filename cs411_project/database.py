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

'''


''' Command TEMPLATES '''
insert_user_acc = "Insert Into User_Accounts values (%s, %s, %s, %s, %s, %d, %d)"

from django.db import connection

DEBUG = 1

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
            return False

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

        cursor.execute("Insert Into Driver_Info Values (%s, %s, %s, %s)",
            [data["emailid"], data["fname"], data["lname"], data["license_num"]]
        )

        return True

def update_driver_info(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from Driver_Info where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # Driver acc not present in database, SANITY CHECK
        if row == None:
            return False

        cmd = "Update Driver_Info"
        for key in data.keys():
            if key != "emailid":
                cmd += " set " + str(key) + " = " + str(data[key])
        cmd += " where emailid = " + str(data["emailid"])

        if DEBUG:
            print(cmd)
            
        cursor.execute(cmd)

def print_driver_info(data):
    with connection.cursor() as cursor:
        cursor.execute("Select * from Driver_Info where emailid = %s", [data["emailid"]])

        row = cursor.fetchone()
        # Driver acc not present in database, SANITY CHECK
        if row == None:
            return False

        print(row)
        return True
