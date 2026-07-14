import socket
import threading
import time
import json
import os
import datetime

username = None
known_users = {} #Format: key:username, value:ip,port,last_activity

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


# (Relative) File path for storing the dictionary -> For persistence
file_path = "known_users.json"

def get_local_ip():
    global username
    global known_users
    # Create a socket object
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Connect to a remote address, in this case, Google's public DNS server
        soc.connect(("8.8.8.8", 80))
        # Get the local IP address bound to the socket
        local_ip = soc.getsockname()[0]
    except Exception as e:
        print(f"An error occurred while getting the local IP address: {e}")
        local_ip = None
    finally:
        # Close the socket
        soc.close()

    return local_ip

def user_connect():
    global username
    global known_users

    if username is None:
        username = input("\nEnter your username: ")

        #Enter this user into the dict
        known_users[username] = (s.getsockname()[0], s.getsockname()[1], int(time.time()))

def send_messages():
    global username
    global known_users
    while True:
        message_input = input()

        #Handle show-users input case
        if (message_input == "show-users"):
            print("Known Users:")
            for user_name, user_data in known_users.items():
                print(f"Username: {user_name}, IP: {user_data[0]}, Port: {user_data[1]}, Last Activity: {user_data[2]}")
            continue

        #Handle the show-utility case
        if (message_input == "show-utility"):
            print("Last activity by users:")
            for user_name, user_data in known_users.items():
                # Convert unix-epoch to human readable format
                last_activity_time = datetime.datetime.fromtimestamp(user_data[2])

                # Print user name and last activity time
                print(f"Last activity for {user_name} ({last_activity_time})")
            continue


        #message_data = message_input.split(maxsplit=3)
        message_data = message_input.split(maxsplit=1)


        # Ensure message_data has at least 2 elements (target user and message)
        if len(message_data) < 2:
            print("Invalid input format. Please provide at least the target user and the message.")

        if len(message_data) == 2:
            target_user, message = message_data
            if target_user in known_users:
                target_ip, target_port = known_users[target_user][:2]
                #FOR DEBUGGING
                #print(target_ip)
                #print(target_port)

                message = f"{username}: {message}"
                if len(message) <= 576:
                    #with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.sendto(message.encode(), (target_ip, target_port))
                     #FOR DEBUGGING:
                    print("Message sent successfully.")
                else:
                    print("Message size exceeds maximum limit (576 bytes).")
            else:
                print(f"Target user {target_user} not found in known users.")
        else:
            print("Invalid input format. Please enter in the format: <target_user> <target_ip> <target_port> <message>, or: <target_user> <message>")


        #Record this sending message as 'activity' by this user

        # Get the current tuple for the specified username
        current_tuple = known_users.get(username, (None, None, None))

        # Update the third entry with the new timestamp
        updated_tuple = (current_tuple[0], current_tuple[1], int(time.time()))

        # Update the value in the known_users dictionary
        known_users[username] = updated_tuple


def setup_socket():
    global username
    global known_users
    #This is logically not perfect yet, e.g if a same user logs in on different machine/different IP I think it would crash
    #because it would try to use a unavailable IP (but good enough for now) -> would just be a little more code and shouldn't happen for now

    # Check if the username is present in the JSON file
    if os.path.exists(file_path): #If the file even exists
        with open(file_path, "r") as file:
            saved_data = json.load(file)
            if username in saved_data:
                saved_ip, saved_port = saved_data[username][:2]  # Get saved IP and port
                #FOR DEBUGGING
                #print(saved_ip)
                #print(saved_port)
                s.bind((saved_ip, saved_port))
            else:
                local_ip = get_local_ip()
                s.bind((local_ip, 0)) #Used to have '' instead of local_ip
    else: #If the file didn't exist
        local_ip = get_local_ip()
        s.bind((local_ip, 0)) #Used to have '' instead of local_ip

    ip_address = s.getsockname()[0]
    port = s.getsockname()[1]

    # Get the current value of the third entry from the known_users dictionary
    #current_timestamp = known_users.get(username, (None, None, None))[2]

    # Update the first two entries and keep the current value in the third entry
    known_users[username] = (ip_address, port, int(time.time()))


def receive_messages():
    global username
    global known_users
    while True:

        data, addr = s.recvfrom(576)  # Changed to receive maximum 576 bytes

        message = data.decode()

        #FOR DEBUGGING
        #print(message)

        print(f"Received message from {addr[0]}:{addr[1]} - {message}")
            

def broadcast_state():
    global username
    global known_users

    while True:
        state_message = ""
        for user, user_data in known_users.items():
            state_message += f"{user}: {user_data[0]}: {user_data[1]}: {user_data[2]}\n"
        s.sendto(state_message.encode(), ('<broadcast>', 37020))
        #FOR DEBUGGING:
        #print("State broadcasted.")
        time.sleep(10)

def parse_broadcasts():
    global username
    global known_users
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    soc.bind(('', 37020))

    while True:

        data, addr = soc.recvfrom(576)

        #FOR DEBUGGING:
        #print("Broadcast received")

        broadcast_data = data.decode()
        for line in broadcast_data.split('\n'):
            if line:
                parts = line.split(": ")
                #FOR DEBUGGING:
                #print(parts)
                if len(parts) == 4:
                    user, sender_ip, sender_port, timestamp_str = parts
                    sender_port = int(sender_port)
                    timestamp = int(timestamp_str)
                    if user not in known_users:
                        known_users[user] = (sender_ip, sender_port, timestamp)
                    elif known_users[user][2] < timestamp:
                        known_users[user] = (sender_ip, sender_port, timestamp)
                    #else:
                        #known_users[user] = (sender_ip, sender_port, timestamp)
                        #known_users[user] = (known_users[user][0], known_users[user][1], timestamp)

#Used on start-up of program to achieve persistence
def reinitialize_dict():
    global username
    global known_users
    try:
        # Check if the file exists
        with open(file_path, "r") as file:
            # Load the dictionary from the file
            known_users = json.load(file)
        print("Dictionary reinitialized from file.")
    except FileNotFoundError:
        print("File not found. No dictionary reinitialized.")


def write_dict_to_file():
    global username
    global known_users
    while True:
        # Write the dictionary to a file in JSON format
        with open(file_path, "w") as file:
            json.dump(known_users, file)
        #FOR DEBUGGING
        #print("Dictionary written to file.")
        # Wait for 15 seconds before writing again
        time.sleep(15)


def main():
    reinitialize_dict()
    user_connect()
    setup_socket()
    print("\nYou are now able to send messages, please use this format: <target_user> <message>\n")
    print("To know which users are currently in the network you can type: \'show-users\'.\nYou can also type \'show-utility\' to see the last activity of all the users.\n")#\nTo see output you may have to wait 10 seconds, because of broadcast delays.\n")
    send_thread = threading.Thread(target=send_messages)
    receive_thread = threading.Thread(target=receive_messages)
    broadcast_thread = threading.Thread(target=broadcast_state)
    parse_broadcasts_thread = threading.Thread(target=parse_broadcasts)
    persistence_thread = threading.Thread(target=write_dict_to_file)
    send_thread.daemon = True
    receive_thread.daemon = True
    broadcast_thread.daemon = True
    parse_broadcasts_thread.daemon = True
    persistence_thread.daemon = True
    send_thread.start()
    receive_thread.start()
    broadcast_thread.start()
    parse_broadcasts_thread.start()
    persistence_thread.start()

    # Add a while loop to keep the main thread running
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
