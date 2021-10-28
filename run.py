"""
Main file
"""

from re import U
from pprint import pprint
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

class User:
    """
    Base user class that will pull data from Google Sheets when called.
    """
    def __init__(self, username, email, first_name, last_name, athlete_type):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.athlete_type = athlete_type

class Workout_User(User):
    """
    Workout user class that has an extra "workouts left" attribute that counts how many times they can work out.
    """
    def __init__(self, username, email, first_name, last_name, athlete_type, workouts_left):
        super().__init__(username, email, first_name, last_name, athlete_type)
        self.workouts_left = workouts_left

class Martial_Arts_User(User):
    """
    Martial arts user class that has the user's athlete group, which dictates which dates they will join."
    """
    def __init__(self, username, email, first_name, last_name, athlete_type, athlete_group):
        super().__init__(username, email, first_name, last_name, athlete_type)
        self.athlete_group = athlete_group

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

def sign_in():
    """
    Sign in function. Calls username check function and then asks for email.
    """
    username = input("Enter username:\n")
    usernames = SHEET.worksheet("users").col_values(1)
    emails = SHEET.worksheet("users").col_values(2)
    print(emails)
    index = 0
    user_class = {}

    for ind in usernames:
        if username == ind:
            user_class = update_user_class(index+2)
    
    pprint(vars(user_class))

    # for ind in usernames:
    #     index += 1
    #     if username == ind:
    #         print(index)
    #         email = input("Please provide your email:\n")
    #         if email == emails[index-1]:
    #             print("Sign in successful!\n")
    #             user_actions(username)
    #         else:
    #             print("Email incorrect. Please try again!")
    #             continue

def update_user_class(ind):
    print(ind)
    values = SHEET.worksheet("users").row_values(ind)
    if values[4] == "workout":
        user_class = Workout_User(values[0], values[1], values[2], values[3], values[4], values[5])
        return user_class


def main():
    """
    Main function used to run all necessary program functions.
    """
    welcome()

main()