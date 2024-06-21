import socket
import threading
import json
from contextlib import closing
from DataBase import connect_to_db
from datetime import datetime, date
from textblob import TextBlob
from decimal import Decimal

def handle_client(client_socket):
    try:
        request = client_socket.recv(4096).decode('utf-8')
        request_data = json.loads(request)
        print(f"Received request: {request_data}")

        response = process_request(request_data)

        client_socket.send(json.dumps(response, default=custom_json_serializer).encode('utf-8'))
        print(f"Sent response: {response}")
    except Exception as e:
        print(f"Exception in handle_client: {e}")
        error_response = {'status': 'error', 'message': str(e)}
        try:
            if client_socket:
                client_socket.send(json.dumps(error_response).encode('utf-8'))
        except Exception as inner_e:
            print(f"Exception sending error response: {inner_e}")
    finally:
        client_socket.close()

def custom_json_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def process_request(request_data):
    action = request_data.get('action')
    if action == 'login':
        return login(request_data['user_id'], request_data['password'])
    elif action == 'register':
        return register(request_data['user_id'], request_data['password'], request_data['user_name'], request_data['role'])
    elif action == 'add_menu_item':
        return add_menu_item(request_data['name'], request_data['price'], request_data['available'])
    elif action == 'update_menu_item':
        return update_menu_item(request_data['item_name'], request_data['new_name'], request_data['price'], request_data['availability'])
    elif action == 'delete_menu_item':
        return delete_menu_item(request_data['item_name'])
    elif action == 'show_menu_items':
        return show_menu_items()
    elif action == 'recommend_menu_items':
        return recommend_menu_items(request_data['items'], request_data['meal_type'])
    elif action == 'generate_monthly_feedback_report':
        return generate_monthly_feedback_report()
    elif action == 'get_recommendations_from_feedback':
        return get_recommendations_from_feedback(request_data['num_recommendations'])
    elif action == 'provide_feedback':
        return provide_feedback(request_data['item_id'], request_data['comment'], request_data['rating'], request_data['user_id'])
    elif action == 'select_preference':
        return select_preference(request_data['item_id'], request_data['user_id'])
    elif action == 'receive_notification':
        return receive_notification(request_data['user_id'])
    elif action == 'get_user_role':
        return get_user_role(request_data['user_id'])
    elif action == 'delete_user':
        return delete_user(request_data['user_id'])
    elif action == 'generate_discard_list':
        return generate_discard_list()
    elif action == 'remove_menu_item':
        return remove_menu_item(request_data['item_name'])
    elif action == 'request_detailed_feedback':
        return request_detailed_feedback(request_data['item_name'])
    else:
        return {'status': 'error', 'message': 'Invalid action'}

def login(user_id, password):
    with closing(connect_to_db()) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT * FROM Users WHERE user_id = %s AND password = %s", (user_id, password))
            user = cursor.fetchone()
            if user:
                cursor.execute("SELECT message FROM Notifications WHERE user_id = %s", (user_id,))
                notifications = cursor.fetchall()
                cursor.execute("DELETE FROM Notifications WHERE user_id = %s", (user_id,))
                conn.commit()
                return {
                    'status': 'success', 
                    'user': {'user_id': user[0], 'user_name': user[1], 'role': user[2]},
                    'notifications': [n[0] for n in notifications]
                }
            else:
                return {'status': 'error', 'message': 'Invalid user ID or password'}

def register(user_id, password, user_name, role):
    with closing(connect_to_db()) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
            if cursor.fetchone():
                return {'status': 'error', 'message': 'User ID already exists'}
            cursor.execute("INSERT INTO Users (user_id, user_name, role, password) VALUES (%s, %s, %s, %s)", 
                           (user_id, user_name, role, password))
            conn.commit()
            return {'status': 'success', 'message': 'Registration successful'}

def get_user_role(user_id):
    with closing(connect_to_db()) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT role FROM Users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                return {'status': 'success', 'user_role': user[0]}
            else:
                return {'status': 'error', 'message': 'User not found'}

