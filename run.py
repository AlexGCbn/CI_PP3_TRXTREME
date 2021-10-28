"""
Main file
"""

import gspread
import datetime
import os.path
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("trxtreme")
CALENDAR = build("calendar", "v3", credentials = CREDS)
CALENDAR_ID = "trxtreme2021@gmail.com"

def welcome():
    """
    Welcome function used to provide user with choice of admin/athlete sign in, or sign up.
    Calls appropriate functions according to user choice.
    """
    print("Welcome to TRXtreme.\n")

    while True:
        print("To sign in as a user, please input the letter u and enter.")
        print("To sign in as admin, please input the letter a and enter.")
        print("To sign up, please input the letter s and enter.\n")
        
        user_answer = input("Enter choice:\n")

        if user_answer.lower() == "u":
            sign_in()
        elif user_answer.lower() == "a":
            admin_sign_in()
        elif user_answer.lower() == "s":
            sign_up()
        elif user_answer.lower() == "exit":
            break
        else:
            print(f"{user_answer} is not an acceptable key. Please choose a correct one.\n")

            
def check_username(username):
    """
    Checks if username exists in the first column of the users worksheet.
    """
    values = SHEET.worksheet("users").col_values(1)
    if username in values:
        return True
    else:
        return False

def sign_in():
    username = input("Enter username:\n")
    user_exists = check_username(username)
    if user_exists:



def main():
    """
    Main function used to run all necessary program functions.
    """
    welcome()

main()