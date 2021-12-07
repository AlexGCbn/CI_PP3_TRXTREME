"""Main file"""

# The following section has all the imports that the app requires to work.
# datetime -> Date and time functions
# gservices -> gservices module, containing all Google services code
# REF#1:
# https://learndataanalysis.org/add-new-worksheets-to-existing-google-sheets-file-with-google-sheets-api/

import datetime
import gservices as gs
import user
import user_data as ud

# START OF USER ACTIONS


def successful_sign_in(user_class: object):
    """
    Uses user class to determine what choices to provide to user.
    For workout users, provides the option to sign up for a workout
    or see their information.
    For martial arts athletes, provides details and next workout directly.
    @param: user_class object
    """
    choice = ""
    if user_class.athlete_type == "workout":
        print(
            "\n"
            f"Welcome {user_class.first_name}! "
            "Please choose an option:"
        )
        print("1. Sign up for workout")
        print("2. View remaining workouts")
        print("3. Exit to main menu")
        choice = input("Enter choice:\n")
        if choice == "1":
            if int(user_class.workouts_left) > 0:
                workout_sign_up(user_class)
            else:
                print("!!!")
                print(
                    "You do not have enough workouts left. "
                    "Please contact the trainer!"
                )
                print("!!!\n")
                welcome()
        elif choice == "2":
            display_user_data(user_class)
        elif choice == "3":
            welcome()
        else:
            print("Incorrect choice. Please try again!")
            successful_sign_in(user_class)
    elif user_class.athlete_type == "martial arts":
        display_user_data(user_class)
    print("Returning to main menu...\n")
    welcome()


def display_user_data(user_class: object):
    """
    Provides information to user about their profile
    depending on their type.
    @param: user_class object
    """
    if user_class.athlete_type == "workout":
        print(
            "\n"
            f"Hello {user_class.first_name} {user_class.last_name}! "
            f"Your remaining workouts are {user_class.workouts_left}"
        )
    elif user_class.athlete_type == "martial arts":
        print(
            "\n"
            f"Hello {user_class.first_name} {user_class.last_name}! "
            f"Your group is {user_class.athlete_group}"
        )

        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_list = []

        user_group = str(user_class.athlete_group)
        events_result = (
            gs.CALENDAR.events()
            .list(
                calendarId=gs.CALENDAR_ID,
                timeMin=now,
                maxResults=1,
                singleEvents=True,
                q=user_group,
            )
            .execute()
        )
        events = events_result.get("items", [])
        for event in events:
            events_list.append(event["id"])
            start = event["start"].get(
                "dateTime", event["start"].get("date")
            )
            start = start.replace("T", " ").replace(":00+02:00", "")
        print(f"Your next training session is on: {start}")


