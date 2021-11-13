"""
Module used to store code for user class and subclasses, along with the function to get the user index.
"""
import gservices as gs

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
        usernames = gs.SHEET.worksheet("users").col_values(1)
        if data in usernames:
            for username in usernames:
                index += 1
                if username == data:
                    break
    elif type == "email":
        emails = gs.SHEET.worksheet("users").col_values(2)
        if data in emails:
            for email in emails:
                index += 1
                if email == data:
                    break
    return index