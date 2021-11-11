"""
User options file
"""

import run

def successful_sign_in(user_class):
    """
    Uses user class to determine what choices to provide to user.
    For workout users, provides the option to sign up for a workout or see their information.
    For martial arts athletes, provides details and next workout directly.
    """
    choice = ""
    if user_class.athlete_type == "workout":
        print(f"Welcome {user_class.first_name}! Please choose an option:")
        print("1. Sign up for workout")
        print("2. View remaining workouts")
        print("3. Exit to main menu")
        choice = input("Enter choice:\n")
        if choice == "1":
            if int(user_class.workouts_left) > 0:
                workout_sign_up(user_class)
            else:
                print("!!!")
                print("You do not have enough workouts left. Please contact the trainer!")
                print("!!!\n")
                run.welcome()
        elif choice == "2":
            display_user_data(user_class)
        elif choice == "3":
            run.welcome()
        else:
            print("Incorrect choice. Please try again!")
            successful_sign_in(user_class)
    elif user_class.athlete_type == "martial arts":
        display_user_data(user_class)
    print("Returning to main menu...\n")
    run.welcome()

def display_user_data(user_class):
    """
    Provides information to user about their profile depending on their type.
    """
    if user_class.athlete_type == "workout":
        print(f"Hello {user_class.first_name} {user_class.last_name}! Your remaining workouts are {user_class.workouts_left}")
    elif user_class.athlete_type == "martial arts":
        print(f"Hello {user_class.first_name} {user_class.last_name}! Your group is {user_class.athlete_group}")

        now = run.datetime.datetime.utcnow().isoformat() + "Z"
        events_list = []

        if user_class.athlete_group == "Junior 1":
            events_result = run.CALENDAR.events().list(calendarId=run.CALENDAR_ID, timeMin=now, maxResults=1, singleEvents=True, q="Junior 1").execute()
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
    now = run.datetime.datetime.utcnow().isoformat() + "Z"
    print("Getting upcoming events")
    events_result = run.CALENDAR.events().list(calendarId=run.CALENDAR_ID, timeMin=now, maxResults=20, singleEvents=True, orderBy="startTime").execute()
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
    chosen_workout = run.CALENDAR.events().get(calendarId=run.CALENDAR_ID, eventId=events_list[int(choice)-1]).execute()
    start = chosen_workout['start'].get('dateTime', chosen_workout['start'].get('date'))
    start = start.replace("T", " ").replace(":00+02:00", "")
    print("You chose the following workout:\n")
    print(f"Name: {chosen_workout['summary']}, Date: {start}")
    new_choice = input("Do you want to register? Y/N\n")
    if new_choice.lower() == 'y':
        update_event_attendees(event_id, "sign_up", user_class)
    elif new_choice.lower() == "n":
        successful_sign_in(user_class)

def update_workout(user_class):
    """
    Gets an action to either add or remove a workout to the user.
    Updates the row of the selected user to add the new value.
    """

    index = str(run.find_user_index(user_class.username, "username"))
    new_range = "users!A"+index
    new_value = int(user_class.workouts_left) - 1
    run.SHEET.values_update(
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
            sheet_check = run.SHEET.worksheet(event_id)
        except:
            sheet_check = run.Null
        if sheet_check == run.Null:
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
            run.SHEET.batch_update(body=new_sheet)
        usernames = run.SHEET.worksheet(event_id).col_values(1)
        if user_class.username in usernames:
            print("!!!")
            print("You are already registered for this workout! Returning to main menu.")
            print("!!!\n")
            run.welcome()
        else:
            print("Signing up for workout...\n")
            updated_worksheet = run.SHEET.worksheet(event_id)
            updated_worksheet.append_row([user_class.username])
            update_workout(user_class)
            print("!!!")
            print("Successfully signed up for workout! Returning to main menu.")
            print("!!!\n")
            run.welcome()