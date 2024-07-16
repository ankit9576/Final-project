from DataBase import connect_to_db
from contextlib import closing

class FoodItem:
    def __init__(self, item_id, item_name, price, available):
        self.item_id = item_id
        self.item_name = item_name
        self.price = price
        self.available = available

class Review:
    def __init__(self, review_id, item_id, customer_id, feedback, rating, review_date):
        self.review_id = review_id
        self.item_id = item_id
        self.customer_id = customer_id
        self.feedback = feedback
        self.rating = rating
        self.review_date = review_date

class Suggestion:
    def __init__(self, suggestion_id, item_id, date, meal_time):
        self.suggestion_id = suggestion_id
        self.item_id = item_id
        self.date = date
        self.meal_time = meal_time

class CustomerPreference:
    def __init__(self, preference_id, customer_id, item_id):
        self.preference_id = preference_id
        self.customer_id = customer_id
        self.item_id = item_id

class MenuDisplay:
    def show_menu_items(self):
        with closing(connect_to_db()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT item_name, price FROM MenuItems WHERE available = 1")
                items = cursor.fetchall()
                self._print_items(items)

    def show_recommendations(self):
        with closing(connect_to_db()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(
                    "SELECT m.item_name, m.price FROM Suggestions s "
                    "JOIN MenuItems m ON s.item_id = m.item_id WHERE m.available = 1 AND date = CURRENT_DATE"
                )
                items = cursor.fetchall()
                self._print_items(items)

    @staticmethod
    def _print_items(items):
        print(f"{'Item Name':<20} {'Price':>10}")
        print("-" * 30)
        for item in items:
            print(f"{item[0]:<20} {item[1]:>10.2f}")
