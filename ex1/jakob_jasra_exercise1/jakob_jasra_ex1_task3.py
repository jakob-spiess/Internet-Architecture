import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP

# Thanks to @stevenreddie
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# Enable broadcasting mode
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

client.bind(("", 37020))

nickname = input("Choose your nickname: ")

def send_message():
    while True:
        message = input()
        message = nickname + ": " + message
        #I used to have a function to calculate the broadcast address for my IP like in the wikipedia Sebastian sent in the discord but decided to just use this <broadcast>
        client.sendto(message.encode(), ('<broadcast>', 37020))

        # Function to receive messages
def receive_messages():
    while True:
        data, addr = client.recvfrom(1024)
        received_message = data.decode()
        if (not received_message.startswith(nickname)):
            print(received_message)
        #print(received_message)
        #sender_ip = addr[0]

        # Get the local IP address of the current machine
        #local_ip = socket.gethostbyname(socket.gethostname())

        # Check if the sender's IP address matches the local IP
        #if sender_ip != local_ip:
            #received_message = data.decode()
            #print(received_message)

send_thread = threading.Thread(target=send_message)
#send_thread.daemon = True
send_thread.start()

receive_thread = threading.Thread(target=receive_messages)
#receive_thread.daemon = True
receive_thread.start()

# Main thread waits for the threads to finish
receive_thread.join()
send_thread.join()