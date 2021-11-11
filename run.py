"""
Main file
"""
import gspread
import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from pyasn1.type.univ import Null

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
SHEET_ID = "1izyPTgGIt_uKegNn2I0lFUdrAuXPJisNeXgvzN2EG_g"
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

def find_user_index(data, type):
    """
    Function to check if username or email exists.
    It was created as it needs to be called multiple times.
    It gets the data and the type, looks for the data in the appropriate column depending on type and returns an index number.
    """
    index = 0
    if type == "username":
        usernames = SHEET.worksheet("users").col_values(1)
        if data in usernames:
            for username in usernames:
                index += 1
                if username == data:
                    break
    elif type == "email":
        emails = SHEET.worksheet("users").col_values(2)
        if data in emails:
            for email in emails:
                index += 1
                if email == data:
                    break
    return index

"""
START OF USER ACTIONS -------------------------------------------------------------------------
"""

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
            if int(user_class.workouts_left) > 0:
                workout_sign_up(user_class)
            else:
                print("!!!")
                print("You do not have enough workouts left. Please contact the trainer!")
                print("!!!\n")
                welcome()
        elif choice == "2":
            display_user_data(user_class)
    elif user_class.athlete_type == "martial arts":
        display_user_data(user_class)

def display_user_data(user_class):
    """
    Provides information to user about their profile depending on their type.
    """
    if user_class.athlete_type == "workout":
        print(f"Hello {user_class.first_name} {user_class.last_name}! Your remaining workouts are {user_class.workouts_left}")
    elif user_class.athlete_type == "martial arts":
        print(f"Hello {user_class.first_name} {user_class.last_name}! Your group is {user_class.athlete_group}")

        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_list = []

        if user_class.athlete_group == "Junior 1":
            events_result = CALENDAR.events().list(calendarId=CALENDAR_ID, timeMin=now, maxResults=1, singleEvents=True, q="Junior 1").execute()
            events = events_result.get('items', [])
            for event in events:
                events_list.append(event['id'])
                start = event['start'].get('dateTime', event['start'].get('date'))
                start = start.replace("T", " ").replace(":00+02:00", "")
            print(f"Your next training session is on: {start}")

def workout_sign_up(user_class):
    """
    Gets next 20 events. Filters events to find only workouts and then presents a list to user.
    When user picks an event, asks to confirm. If confirmed, calls the event attendees update function.
    Uses 'now' to get UTC+0 timestamp. Events are presented in GSheet time.
    """
    now = datetime.datetime.utcnow().isoformat() + "Z"
    print("Getting upcoming events")
    events_result = CALENDAR.events().list(calendarId=CALENDAR_ID, timeMin=now, maxResults=20, singleEvents=True, orderBy="startTime").execute()
    events = events_result.get('items', [])

    index = 0
    events_list = []

    if not events:
        print('No upcoming events found.')
    for event in events:
        if "TRX" in event['summary'] or "Cross Training" in event['summary']:
            index += 1
            events_list.append(event['id'])
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(index, "-", start.replace("T", " ").replace(":00+02:00", ""), event['summary'])
    
    choice = input("Please input the number of the workout you choose from above:\n")
    event_id = events_list[int(choice)-1]
    chosen_workout = CALENDAR.events().get(calendarId=CALENDAR_ID, eventId=events_list[int(choice)-1]).execute()
    start = chosen_workout['start'].get('dateTime', chosen_workout['start'].get('date'))
    start = start.replace("T", " ").replace(":00+02:00", "")
    print("You chose the following workout:\n")
    print(f"Name: {chosen_workout['summary']}, Date: {start}")
    new_choice = input("Do you want to register? Y/N\n")
    if new_choice.lower() == 'y':
        update_event_attendees(event_id, "sign_up", user_class)
    elif new_choice.lower() == "n":
        successful_sign_in(user_class)

def update_workout(user_class, action):
    """
    Gets an action to either add or remove a workout to the user.
    Updates the row of the selected user to add the new value.
    """

    index = str(find_user_index(user_class.username, "username"))
    new_range = "users!A"+index
    new_value = int(user_class.workouts_left) - 1

    if action == "remove":
        SHEET.values_update(
            new_range,
            params={
                'valueInputOption': 'USER_ENTERED'
            },
            body={
                'values': [[user_class.username, user_class.email, user_class.first_name, user_class.last_name, user_class.athlete_type, new_value]]
            }
        )
        