def workout_sign_up(user_class: object):
    """
    Gets next 20 events.
    Filters events to find only workouts and then presents a list to user.
    When user picks an event, asks to confirm.
    If confirmed, calls the event attendees update function.
    Uses 'now' to get UTC+0 timestamp. Events are presented in GSheet time.
    @param: user_class object
    """
    now = datetime.datetime.utcnow().isoformat() + "Z"
    print("Getting upcoming events")
    events_result = (
        gs.CALENDAR.events()
        .list(
            calendarId=gs.CALENDAR_ID,
            timeMin=now,
            maxResults=20,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    index = 0
    events_list = []

    if not events:
        print("No upcoming events found.")
    for event in events:
        if "TRX" in event["summary"] or "Cross Training" in event["summary"]:
            index += 1
            events_list.append(event["id"])
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(
                index,
                "-",
                start.replace("T", " ").replace(":00+02:00", ""),
                event["summary"],
            )

    choice = input(
        "Please input the number of the workout "
        "you choose from above:\n"
    )
    event_id = events_list[int(choice) - 1]
    chosen_workout = (
        gs.CALENDAR.events()
        .get(calendarId=gs.CALENDAR_ID, eventId=events_list[int(choice) - 1])
        .execute()
    )
    start = chosen_workout["start"].get(
        "dateTime", chosen_workout["start"].get("date")
    )
    start = start.replace("T", " ").replace(":00+02:00", "")
    print("You chose the following workout:\n")
    print(f"Name: {chosen_workout['summary']}, Date: {start}")
    new_choice = input("Do you want to register? Y/N\n")
    if new_choice.lower() == "y":
        update_event_attendees(event_id, "sign_up", user_class)
    elif new_choice.lower() == "n":
        successful_sign_in(user_class)


def update_event_attendees(event_id: str, operation: str, user_class: object):
    """
    Checks to see if there is a worksheet with the event ID as name.
    If not, creates one.
    If there is, adds username to worksheet.
    @param: event_id str
    @param: operation str
    @param: user_class object
    """
    if operation == "sign_up":
        try:
            sheet_check = gs.SHEET.worksheet(event_id)
        except:
            sheet_check = None
        if sheet_check is None:
            # Credits: start of code, REF#1
            new_sheet = {
                "requests": [{"addSheet": {"properties": {"title": event_id}}}]
            }
            gs.SHEET.batch_update(body=new_sheet)
        usernames = gs.SHEET.worksheet(event_id).col_values(1)
        if user_class.username in usernames:
            print("!!!")
            print(
                "You are already registered for this workout! "
                "Returning to main menu."
            )
            print("!!!\n")
            welcome()
        else:
            print("Signing up for workout...\n")
            updated_worksheet = gs.SHEET.worksheet(event_id)
            updated_worksheet.append_row([user_class.username])
            ud.update_workout(user_class)
            print("!!!")
            print(
                "Successfully signed up for workout! "
                "Returning to main menu."
            )
            print("!!!\n")
            welcome()


# END OF USER ACTIONS


def verify_username():
    """
    Uses username to check if user exists on Google Sheet.
    If user exists, calls the function update_user_class
    to create the user object.
    Then it calls the email verification function.
    """
    while True:
        username = input("Enter username or 'exit' to return to menu:\n")
        index = user.find_user_index(username, "username")
        if username == "exit":
            welcome()
        elif index > 0:
            user_class = ud.update_user_class(index)
            verify_email(user_class)
            break
        else:
            print("Username incorrect!")


def verify_email(user_class: object):
    """
    Takes the user object,
    asks the user for the email and verifies if it is correct.
    If so, it passes the user object to the next function.
    @param: user_class object
    """
    while True:
        email = input(
            "Please input your email or type 'exit' to return to main menu:\n"
        )
        index = user.find_user_index(email, "email")
        if email == "exit":
            welcome()
        elif index > 0:
            successful_sign_in(user_class)
            break
        else:
            print("Email incorrect!")


# START OF SIGN UP


def martial_sign_up(choice: str, new_user: list) -> list:
    """
    Gets the user's choice of martial arts class
    Checks if there is room for more athletes (<12)
    Returns the user instance with appropriate data
    @param: choice str
    @param: new_user list
    """
    level_count = 0
    if choice == "1":
        counters = []
        index = 0
        counters.append(ud.count_athletes("Junior 1"))
        counters.append(ud.count_athletes("Junior 2"))
        counters.append(ud.count_athletes("Junior 3"))
        for counter in counters:
            index += 1
            if counter < 12:
                new_user.append("Junior "+str(index))
                break
    elif choice == "2":
        new_user.append("Teenage MA")
    elif choice == "3":
        new_user.append("Adult MA")
    elif choice == "4":
        new_user.append("Professional MA")
    else:
        print("Incorrect choice. Returning to user creation.\n")
        sign_up()
    level_count = ud.count_athletes(new_user[6])
    if level_count >= 12:
        print(
            "Too many athletes in selected level. "
            "Please contact the trainer!"
        )
        print("Returning to main menu...\n")
        welcome()
    return new_user


def sign_up():
    """
    Creates a new user from the parameters provided.
    """
    while True:
        username = input("Please enter your new username:\n")
        user_exists = user.find_user_index(username, "username")
        if username.lower() == "exit":
            welcome()
        elif user_exists > 0:
            print(
                "Username already in use."
                " Please use a different username or type"
                " 'exit' to go to main menu."
            )
        elif len(username) < 4 or len(username) > 15:
            print(
                "Username should be between 4 and 15 characters. "
                "Please try again."
            )
        else:
            break
    while True:
        email = input("Please enter your email:\n")
        email_exists = user.find_user_index(username, "username")
        if email.lower() == "exit":
            welcome()
        elif email_exists > 0:
            print(
                "Email already in use. Please try again or "
                "type 'exit' to go to main menu."
            )
        elif len(email) < 10 or len(email) > 50:
            print(
                "Email should be between 10 and 50 characters. "
                "Please try again."
            )
        else:
            break
    first_name = input("Please enter your first name:\n")
    while True:
        if len(first_name) >= 2 and len(first_name) <= 30:
            break
        else:
            first_name = input(
                "Name cannot be less than 2 letters or more than 30."
                " Please try again.\n"
            )
    last_name = input("Please enter your last name:\n")
    while True:
        if len(last_name) >= 2 and len(last_name) <= 30:
            break
        else:
            last_name = input(
                "Last name cannot be less than 2 letters or more than 30."
                " Please try again.\n"
            )
    new_user = [username, email, first_name, last_name]

    while True:
        print("Are you signing up for workouts or martial arts?")
        choice = input("Please input 1 for workouts and 2 for martial arts:\n")

        if choice == "1":
            new_user.append("workout")
            new_user.append(0)
            break
        elif choice == "2":
            new_user.append("martial arts")
            new_user.append("")
            level_choice = input(
                "Please enter 1 for Junior level, 2 for Teenage, "
                "3 for Adult or 4 for Professional:\n"
            )
            new_user = martial_sign_up(level_choice, new_user)
            break
        else:
            print("Incorrect choice! Please try again.")

    updated_worksheet = gs.SHEET.worksheet("users")
    updated_worksheet.append_row(new_user)

    print(
        "Sign up complete! Please speak with the trainer to begin attending!"
    )
    print("Returning to main menu...\n")
    welcome()


# END OF SIGN UP

# START OF ADMIN ACTIONS


def view_attendees(events_list: list):
    """
    Provides option to choose an event to view the attendees
    @param: events_list list
    """
    choice = input(
        "Please input the number of the workout you "
        "choose from above, or type 'exit' to return:\n"
    )
    if choice.lower() != "exit":
        event_id = events_list[int(choice) - 1]
        chosen_workout = (
            gs.CALENDAR.events()
            .get(calendarId=gs.CALENDAR_ID, eventId=events_list[int(choice)-1])
            .execute()
        )
        start = chosen_workout["start"].get(
            "dateTime", chosen_workout["start"].get("date")
        )
        start = start.replace("T", " ").replace(":00+02:00", "")
        print("You chose the following workout:")
        print(f"Name: {chosen_workout['summary']}, Date: {start}")
        try:
            sheet_check = gs.SHEET.worksheet(event_id)
        except:
            sheet_check = None
        if (
            "TRX" in chosen_workout["summary"] or
            "Cross Training" in chosen_workout["summary"]
        ):
            if sheet_check is None:
                print("There are no registered users for this class.\n")
            else:
                print("The following users are registered:")
                usernames = gs.SHEET.worksheet(
                    chosen_workout["id"]
                ).col_values(1)
                for username in usernames:
                    print(username)
            print("\n")
        else:
            print("The following users are registered:")
            index = 0
            ma_users = gs.SHEET.worksheet("users").col_values(7)
            usernames = gs.SHEET.worksheet("users").col_values(1)
            for ma_user in ma_users:
                index += 1
                if ma_user == chosen_workout["summary"]:
                    print(usernames[index - 1])
            print("\n")


def get_events():
    """
    Gets a date from admin and displays the schedule for the day.
    Provides the option to see who is in each workout/class.
    """
    chosen_year = input("Provide year (YYYY):\n")
    chosen_month = input("Provide month (MM):\n")
    chosen_day = input("Provide date (DD):\n")
    try:
        new_date = (
            datetime.datetime(
                int(chosen_year), int(chosen_month), int(chosen_day)
            ).isoformat() + "Z"
        )
    except ValueError:
        print("Date incorrect. Please try again!")
        get_events()
    date_no_time = new_date.replace("T00:00:00Z", "")
    print(date_no_time)

    print(f"Getting events for date {date_no_time}...")
    events_result = (
        gs.CALENDAR.events()
        .list(
            calendarId=gs.CALENDAR_ID,
            timeMin=new_date,
            maxResults=20,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    index = 0
    events_list = []

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        if date_no_time in start:
            index += 1
            events_list.append(event["id"])
            print(
                index,
                "-",
                start.replace("T", " ").replace(":00+02:00", ""),
                event["summary"],
            )
    if index != 0:
        view_attendees(events_list)
    else:
        print("No upcoming events found.\n")
    admin_actions()


def admin_edit_user_menu(index: int, user_class: object):
    """
    Gets user index and the created object to
    provide change options and call next function.
    @param: index int
    @param: user_class object
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
        ud.edit_item(index, user_class, "username")
    elif choice == "2":
        ud.edit_item(index, user_class, "email")
    elif choice == "3":
        ud.edit_item(index, user_class, "first_name")
    elif choice == "4":
        ud.edit_item(index, user_class, "last_name")
    elif choice == "5":
        if user_class.athlete_type == "workout":
            ud.edit_item(index, user_class, "workouts_left")
        else:
            ud.edit_item(index, user_class, "athlete_group")
    admin_actions()


def admin_display_user_data():
    """
    Displays chosen user data and provides options to change it.
    """
    username = input(
        "Please provide user's username or type 'exit' to go back:\n"
    )
    user_index = user.find_user_index(username, "username")
    if username.lower() == "exit":
        admin_actions()
    elif user_index == 0:
        print("Username incorrect. Please try again.")
        admin_display_user_data()
    else:
        print("User found! Fetching data...\n")
        user_class = ud.update_user_class(user_index)
        print(f"You have chosen username '{user_class.username}':")
        print(f"Full name: {user_class.first_name} {user_class.last_name}")
        print(f"Email: {user_class.email}")
        print(f"Athlete type: {user_class.athlete_type}")
        if user_class.athlete_type == "workout":
            print(f"Workouts remaining: {user_class.workouts_left}\n")
        else:
            print(f"Martial arts group: {user_class.athlete_group}\n")
        print(
            "Would you like to change the user's data "
            "or go back to the previous menu?"
        )
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
        get_events()
    elif choice == "3" or choice.lower() == "exit":
        welcome()
    else:
        print("Incorrect choice. Returning to options...")
        admin_actions()


def admin_sign_in():
    """
    Asks for admin username and password.
    Then calls admin actions function if successfully signed in.
    """
    admin_username = gs.SHEET.worksheet("users").col_values(10)
    admin_password = gs.SHEET.worksheet("users").col_values(11)
    while True:
        username = input("Greetings admin! Please provide your username:\n")
        if username in admin_username:
            password = input("Please enter the admin password:\n")
            if password in admin_password:
                admin_actions()
                break
            print("Password incorrect. Please try again!")
        else:
            print("Username incorrect. Please try again!")


# END OF ADMIN ACTIONS


def welcome():
    """
    Welcome function used to provide user with
    choice of admin/athlete sign in, or sign up.
    Calls appropriate functions according to user choice.
    """
    print("----")
    print("Welcome to TRXtreme! Please choose an option:\n")

    print("1. Sign in (Already a user)")
    print("2. Sign up (Not a user)")
    print("3. Admin sign in")

    user_answer = input("Enter choice:\n")

    if user_answer == "1":
        verify_username()
    elif user_answer == "2":
        sign_up()
    elif user_answer == "3":
        admin_sign_in()
    else:
        print(
            f"{user_answer} is not an acceptable key. Please try again.\n"
        )
        welcome()


welcome()
