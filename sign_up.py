"""
Sign up functions file
"""

import run

def sign_up():
    """
    Creates a new user from the parameters provided.
    """
    while True:
        username = input("Please enter your new username:\n")
        user_exists = run.find_user_index(username, "username")
        if username.lower() == "exit":
            run.welcome()
        elif user_exists > 0:
            print("Username already in use. Please use a different username or type 'exit' to go to main menu.")
        else:
            break
    while True:
        email = input("Please enter your email:\n")
        email_exists = run.find_user_index(username, "username")
        if email.lower() == "exit":
            run.welcome()
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
        level_athletes = run.SHEET.worksheet("users").col_values(7)
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
    updated_worksheet = run.SHEET.worksheet("users")
    updated_worksheet.append_row(new_user)

    print("Sign up complete! Please speak with the trainer to begin attending!")
    print("Returning to main menu...\n")
    run.welcome()