def update_event_attendees(event_id, operation, user_class):
    """
    Checks to see if there is a worksheet with the event ID as name. 
    If not, creates one.
    If there is, adds username to worksheet.
    """
    if operation == "sign_up":
        try:
            sheet_check = SHEET.worksheet(event_id)
        except:
            sheet_check = Null
        if sheet_check == Null:
            # Credits to: https://learndataanalysis.org/add-new-worksheets-to-existing-google-sheets-file-with-google-sheets-api/
            new_sheet = {
                "requests": [{
                    "addSheet": {
                        "properties": {
                            "title": event_id
                        }
                    }
                }]
            }
            SHEET.batch_update(body=new_sheet)
        usernames = SHEET.worksheet(event_id).col_values(1)
        if user_class.username in usernames:
            print("!!!")
            print("You are already registered for this workout! Returning to main menu.")
            print("!!!\n")
            welcome()
        else:
            print("Signing up for workout...\n")
            updated_worksheet = SHEET.worksheet(event_id)
            updated_worksheet.append_row([user_class.username])
            update_workout(user_class, "remove")
            print("!!!")
            print("Successfully signed up for workout! Returning to main menu.")
            print("!!!\n")
            welcome()

"""
END OF USER ACTIONS -------------------------------------------------------------------------
"""

def update_user_class(ind):
    """
    Uses the passed index number to find user on Google Sheet and create the user object.
    """
    values = SHEET.worksheet("users").row_values(ind)
    if values[4] == "workout":
        user_class = Workout_User(values[0], values[1], values[2], values[3], values[4], values[5])
    elif values[4] == "martial arts":
        user_class = Martial_Arts_User(values[0], values[1], values[2], values[3], values[4], values[6])
    return user_class

def verify_username():
    """
    Uses username to check if user exists on Google Sheet.
    If user exists, calls the function update_user_class to create the user object.
    Then it calls the email verification function.
    """
    while True:
        username = input("Enter username or 'exit' to return to menu:\n")
        index = find_user_index(username, "username")
        if username == "exit":
            welcome()
        elif index > 0:
            user_class = update_user_class(index)
            verify_email(user_class)
            break
        else:
            print("Username incorrect!")
    

def verify_email(user_class):
    """
    Takes the user object, asks the user for the email and verifies if it is correct.
    If so, it passes the user object to the next function.
    """
    while True:
        email = input("Please input your email or type 'exit' to return to main menu:\n")
        index = find_user_index(email, "email")
        if email == "exit":
            welcome()
        elif index > 0:
            successful_sign_in(user_class)
            break
        else:
            print("Email incorrect!")

"""
START OF SIGN UP
"""

def sign_up():
    """
    Creates a new user from the parameters provided.
    """
    while True:
        username = input("Please enter your new username:\n")
        user_exists = find_user_index(username, "username")
        if username.lower() == "exit":
            welcome()
        elif user_exists > 0:
            print("Username already in use. Please use a different username or type 'exit' to go to main menu.")
        else:
            break
    while True:
        email = input("Please enter your email:\n")
        email_exists = find_user_index(username, "username")
        if email.lower() == "exit":
            welcome()
        elif email_exists > 0:
            print("Email already in use. Please try again or type 'exit' to go to main menu.")
        else:
            break
    first_name = input("Please enter your new first name:\n")
    last_name = input("Please enter your last name:\n")
    new_user = [username, email, first_name, last_name]

    print("Are you signing up for workouts or martial arts?")
    choice = input("Please input 1 for workouts and 2 for martial arts:\n")
    
    if choice == "1":
        new_user.append("workout")
        new_user.append(0)
    elif choice == "2":
        new_user.append("martial arts")
        new_user.append("")
        level_choice = input("Please enter 1 for Junior level, 2 for Teenage, 3 for Adult or 4 for Professional:\n")
        level_athletes = SHEET.worksheet("users").col_values(7)
        level_count = 0
        if level_choice == "1":
            new_user.append("Junior 1")
            for athlete in level_athletes:
                if athlete == "Junior 1":
                    level_count += 1
            if level_count >= 12:
                new_user.pop()
                new_user.append("Junior 2")
                level_count = 0
                for athlete in level_athletes:
                    if athlete == "Junior 2":
                        level_count += 1
                if level_count >= 12:
                    new_user.pop()
                    new_user.append("Junior 3")
                    level_count = 0
                    for athlete in level_athletes:
                        if athlete == "Junior 3":
                            level_count += 1
                    if level_count >= 12:
                        print("Too many athletes in selected level. Please contact the trainer!")
        elif level_choice == "2":
            new_user.append("Teenage MA")
            for athlete in level_athletes:
                if athlete == "Teenage MA":
                    level_count += 1
        elif level_choice == "3":
            new_user.append("Adult MA")
            for athlete in level_athletes:
                if athlete == "Adult MA":
                    level_count += 1
        elif level_choice == "4":
            new_user.append("Professional MA")
            for athlete in level_athletes:
                if athlete == "Professional MA":
                    level_count += 1
            if level_count >= 12:
                    print("Too many athletes in selected level. Please contact the trainer!")
        else:
            print("Incorrect choice. Returning to user creation.\n")
            sign_up()
    
    print(new_user)
    updated_worksheet = SHEET.worksheet("users")
    updated_worksheet.append_row(new_user)

    print("Sign up complete! Please speak with the trainer to begin attending!")

