import socket
import json

def send_request(action, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', 12345))
        request = json.dumps({'action': action, **data})
        client_socket.send(request.encode('utf-8'))
        response = client_socket.recv(4096).decode('utf-8')
        return json.loads(response)

def show_admin_menu():
    print("Admin Menu:")
    print("1. Add Food Item")
    print("2. Update Food Item")
    print("3. Delete Food Item")
    print("4. Show available food items")
    print("5. Register new user")
    print("6. Delete user")
    print("7. View Discard Menu Item List")
    print("8. Logout")

def handle_admin_actions(user):
    while True:
        show_admin_menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            name = input("Enter food item name: ")
            while not name.replace(' ', '').isalpha():
                print("Invalid food name. Please try again.")
                name = input("Enter food item name: ")
            while True:
                try:
                    price = float(input("Enter food item price: "))
                    break
                except ValueError:
                    print("Invalid price. Please enter a valid number.")
            available = input("Enter availability (1 for available, 0 for not available): ")
            response = send_request('add_menu_item', {'name': name, 'price': price, 'available': available})
            print(response['message'])
        elif choice == '2':
            item_name = input("Enter food item name to update: ")
            new_name = input("Enter new food item name: ")
            while not new_name.replace(' ', '').isalpha():
                print("Invalid food name. Please try again.")
                new_name = input("Enter new food item name: ")
            while True:
                try:
                    price = float(input("Enter new food item price: "))
                    break
                except ValueError:
                    print("Invalid price. Please enter a valid number.")
            availability = input("Enter availability (1 for available, 0 for not available): ")
            response = send_request('update_menu_item', {'item_name': item_name, 'new_name': new_name, 'price': price, 'availability': availability})
            print(response['message'])
        elif choice == '3':
            item_name = input("Enter the item name to delete: ")
            response = send_request('delete_menu_item', {'item_name': item_name})
            print(response['message'])
        elif choice == '4':
            response = send_request('show_menu_items', {})
            if response['status'] == 'success':
                items = response['items']
                print("Available items")
                print("--------------------")
                for item in items:
                    print(f"{item[0]} - {item[1]}")
            else:
                print(response['message'])
        elif choice == '5':
            user_id = input("Enter new user ID: ")
            password = input("Enter password: ")
            user_name = input("Enter user name: ")
            role = input("Enter role (Admin, Chef, Employee): ")
            response = send_request('register', {'user_id': user_id, 'password': password, 'user_name': user_name, 'role': role})
            print(response['message'])
        elif choice == '6':
            user_id = input("Enter the user ID to delete: ")
            response = send_request('delete_user', {'user_id': user_id})
            print(response['message'])
        elif choice == '7':
            response = send_request('generate_discard_list', {})
            if response['status'] == 'success':
                discard_list = response['discard_list']
                print("Discard Menu Item List")
                for item in discard_list:
                    print(f"Food Item: {item['item_name']}")
                    print(f"Average Rating: {item['avg_rating']}/5")
                    print(f"Sentiments: {item['comments']}")
                    print("--------------------------------------------------")
                print("1) Remove the Food Item from Menu List")
                print("2) Get Detailed Feedback")
                sub_choice = input("Enter your choice: ")
                if sub_choice == '1':
                    item_name = input("Enter the food item name to remove: ")
                    remove_response = send_request('remove_menu_item', {'item_name': item_name})
                    print(remove_response['message'])
                elif sub_choice == '2':
                    item_name = input("Enter the food item name for detailed feedback: ")
                    feedback_response = send_request('request_detailed_feedback', {'item_name': item_name})
                    print(feedback_response['message'])
                else:
                    print("Invalid choice. Please try again.")
        elif choice == '8':
            break
        else:
            print("Invalid choice. Please try again.")

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
            if user['role'] == 'Admin':
                handle_admin_actions(user)
            break
        else:
            print("Invalid user ID or password. Please try again.")

if __name__ == "__main__":
    main()
