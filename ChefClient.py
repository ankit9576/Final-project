import socket
import json

def send_request(action, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', 12345))
        request = json.dumps({'action': action, **data})
        client_socket.send(request.encode('utf-8'))
        response = client_socket.recv(4096).decode('utf-8')
        return json.loads(response)

def show_chef_menu():
    print("\nChef Menu:")
    print("1. Recommend Menu Items")
    print("2. Generate Monthly Feedback Report")
    print("3. Show available food items")
    print("4. Get Recommendations from Feedback")
    print("5. Logout")

def handle_chef_actions(user):
    while True:
        show_chef_menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            meal_type = input("Enter meal type (Breakfast, Lunch, Dinner): ")
            num_items = int(input("Enter the number of items to recommend: "))
            items = []
            for _ in range(num_items):
                item_id = int(input("Enter food item ID to recommend: "))
                items.append(item_id)
            response = send_request('recommend_menu_items', {'items': items, 'meal_type': meal_type})
            print(response['message'])
        elif choice == '2':
            response = send_request('generate_monthly_feedback_report', {})
            if response['status'] == 'success':
                feedbacks = response['feedbacks']
                print("Item ID | Comment | Rating | Feedback Date")
                print("-" * 50)
                for feedback in feedbacks:
                    print(f"{feedback[0]} | {feedback[1]} | {feedback[2]} | {feedback[3]}")
            else:
                print(response['message'])
        elif choice == '3':
            response = send_request('show_menu_items', {})
            if response['status'] == 'success':
                items = response['items']
                print("Available items")
                print("--------------------")
                for item in items:
                    print(f"{item[0]} - {item[1]}")
            else:
                print(response['message'])
        elif choice == '4':
            num_recommendations = int(input("Enter the number of recommendations: "))
            response = send_request('get_recommendations_from_feedback', {'num_recommendations': num_recommendations})
            if response['status'] == 'success':
                recommendations = response['recommended_items']
                print("Item Name                | Price | Sentiment Score")
                print("--------------------------------------------------")
                for item in recommendations:
                    print(f"{item['item_name']: <25} | {item['price']: >5} | {item['sentiment_score']:.2f}")
            else:
                print(response['message'])
        elif choice == '5':
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
            handle_chef_actions(user)
            break
        else:
            print("Invalid user ID or password. Please try again.")

if __name__ == "__main__":
    main()
