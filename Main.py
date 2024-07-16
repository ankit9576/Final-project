from datetime import datetime
import threading
from User import *
from Cafeteria import *
from DataBase import *
from Exception import InvalidInputError

def display_admin_menu():
    print("\nAdmin Menu:")
    print("1. Add User (Registration)")
    print("2. Add Food Item")
    print("3. Update Food Item")
    print("4. Delete Food Item")
    print("5. Show available food items")
    print("6. Logout")

def display_chef_menu():
    print("\nChef Menu:")
    print("1. Recommend Menu Items")
    print("2. Generate Monthly Feedback Report")
    print("3. Show available food items")
    print("4. Get Recommendations from Feedback")
    print("5. Logout")

def display_employee_menu():
    print("\nEmployee Menu:")
    print("1. Show available food items")
    print("2. Provide Feedback")
    print("3. Select Preference")
    print("4. Receive Notifications")
    print("5. Set Personal Preference")
    print("6. Logout")

def get_user_choice():
    try:
        choice = int(input("Enter your choice: "))
        return choice
    except ValueError:
        raise InvalidInputError

def main():
    while True:
        print("Welcome to the Cafeteria Recommendation Engine")
        user_id = input("Enter your user ID to login: ")
        user_password = input("Enter password: ")
        user = User.login(user_id, user_password)
        menu_display = MenuDisplay()
        if user:
            print(f"Welcome, {user.user_name}. You are logged in as {user.user_role}.")
            if user.user_role == 'Admin':
                admin = Admin(user.user_id, user.user_name)
                while True:
                    display_admin_menu()
                    try:
                        choice = get_user_choice()
                    except InvalidInputError as e:
                        print(e.message)
                        continue
                    if choice == 1:
                        admin.register()
                    elif choice == 2:
                        admin.add_menu_item()
                    elif choice == 3:
                        admin.update_menu_item()
                    elif choice == 4:
                        admin.delete_menu_item()
                    elif choice == 5:
                        menu_display.show_menu_items()
                    elif choice == 6:
                        break
                    else:
                        print("Invalid choice. Please try again.")
            elif user.user_role == 'Chef':
                chef = Chef(user.user_id, user.user_name)
                while True:
                    display_chef_menu()
                    try:
                        choice = get_user_choice()
                    except InvalidInputError as e:
                        print(e.message)
                        continue
                    if choice == 1:
                        chef.recommend_menu_items()
                    elif choice == 2:
                        chef.generate_monthly_feedback_report()
                    elif choice == 3:
                        menu_display.show_menu_items()
                    elif choice == 4:
                        chef.get_recommendations_from_feedback()
                    elif choice == 5:
                        break
                    else:
                        print("Invalid choice. Please try again.")
            elif user.user_role == 'Employee':
                employee = Employee(user.user_id, user.user_name)
                while True:
                    display_employee_menu()
                    try:
                        choice = get_user_choice()
                    except InvalidInputError as e:
                        print(e.message)
                        continue
                    if choice == 1:
                        menu_display.show_recommendations()
                    elif choice == 2:
                        employee.provide_feedback()
                    elif choice == 3:
                        employee.select_preference()
                    elif choice == 4:
                        employee.receive_notification()
                    elif choice == 5:
                        employee.set_personal_preference()
                    elif choice == 6:
                        break
                    else:
                        print("Invalid choice. Please try again.")
        else:
            print("Invalid user ID or password. Please try again.")

if __name__ == "__main__":
    main()
