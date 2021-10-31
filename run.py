"""
Main file
"""

from re import U
from pprint import pprint
import gspread
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
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

def successful_sign_in(user_class):
    """
    Uses user class to determine what choices to provide to user.
    For workout users, provides the option to sign up for a workout or see their information.
    For martial arts athletes, provides details and next workout directly.
    """
    choice = ""

    if user_class.athlete_type == "workout":
        choice = input(f"Welcome {user_class.first_name}! Input 1 if you want to sign up for a workout or 2 if you want to see how many you have left for the month:\n")
        if choice == "1":
            # date = input("Please provide date in format 'YYYY-MM-DD':\n")
            # date += "T23:59:59B"
            # print(date)
            # events = 
            now = datetime.datetime.utcnow().isoformat() + "Z"
            print(now)
            print("Getting upcoming events")
            events_result = CALENDAR.events().list(calendarId=CALENDAR_ID, timeMin=now, maxResults=10, singleEvents = False).execute()
            events = events_result.get('items', [])

            
            if not events:
                print('No upcoming events found.')
            for event in events:
                if "TRX" in event['summary'] or "Cross Training" in event['summary']:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    print(start.replace("T", " ").replace(":00+03:00", ""), event['summary'])

def update_user_class(ind):
    """
    Uses the passed index number to find user on Google Sheet and create the user object.
    """
    values = SHEET.worksheet("users").row_values(ind)
    if values[4] == "workout":
        user_class = Workout_User(values[0], values[1], values[2], values[3], values[4], values[5])
    elif values[4] == "martial-arts":
        user_class = Martial_Arts_User(values[0], values[1], values[2], values[3], values[4], values[6])
    return user_class

def sign_in():
    """
    Sign in function. Uses username to check if user exists on Google Sheet.
    If user exists, calls the function update_user_class to create the user object.
    Uses the email there to verify the user.
    """
    username = input("Enter username:\n")
    usernames = SHEET.worksheet("users").col_values(1)
    email = ""
    index = 0
    user_class = {}

    for ind in usernames:
        if username == ind:
            user_class = update_user_class(index+2)
            break
    
    email = input("Please input your email:\n")

    if email != user_class.email:
        while True:
            email = input("Email incorrect. Please try again, or type 'exit' to go to main page.\n")
            if email == "exit":
                welcome()
                break
            elif email == user_class.email:
                successful_sign_in(user_class)
                break
    elif email == user_class.email:
        successful_sign_in(user_class)

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
            break
        elif user_answer.lower() == "a":
            admin_sign_in()
            break
        elif user_answer.lower() == "s":
            sign_up()
            break
        elif user_answer.lower() == "exit":
            break
        else:
            print(f"{user_answer} is not an acceptable key. Please choose a correct one.\n")

def main():
    """
    Main function used to run all necessary program functions.
    """
    welcome()

main()