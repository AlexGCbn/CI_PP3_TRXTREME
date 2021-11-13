"""
File used to store functions that affect user data.
"""

import user
import gservices as gs

def update_workout(user_class):
    """
    Removes a user workout from their counter.
    Updates the row of the selected user to add the new value.
    """
    index = str(user.find_user_index(user_class.username, "username"))
    new_range = "users!A"+index
    new_value = int(user_class.workouts_left) - 1
    gs.SHEET.values_update(
        new_range,
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': [[user_class.username, user_class.email, user_class.first_name, user_class.last_name, user_class.athlete_type, new_value]]
        }
    )

def update_user_class(ind):
    """
    Uses the passed index number to find user on Google Sheet and create the user object.
    """
    values = gs.SHEET.worksheet("users").row_values(ind)
    if values[4] == "workout":
        user_class = user.Workout_User(values[0], values[1], values[2], values[3], values[4], values[5])
    elif values[4] == "martial arts":
        user_class = user.Martial_Arts_User(values[0], values[1], values[2], values[3], values[4], values[6])
    return user_class

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
        gs.SHEET.values_update(
            new_range,
            params={
                'valueInputOption': 'USER_ENTERED'
            },
            body={
                'values': [[user_class.username, user_class.email, user_class.first_name, user_class.last_name, user_class.athlete_type, user_class.workouts_left]]
            }
        )
        print(f"{item_str} updated!\n")
    else:
        gs.SHEET.values_update(
            new_range,
            params={
                'valueInputOption': 'USER_ENTERED'
            },
            body={
                'values': [[user_class.username, user_class.email, user_class.first_name, user_class.last_name, user_class.athlete_type, "", user_class.athlete_group]]
            }
        )
        print(f"{item_str} updated!\n")