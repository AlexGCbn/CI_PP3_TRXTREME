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
    while True:
        if item == "athlete_group":
            print("1. Junior 1")
            print("2. Junior 2")
            print("3. Junior 3")
            print("4. Teenage MA")
            print("5. Adult MA")
            print("6. Professional MA")
            new_value = input("Choice:\n")
        if item == "workouts_left":
            new_value = input("Provide new value:\n")
            try:
                int(new_value)
                break
            except ValueError:
                print("Workouts should be a number! Please try again.")
            # if new_value is not int:
            #     print("Workouts should be a number! Please try again.")
            # else:
            #     break
        elif item == "athlete_group":
            if new_value == "1":
                new_value = "Junior 1"
                break
            elif new_value == "2":
                new_value = "Junior 2"
                break
            elif new_value == "3":
                new_value = "Junior 3"
                break
            elif new_value == "4":
                new_value = "Teenage MA"
                break
            elif new_value == "5":
                new_value = "Adult MA"
                break
            elif new_value == "6":
                new_value = "Professional MA"
                break
            else:
                print("Input incorrect. Please try again.")
        else:
            new_value = input("Provide new value:\n")
            if new_value == "" or len(new_value) < 2 or len(new_value) > 50:
                print("Please provide a value greater than 2 characters and smaller than 50.")
            else:
                break

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
