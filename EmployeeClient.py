import socket
import json

def send_request(action, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', 12345))
        request = json.dumps({'action': action, **data})
        client_socket.send(request.encode('utf-8'))
        response = client_socket.recv(4096).decode('utf-8')
        return json.loads(response)

def show_employee_menu():
    print("Employee Menu:")
    print("1. Show available food items")
    print("2. Provide Feedback")
    print("3. Select Preference")
    print("4. Receive Notifications")
    print("5. Set User Preferences")
    print("6. Logout")

def handle_employee_actions(user):
    while True:
        show_employee_menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            response = send_request('show_menu_items', {})
            if response['status'] == 'success':
                print("Available items")
                print("____________________")
                for item in response['items']:
                    print(f"{item[0]} - {item[1]}")
            else:
                print(response['message'])
        elif choice == '2':
            item_id = input("Enter food item ID to provide feedback: ")
            comment = input("Enter your comment: ")
            rating = input("Enter your rating (1-5): ")
            response = send_request('provide_feedback', {'item_id': item_id, 'comment': comment, 'rating': rating, 'user_id': user['user_id']})
            print(response['message'])
        elif choice == '3':
            item_id = input("Enter food item ID to select as preference: ")
            response = send_request('select_preference', {'item_id': item_id, 'user_id': user['user_id']})
            print(response['message'])
        elif choice == '4':
            response = send_request('receive_notification', {'user_id': user['user_id']})
            if response['status'] == 'success':
                print("Notifications:")
                for notification in response['notifications']:
                    print(notification)
            else:
                print(response['message'])
        elif choice == '5':
            set_user_preferences(user)
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

def set_user_preferences(user):
    preference_1 = input("1) Please select one - Vegetarian, Non Vegetarian, Eggetarian: ")
    preference_2 = input("2) Please select your spice level - High, Medium, Low: ")
    preference_3 = input("3) What do you prefer most? - North Indian, South Indian, Other: ")
    preferences = {
        'preference_1': preference_1,
        'preference_2': preference_2,
        'preference_3': preference_3
    }
    response = send_request('set_user_preferences', {'user_id': user['user_id'], 'preferences': preferences})
    print(response['message'])

def main():
    while True:
        print("Welcome to the Cafeteria Recommendation Engine")
        user_id = input("Enter your user ID to login: ")
        user_password = input("Enter password: ")

        response = send_request('login', {'user_id': user_id, 'password': user_password})

        if response['status'] == 'success':
            user = response['user']
            notifications = response.get('notifications', [])
            print(f"Welcome, {user['user_name']}. You are logged in as {user['role']}.")
            if notifications:
                print("Notifications:")
                for notification in notifications:
                    print(notification)
            handle_employee_actions(user)
            break
        else:
            print("Invalid user ID or password. Please try again.")

if __name__ == "__main__":
    main()