def delete_user(user_id):
    with closing(connect_to_db()) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT role FROM Users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            if user and user[0] == 'Admin':
                return {'status': 'error', 'message': 'Admin cannot be deleted'}

            cursor.execute("DELETE FROM CustomerPreferences WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM FoodFeedback WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM Notifications WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
            conn.commit()
            return {'status': 'success', 'message': 'User deleted successfully'}

def add_menu_item(name, price, available):
    with closing(connect_to_db()) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("INSERT INTO MenuItems (item_name, price, available) VALUES (%s, %s, %s)", 
                           (name, price, available))
            conn.commit()
            cursor.execute("SELECT user_id FROM Users WHERE role = 'Employee'")
            employees = cursor.fetchall()
            for employee in employees:
                cursor.execute(
                    "INSERT INTO Notifications (user_id, message) VALUES (%s, %s)", 
                    (employee[0], f"New item added: {name}, Price: {price}, Available: {available}")
                )
            conn.commit()
            return {'status': 'success', 'message': 'Food item added successfully'}

def update_menu_item(item_name, new_name, price, availability):
    with closing(connect_to_db()) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT item_id FROM MenuItems WHERE item_name = %s", (item_name,))
            item_id_list = cursor.fetchone()
            if item_id_list:
                item_id = item_id_list[0]
                cursor.execute(
                    "UPDATE MenuItems SET item_name=%s, price=%s, available=%s WHERE item_id=%s", 
                    (new_name, price, availability, item_id)
                )
                conn.commit()
                cursor.execute("SELECT user_id FROM Users WHERE role = 'Employee'")
                employees = cursor.fetchall()
                for employee in employees:
                    cursor.execute(
                        "INSERT INTO Notifications (user_id, message) VALUES (%s, %s)", 
                        (employee[0], f"Item updated: {item_name} to {new_name}, Price: {price}, Available: {availability}")
                    )
                conn.commit()
                return {'status': 'success', 'message': 'Food item updated successfully'}
            else:
                return {'status': 'error', 'message': 'Food item not found'}

def delete_menu_item(item_name):
    try:
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT item_id FROM MenuItems WHERE item_name = %s", (item_name,))
                item = cursor.fetchone()
                if item:
                    item_id = item[0]
                    # Delete related entries in the FoodFeedback table
                    cursor.execute("DELETE FROM FoodFeedback WHERE item_id = %s", (item_id,))
                    # Delete the menu item
                    cursor.execute("DELETE FROM MenuItems WHERE item_name = %s", (item_name,))
                    conn.commit()
                    # Send notification to employees about the deletion
                    cursor.execute("SELECT user_id FROM Users WHERE role = 'Employee'")
                    employees = cursor.fetchall()
                    for employee in employees:
                        cursor.execute(
                            "INSERT INTO Notifications (user_id, message) VALUES (%s, %s)", 
                            (employee[0], f"Item deleted: {item_name}")
                        )
                    conn.commit()
                    return {'status': 'success', 'message': 'Food item deleted successfully'}
                else:
                    return {'status': 'error', 'message': 'Food item not found'}
    except Exception as e:
        print(f"Exception in delete_menu_item: {e}")
        return {'status': 'error', 'message': str(e)}

def show_menu_items():
    with closing(connect_to_db()) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT item_name, price FROM MenuItems WHERE available = 1")
            items = cursor.fetchall()
            return {'status': 'success', 'items': items}

def recommend_menu_items(items, meal_type):
    with closing(connect_to_db()) as conn:
        with closing(conn.cursor()) as cursor:
            date = datetime.now().strftime("%Y-%m-%d")
            for item in items:
                cursor.execute("SELECT item_id FROM MenuItems WHERE item_id = %s", (item,))
                if not cursor.fetchone():
                    return {'status': 'error', 'message': f'Item ID {item} does not exist in the menu'}
                cursor.execute("INSERT INTO Suggestions (item_id, date, meal_time) VALUES (%s, %s, %s)", 
                               (item, date, meal_type))
            conn.commit()
            
            cursor.execute("SELECT item_name, price FROM MenuItems WHERE item_id IN (%s)" % ",".join(map(str, items)))
            recommended_item_details = cursor.fetchall()
            item_details = ', '.join([f"{item[0]} ({item[1]})" for item in recommended_item_details])
            
            cursor.execute("SELECT user_id FROM Users WHERE role = 'Employee'")
            employees = cursor.fetchall()
            for employee in employees:
                cursor.execute(
                    "INSERT INTO Notifications (user_id, message) VALUES (%s, %s)", 
                    (employee[0], f"New menu items recommended for {meal_type}: {item_details}")
                )
            conn.commit()
            return {'status': 'success', 'message': 'Menu items recommended successfully'}

def generate_monthly_feedback_report():
    try:
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "SELECT item_id, comment, rating, feedback_date "
                    "FROM FoodFeedback WHERE feedback_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW()"
                )
                feedbacks = cursor.fetchall()
                print(f"Retrieved feedbacks: {feedbacks}")  # Log the retrieved feedbacks
                return {'status': 'success', 'feedbacks': feedbacks}
    except Exception as e:
        print(f"Exception in generate_monthly_feedback_report: {e}")
        return {'status': 'error', 'message': str(e)}

