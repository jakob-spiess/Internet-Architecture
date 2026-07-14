import socket
import sys
import threading

def start_server(port):
    #added by me to know which ip to connect to:
    print(socket.gethostbyname(socket.gethostname()))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', port)
    server_socket.bind(server_address)

    server_socket.listen(1)

    print('Waiting for a connection...')
    connection, client_address = server_socket.accept()
    print('Connection from', client_address)

    receive_thread = threading.Thread(target=receive_messages, args=(connection,))
    receive_thread.start()

    while True:
        message = input()
        if message == '':
            break
        connection.sendall(message.encode('utf-8'))

    connection.close()
    server_socket.close()

def start_client(ip, port):
    #To find your Ipv4 adress aka the server, run socket.gethostbyname(socket.gethostname()), or just send 'localhost'
    #the ip is the server
    
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = (ip, port)
    #client_socket.bind(client_address)

    # Connect the socket to the server's address and port
    print('Connecting to server...')
    client_socket.connect(server_address)
    print('Connected to', server_address)

    #WORKS TILL HERE
    connection = client_socket

    # Create a separate thread for receiving messages
    receive_thread = threading.Thread(target=receive_messages, args=(connection,))
    receive_thread.start()

    # Continuously send messages
    while True:
        message = input()
        if message == '':
            break
        connection.sendall(message.encode('utf-8'))

    # Close the connection and the client socket
    connection.close()
    client_socket.close()

    pass

def receive_messages(connection):
    # You can reuse this if needed
    while True:
        data = connection.recv(1024)
        if not data:
            break
        print(data.decode('utf-8'))

if len(sys.argv) == 1:
    start_server(10000)
elif len(sys.argv) == 2:
    port = int(sys.argv[1])
    start_server(port)
else:
    ip = sys.argv[1]
    port = int(sys.argv[2])
    start_client(ip, port)

