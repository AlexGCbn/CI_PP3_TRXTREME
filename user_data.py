"""File used to store functions that affect user data."""

import user
import gservices as gs


def update_workout(user_class: object):
    """
    Removes a user workout from their counter.
    Updates the row of the selected user to add the new value.
    @param: user_class object
    """
    index = str(user.find_user_index(user_class.username, "username"))
    new_range = "users!A" + index
    new_value = int(user_class.workouts_left) - 1
    gs.SHEET.values_update(
        new_range,
        params={"valueInputOption": "USER_ENTERED"},
        body={
            "values": [
                [
                    user_class.username,
                    user_class.email,
                    user_class.first_name,
                    user_class.last_name,
                    user_class.athlete_type,
                    new_value,
                ]
            ]
        },
    )


def update_user_class(ind: int) -> object:
    """
    Uses the passed index number to find user on
    Google Sheet and create the user object.
    @param: ind int
    """
    values = gs.SHEET.worksheet("users").row_values(ind)
    if values[4] == "workout":
        user_class = user.WorkoutUser(
            values[0], values[1], values[2], values[3], values[4], values[5]
        )
    elif values[4] == "martial arts":
        user_class = user.MartialArtsUser(
            values[0], values[1], values[2], values[3], values[4], values[6]
        )
    return user_class


def edit_item(index: int, user_class: object, item: str):
    """
    Gets user index, the created object and the item to change.
    Changes the item in the object so it can be returned to the GSheet.
    @param: index int
    @param: user_class object
    @param: item str
    """
    new_range = "users!A" + str(index)
    new_value = input("Provide new value:\n")
    setattr(user_class, item, new_value)
    item_str = item.replace("_", " ").capitalize()
    if user_class.athlete_type == "workout":
        gs.SHEET.values_update(
            new_range,
            params={"valueInputOption": "USER_ENTERED"},
            body={
                "values": [
                    [
                        user_class.username,
                        user_class.email,
                        user_class.first_name,
                        user_class.last_name,
                        user_class.athlete_type,
                        user_class.workouts_left,
                    ]
                ]
            },
        )
        print(f"{item_str} updated!\n")
    else:
        gs.SHEET.values_update(
            new_range,
            params={"valueInputOption": "USER_ENTERED"},
            body={
                "values": [
                    [
                        user_class.username,
                        user_class.email,
                        user_class.first_name,
                        user_class.last_name,
                        user_class.athlete_type,
                        "",
                        user_class.athlete_group,
                    ]
                ]
            },
        )
        print(f"{item_str} updated!\n")


def count_athletes(level: str) -> int:
    """
    Counts how many athletes are in specified level
    Returns the number
    @param: level str
    """
    level_athletes = gs.SHEET.worksheet("users").col_values(7)
    level_count = 0
    for athlete in level_athletes:
        if athlete == level:
            level_count += 1
    return level_count