def get_recommendations_from_feedback(num_recommendations):
    try:
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT item_id, comment FROM FoodFeedback")
                feedbacks = cursor.fetchall()

                item_scores = {}
                for feedback in feedbacks:
                    item_id, comment = feedback
                    sentiment = TextBlob(comment).sentiment.polarity
                    if item_id in item_scores:
                        item_scores[item_id].append(sentiment)
                    else:
                        item_scores[item_id] = [sentiment]

                print(f"Item scores before averaging: {item_scores}")

                average_scores = {item_id: sum(scores)/len(scores) for item_id, scores in item_scores.items()}
                print(f"Average scores: {average_scores}")

                recommended_items = sorted(average_scores.items(), key=lambda x: x[1], reverse=True)[:num_recommendations]
                print(f"Recommended items after sorting and slicing: {recommended_items}")

                items = []
                for item_id, score in recommended_items:
                    cursor.execute("SELECT item_name, price FROM MenuItems WHERE item_id = %s", (item_id,))
                    item = cursor.fetchone()
                    if item:
                        items.append({'item_name': item[0], 'price': float(item[1]), 'sentiment_score': score})

                print(f"Final recommended items: {items}")

                return {'status': 'success', 'recommended_items': items}
    except Exception as e:
        print(f"Exception in get_recommendations_from_feedback: {e}")
        return {'status': 'error', 'message': str(e)}

def provide_feedback(item_id, comment, rating, user_id):
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "INSERT INTO FoodFeedback (user_id, item_id, comment, rating, feedback_date) VALUES (%s, %s, %s, %s, %s)", 
                    (user_id, item_id, comment, rating, date)
                )
                conn.commit()
                return {'status': 'success', 'message': 'Feedback provided successfully'}
    except Exception as e:
        print(f"Exception in provide_feedback: {e}")
        return {'status': 'error', 'message': str(e)}

def select_preference(item_id, user_id):
    try:
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "INSERT INTO CustomerPreferences (user_id, item_id) VALUES (%s, %s)", 
                    (user_id, item_id)
                )
                conn.commit()
                return {'status': 'success', 'message': 'Preference selected successfully'}
    except Exception as e:
        print(f"Exception in select_preference: {e}")
        return {'status': 'error', 'message': str(e)}

def receive_notification(user_id):
    try:
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT message FROM Notifications WHERE user_id = %s", (user_id,))
                notifications = cursor.fetchall()
                return {'status': 'success', 'notifications': [n[0] for n in notifications]}
    except Exception as e:
        print(f"Exception in receive_notification: {e}")
        return {'status': 'error', 'message': str(e)}

def generate_discard_list():
    try:
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "SELECT item_id, AVG(rating) as avg_rating, GROUP_CONCAT(comment SEPARATOR '; ') as comments "
                    "FROM FoodFeedback GROUP BY item_id"
                )
                feedbacks = cursor.fetchall()

                discard_list = []
                for item_id, avg_rating, comments in feedbacks:
                    sentiment_score = sum(TextBlob(comment).sentiment.polarity for comment in comments.split('; ')) / len(comments.split('; '))
                    if avg_rating < 2 or sentiment_score < 0:
                        cursor.execute("SELECT item_name FROM MenuItems WHERE item_id = %s", (item_id,))
                        item_name = cursor.fetchone()
                        if item_name:
                            discard_list.append({
                                'item_name': item_name[0],
                                'avg_rating': avg_rating,
                                'comments': comments
                            })
                return {'status': 'success', 'discard_list': discard_list}
    except Exception as e:
        print(f"Exception in generate_discard_list: {e}")
        return {'status': 'error', 'message': str(e)}

def remove_menu_item(item_name):
    try:
        return delete_menu_item(item_name)
    except Exception as e:
        print(f"Exception in remove_menu_item: {e}")
        return {'status': 'error', 'message': str(e)}

def request_detailed_feedback(item_name):
    try:
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT user_id FROM Users WHERE role = 'Employee'")
                employees = cursor.fetchall()
                for employee in employees:
                    cursor.execute(
                        "INSERT INTO Notifications (user_id, message) VALUES (%s, %s)", 
                        (employee[0], f"We are trying to improve your experience with {item_name}. Please provide your feedback and help us. "
                                      f"Q1. What didn’t you like about {item_name}? "
                                      f"Q2. How would you like {item_name} to taste? "
                                      f"Q3. Share your mom’s recipe.")
                    )
                conn.commit()
                return {'status': 'success', 'message': 'Detailed feedback requested successfully'}
    except Exception as e:
        print(f"Exception in request_detailed_feedback: {e}")
        return {'status': 'error', 'message': str(e)}

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(5)
    print("Server started at localhost on port 12345")
    
    while True:
        client_socket, addr = server_socket.accept()
        print("Connection from", addr)
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