"""
END OF SIGN UP
"""

"""
START OF ADMIN ACTIONS -------------------------------------------------------------------------
"""

def view_workouts():
    """
    Gets a date from admin and displays the schedule for the day.
    Provides the option to see who is in each workout/class.
    """
    chosen_year = input("Provide year (YYYY):\n")
    chosen_month = input("Provide month (MM):\n")
    chosen_day = input("Provide date (DD):\n")
    try:
        new_date = datetime.datetime(int(chosen_year), int(chosen_month), int(chosen_day)).isoformat() + "Z"
    except ValueError:
        print("Date incorrect. Please try again!")
        view_workouts()
    date_no_time = new_date.replace("T00:00:00Z", "")
    print(date_no_time)

    print(f"Getting events for date {date_no_time}...")
    events_result = CALENDAR.events().list(calendarId=CALENDAR_ID, timeMin=new_date, maxResults=20, singleEvents=True, orderBy="startTime").execute()
    events = events_result.get('items', [])
    index = 0
    events_list = []

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if date_no_time in start:
            index += 1
            events_list.append(event['id'])
            print(index, "-", start.replace("T", " ").replace(":00+02:00", ""), event['summary'])
    
    choice = input("Please input the number of the workout you choose from above:\n")
    event_id = events_list[int(choice)-1]
    chosen_workout = CALENDAR.events().get(calendarId=CALENDAR_ID, eventId=events_list[int(choice)-1]).execute()
    start = chosen_workout['start'].get('dateTime', chosen_workout['start'].get('date'))
    start = start.replace("T", " ").replace(":00+02:00", "")
    print("You chose the following workout:")
    print(f"Name: {chosen_workout['summary']}, Date: {start}")
    try:
        sheet_check = SHEET.worksheet(event_id)
    except:
        sheet_check = Null
    if "TRX" in chosen_workout["summary"] or "Cross Training" in chosen_workout["summary"]:
        if sheet_check == Null:
            print("There are no registered users for this class.\n")
        else:
            print("The following users are registered:")
            usernames = SHEET.worksheet(chosen_workout["id"]).col_values(1)
            for username in usernames:
                print(username)
        print("\n")
    else:
        print("The following users are registered:")
        index = 0
        ma_users = SHEET.worksheet("users").col_values(7)
        usernames = SHEET.worksheet("users").col_values(1)
        for ma_user in ma_users:
            index += 1
            if ma_user == chosen_workout["summary"]:
                print(usernames[index-1])
        print("\n")
    admin_actions()


def edit_item(index, user_class, item):
    """
    Gets user index, the created object and the item to change.
    Changes the item in the object so it can be returned to the GSheet.
    """
    new_range = "users!A"+str(index)
    new_value = input("Provide new value:\n")
    setattr(user_class, item, new_value)
    item_str = item.replace("_", " ").capitalize()
    if user_class.athlete_type == "workout":
        SHEET.values_update(
            new_range,
            params={
                'valueInputOption': 'USER_ENTERED'
            },
            body={
                'values': [[user_class.username, user_class.email, user_class.first_name, user_class.last_name, user_class.athlete_type, user_class.workouts_left]]
            }
        )
        print(f"{item_str} updated!")
    else:
        SHEET.values_update(
            new_range,
            params={
                'valueInputOption': 'USER_ENTERED'
            },
            body={
                'values': [[user_class.username, user_class.email, user_class.first_name, user_class.last_name, user_class.athlete_type, "", user_class.athlete_group]]
            }
        )
        print(f"{item_str} updated!")


