import socket
import threading
from User import *
from Cafeteria import *
from DataBase import *

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('localhost', 12345))
        server_socket.listen(5)
        print("Server started at localhost on port 12345")
        
        while True:
            client_socket, addr = server_socket.accept()
            print("Connection from", addr)
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()

def handle_client(client_socket):
    with client_socket:
        request = client_socket.recv(1024)
        print("Received", request.decode('utf-8'))
        client_socket.send("ACK".encode('utf-8'))

if __name__ == "__main__":
    start_server()
