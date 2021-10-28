"""
Main file
"""

def welcome():
    """
    Welcome function used to provide user with choice of admin/athlete sign in, or sign up.
    """
    print("Welcome to TRXtreme.\n")
    print("To sign in as a user, please input the letter u and enter.")
    print("To sign in as admin, please input the letter a and enter.")
    print("To sign up, please input the letter s and enter.\n")
    
    user_answer = input()

    if user_answer.lower() == "u":
        sign_in()
    elif user_answer.lower() == "a":
        admin_sign_in()
    elif user_answer.lower() == "s":
        sign_up()
    else:
        print(f"{user_answer} is not an acceptable key. Please choose a correct one.")


def main():
    """
    Main function used to run all necessary program functions.
    """
    welcome()

main()