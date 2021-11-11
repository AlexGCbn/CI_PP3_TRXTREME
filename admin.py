"""
Admin options file
"""
import run

def view_workouts():
    """
    Gets a date from admin and displays the schedule for the day.
    Provides the option to see who is in each workout/class.
    """
    chosen_year = input("Provide year (YYYY):\n")
    chosen_month = input("Provide month (MM):\n")
    chosen_day = input("Provide date (DD):\n")
    try:
        new_date = run.datetime.datetime(int(chosen_year), int(chosen_month), int(chosen_day)).isoformat() + "Z"
    except ValueError:
        print("Date incorrect. Please try again!")
        view_workouts()
    date_no_time = new_date.replace("T00:00:00Z", "")
    print(date_no_time)

    print(f"Getting events for date {date_no_time}...")
    events_result = run.CALENDAR.events().list(calendarId=run.CALENDAR_ID, timeMin=new_date, maxResults=20, singleEvents=True, orderBy="startTime").execute()
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
    chosen_workout = run.CALENDAR.events().get(calendarId=run.CALENDAR_ID, eventId=events_list[int(choice)-1]).execute()
    start = chosen_workout['start'].get('dateTime', chosen_workout['start'].get('date'))
    start = start.replace("T", " ").replace(":00+02:00", "")
    print("You chose the following workout:")
    print(f"Name: {chosen_workout['summary']}, Date: {start}")
    try:
        sheet_check = run.SHEET.worksheet(event_id)
    except:
        sheet_check = run.Null
    if "TRX" in chosen_workout["summary"] or "Cross Training" in chosen_workout["summary"]:
        if sheet_check == run.Null:
            print("There are no registered users for this class.\n")
        else:
            print("The following users are registered:")
            usernames = run.SHEET.worksheet(chosen_workout["id"]).col_values(1)
            for username in usernames:
                print(username)
        print("\n")
    else:
        print("The following users are registered:")
        index = 0
        ma_users = run.SHEET.worksheet("users").col_values(7)
        usernames = run.SHEET.worksheet("users").col_values(1)
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
        run.SHEET.values_update(
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
        run.SHEET.values_update(
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
    admin_actions()

def admin_display_user_data():
    """
    Displays chosen user data and provides options to change it.
    """
    username = input("Please provide user's username or type 'exit' to go back:\n")
    user_index = run.find_user_index(username, "username")
    if username.lower() == "exit":
        admin_actions()
    elif user_index == 0:
        print("Username incorrect. Please try again.")
        admin_display_user_data()
    else:
        print("User found! Fetching data...\n")
        user_class = run.update_user_class(user_index)
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
    admin_username = run.SHEET.worksheet("users").col_values(10)
    admin_password = run.SHEET.worksheet("users").col_values(11)
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