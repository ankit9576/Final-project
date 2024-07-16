from DataBase import connect_to_db
from mysql.connector import Error
from contextlib import closing

class Validation:
    @staticmethod
    def check_menu_item_existance(item_name):
        try:
            with closing(connect_to_db()) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute("SELECT item_id FROM MenuItems WHERE item_name = %s", (item_name,))
                    result = cursor.fetchone()
                    return result is not None
        except Error as e:
            print(f"Error: {e}")
            return False
