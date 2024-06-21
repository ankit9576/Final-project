import requests

SERVER_IP = "192.168.6.11"

def send_get_request():
    response = requests.get(f"http://{SERVER_IP}:5000")
    print("GET response from server:", response.text)

def send_post_request(data):
    response = requests.post(f"http://{SERVER_IP}:5000", data=data)
    if response.status_code == 200:
        return response.text
    else:
        print("Error:", response.text)
        return None

if __name__ == "__main__":
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    send_get_request()
    login_data = f"{username}:{password}"
    response_text = send_post_request(login_data)
    
    if response_text :
        print(response_text)
        vote = input("Enter your vote: ")
        vote_data = f"{username}:{vote}"
        vote_response = send_post_request(vote_data)
        if vote_response:
            print(vote_response)
    else:
        print("Failed to log in or no voting option provided.")
