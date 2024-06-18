from DataBase import connect_to_db
from Validation import Validation
from Cafeteria import FoodItem, Review, Suggestion, CustomerPreference
from datetime import datetime
from Exception import InvalidInputError
from textblob import TextBlob
from contextlib import closing

class User:
    def __init__(self, user_id, user_name, user_role):
        self.user_id = user_id
        self.user_name = user_name
        self.user_role = user_role

    @staticmethod
    def login(user_id, user_password):
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT * FROM Users WHERE user_id = %s AND password = %s", (user_id, user_password))
                user = cursor.fetchone()
                if user:
                    return User(user[0], user[1], user[2])
                else:
                    return None

class Admin(User):
    def __init__(self, user_id, user_name):
        super().__init__(user_id, user_name, 'Admin')

    def add_menu_item(self):
        name = input("Enter food item name: ")
        while True:
            try:
                price = float(input("Enter food item price: "))
                break
            except ValueError as e:
                print(e)

        while True:
            try:
                availability = int(input("Enter food item availability (1 for available, 0 for not available): "))
                if availability in [0, 1]:
                    break
                else:
                    raise ValueError("Availability must be 1 (available) or 0 (not available).")
            except ValueError as e:
                print(e)

        item = FoodItem(None, name, price, availability)
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("INSERT INTO MenuItems (item_name, price, available) VALUES (%s, %s, %s)", 
                               (item.item_name, item.price, item.available))
                conn.commit()
        print("Food item added successfully.")

    def update_menu_item(self):
        item_name = input("Enter food item name to update: ")
        check_item = Validation.check_menu_item_existance(item_name)
        if check_item:
            item_new_name = input("Enter new food item name: ")
            while True:
                try:
                    price = float(input("Enter food item price: "))
                    break
                except ValueError as e:
                    print(e)
            while True:
                try:
                    availability = int(input("Enter food item availability (1 for available, 0 for not available): "))
                    if availability in [0, 1]:
                        break
                    else:
                        raise ValueError("Availability must be 1 (available) or 0 (not available).")
                except ValueError as e:
                    print(e)
            
            with closing(connect_to_db()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("SELECT item_id FROM MenuItems WHERE item_name = %s", (item_name,))
                    item_id_list = cursor.fetchone()
                    if item_id_list:
                        item_id = item_id_list[0]
                        cursor.execute(
                            "UPDATE MenuItems SET item_name=%s, price=%s, available=%s WHERE item_id=%s", 
                            (item_new_name, price, availability, item_id)
                        )
                        conn.commit()
                        print("Food item updated successfully.")
                    else:
                        print("Food item not found.")
        else:
            print("Entered item doesn't exist")

    def delete_menu_item(self):
        item_name = input("Enter the item name to delete: ")
        check_item = Validation.check_menu_item_existance(item_name)
        if check_item:
            with closing(connect_to_db()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("DELETE FROM MenuItems WHERE item_name = %s", (item_name,))
                    conn.commit()
            print("The food item is deleted successfully.")
        else:
            print("Entered item doesn't exist")

    @staticmethod
    def register():
        while True:
            user_id = int(input("Enter your user ID to register: "))
            with closing(connect_to_db()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
                    user = cursor.fetchone()
                    if user:
                        print("User ID already exists. Please try a different ID.")
                    else:
                        break
        user_password = input("Enter password: ")
        user_name = input("Enter your user name: ")
        print("Select role:")
        print("1. Admin  2. Chef  3. Employee")
        role_choice = int(input("Enter the number corresponding to your role: "))
        if role_choice == 1:
            user_role = 'Admin'
        elif role_choice == 2:
            user_role = 'Chef'
        elif role_choice == 3:
            user_role = 'Employee'
        else:
            print("Invalid role choice. Defaulting to Employee.")
            user_role = 'Employee'

        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("INSERT INTO Users (user_id, user_name, role, password) VALUES (%s, %s, %s, %s)", 
                               (user_id, user_name, user_role, user_password))
                conn.commit()
        print("Registration successful.")
        return User(user_id, user_name, user_role)

class Chef(User):
    def __init__(self, user_id, user_name):
        super().__init__(user_id, user_name, 'Chef')

    def recommend_menu_items(self):
        items = []
        meal_type = input("Enter meal type (Breakfast, Lunch, Dinner): ")
        num_items = int(input("Enter the number of items to recommend: "))
        for _ in range(num_items):
            item_id = int(input("Enter food item ID to recommend: "))
            items.append(FoodItem(item_id, None, None, None))
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                date = datetime.now().strftime("%Y-%m-%d")
                for item in items:
                    cursor.execute("INSERT INTO Suggestions (item_id, date, meal_time) VALUES (%s, %s, %s)", 
                                   (item.item_id, date, meal_type))
                conn.commit()
        print("Menu items recommended successfully.")

    def generate_monthly_feedback_report(self):
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "SELECT item_id, comment, rating, feedback_date "
                    "FROM FoodFeedback WHERE feedback_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW()"
                )
                feedbacks = cursor.fetchall()
        for feedback in feedbacks:
            print(feedback)

    def get_recommendations_from_feedback(self):
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

                average_scores = {item_id: sum(scores)/len(scores) for item_id, scores in item_scores.items()}
                recommended_items = sorted(average_scores.items(), key=lambda x: x[1], reverse=True)

                print("Recommended items based on feedback sentiment:")
                for item_id, score in recommended_items:
                    cursor.execute("SELECT item_name, price FROM MenuItems WHERE item_id = %s", (item_id,))
                    item = cursor.fetchone()
                    if item:
                        print(f"Item: {item[0]}, Price: {item[1]:.2f}, Sentiment Score: {score:.2f}")

class Employee(User):
    def __init__(self, user_id, user_name):
        super().__init__(user_id, user_name, 'Employee')

    def provide_feedback(self):
        item_id = int(input("Enter food item ID to provide feedback: "))
        comment = input("Enter your comment: ")
        while True:
            try:
                rating = float(input("Enter your rating (1-5): "))
                if rating < 1 or rating > 5:
                    raise ValueError("Rating must be between 1 and 5")
                break
            except ValueError as e:
                print(f"Invalid input: {e}. Please enter a valid rating.")
        feedback = Review(None, item_id, self.user_id, comment, rating, datetime.now())
        date = datetime.now().strftime("%Y-%m-%d")
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "INSERT INTO FoodFeedback (user_id, item_id, comment, rating, feedback_date) VALUES (%s, %s, %s, %s, %s)", 
                    (self.user_id, feedback.item_id, feedback.feedback, feedback.rating, date)
                )
                conn.commit()
        print("Feedback provided successfully.")

    def select_preference(self):
        item_id = int(input("Enter food item ID to select as preference: "))
        preference = CustomerPreference(None, self.user_id, item_id)
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "INSERT INTO CustomerPreferences (user_id, item_id) VALUES (%s, %s)", 
                    (self.user_id, preference.item_id)
                )
                conn.commit()
        print("Preference selected successfully.")

    def receive_notification(self):
        with closing(connect_to_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT message FROM Notifications WHERE user_id = %s", (self.user_id,))
                notifications = cursor.fetchall()
        for notification in notifications:
            print(notification[0])