def admin_edit_user_menu(index, user_class):
    """
    Gets user index and the created object to provide change options and call next function.
    """
    print("What do you want to edit?")
    print("1. Username")
    print("2. Email")
    print("3. First name")
    print("4. Last name")
    if user_class.athlete_type == "workout":
        print("5. Workouts left")
    else:
        print("5. Athlete group")
    print("6. Exit to menu")

    choice = input("Input choice:\n")
    if choice == "6":
        admin_actions()
    elif choice == "1":
        edit_item(index, user_class, "username")
    elif choice == "2":
        edit_item(index, user_class, "email")
    elif choice == "3":
        edit_item(index, user_class, "first_name")
    elif choice == "4":
        edit_item(index, user_class, "last_name")
    elif choice == "5":
        if user_class.athlete_type == "workout":
            edit_item(index, user_class, "workouts_left")
        else:
            edit_item(index, user_class, "athlete_group")

def admin_display_user_data():
    """
    Displays chosen user data and provides options to change it.
    """
    username = input("Please provide user's username or type 'exit' to go back:\n")
    user_index = find_user_index(username, "username")
    if username.lower() == "exit":
        admin_actions()
    elif user_index == 0:
        print("Username incorrect. Please try again.")
        admin_display_user_data()
    else:
        print("User found! Fetching data...\n")
        user_class = update_user_class(user_index)
        print(f"You have chosen username '{user_class.username}':")
        print(f"Full name: {user_class.first_name} {user_class.last_name}")
        print(f"Email: {user_class.email}")
        print(f"Athlete type: {user_class.athlete_type}")
        if user_class.athlete_type == "workout":
            print(f"Workouts remaining: {user_class.workouts_left}\n")
        else:
            print(f"Martial arts group: {user_class.athlete_group}\n")
        print("Would you like to change the user's data or go back to the previous menu?")
        choice = input("Input 1 to edit or any other key to go back:\n")
        if choice == "1":
            admin_edit_user_menu(user_index, user_class)
        else:
            admin_actions()


def admin_actions():
    """
    Provides admin with options of what they can do.
    Calls appropriate functions.
    """
    print("Welcome admin! Please choose what you want to do:")
    print("1. View and edit user account information.")
    print("2. View workouts.")
    print("3. Exit to main menu.")
    choice = input("What is your choice?\n")

    if choice == "1":
        admin_display_user_data()
    elif choice == "2":
        view_workouts()
    elif choice == "3" or choice.lower() == "exit":
        welcome()
    else:
        print("Incorrect choice. Returning to options...")
        admin_actions()

def admin_sign_in():
    """
    Asks for admin username and password, then calls admin actions function if successfully signed in.
    """
    admin_username = SHEET.worksheet("users").col_values(10)
    admin_password = SHEET.worksheet("users").col_values(11)
    while True:
        username = input("Greetings admin! Please provide your username:\n")
        if username in admin_username:
            password = input("Please enter the admin password:\n")
            if password in admin_password:
                admin_actions()
                break
            else:
                print("Password incorrect. Please try again!")
        else:
            print("username incorrect. Please try again!")


"""
END OF ADMIN ACTIONS -------------------------------------------------------------------------
"""

def welcome():
    """
    Welcome function used to provide user with choice of admin/athlete sign in, or sign up.
    Calls appropriate functions according to user choice.
    """
    print("Welcome to TRXtreme! Please choose an option:\n")

    while True:
        print("1. Sign in (Already a user)")
        print("2. Sign up (Not a user)")
        print("3. Admin sign in")
        print("4. Terminate program\n")
        
        user_answer = input("Enter choice:\n")

        if user_answer == "1":
            verify_username()
            break
        elif user_answer == "2":
            sign_up()
            break
        elif user_answer == "3":
            admin_sign_in()
            break
        elif user_answer == "4" or user_answer.lower() == "exit":
            quit()
        else:
            print(f"{user_answer} is not an acceptable key. Please choose a correct one.\n")

welcome()