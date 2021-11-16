"""
Module used to store code for user class and subclasses,
along with the function to get the user index.
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


class WorkoutUser(User):
    """
    Workout user class that has an extra "workouts left"
    attribute that counts how many times they can work out.
    """

    def __init__(
        self, username, email, first_name,
            last_name, athlete_type, workouts_left
    ):
        super().__init__(username, email, first_name, last_name, athlete_type)
        self.workouts_left = workouts_left


class MartialArtsUser(User):
    """
    Martial arts user class that has the user's athlete group,
    which dictates which dates they will join."
    """

    def __init__(
        self, username, email, first_name,
            last_name, athlete_type, athlete_group
    ):
        super().__init__(username, email, first_name, last_name, athlete_type)
        self.athlete_group = athlete_group


def find_user_index(data_value: str, type_value: str) -> int:
    """
    Function to check if username or email exists.
    It was created as it needs to be called multiple times.
    It gets the data_value and the type_value, looks for the data_value in the
    appropriate column depending on type_value and returns an index number.
    @param: data_value str
    @param: type_value str
    """
    index = 0
    if type_value == "username":
        usernames = gs.SHEET.worksheet("users").col_values(1)
        if data_value in usernames:
            for username in usernames:
                index += 1
                if username == data_value:
                    break
    elif type_value == "email":
        emails = gs.SHEET.worksheet("users").col_values(2)
        if data_value in emails:
            for email in emails:
                index += 1
                if email == data_value:
                    break
    return index
