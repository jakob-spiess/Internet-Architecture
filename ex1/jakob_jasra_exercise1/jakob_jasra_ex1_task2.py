#!/bin/python3

from socket import *
import threading
import ast

#Central server mediates connections between clients
#Fully operable from the command line -> My idea_ run script and get instructed on how to use it by the program itself (in the terminal)

serverName = 'localhost'
serverPort = 20000

print("Do you want to start a server or a client? Please type; 'server' or 'client'.")
typeOfService = input()

def serverRequestHandler(server_socket, nicknames, message, clientAddress):
        #print(message.decode())
        message = message.decode()
        if(message.startswith("[[[")):
            nickname = message
            nickname = nickname[3:]
            nickNameChooser(server_socket, nickname, nicknames, clientAddress)
        else:
            chatPartner = message
            chatPartnerChooser(server_socket, chatPartner, nicknames, clientAddress)    

def nickNameChooser(server_socket, nickname, nicknames, clientAddress):
    while True:
        #nickname, clientAddress = server_socket.recvfrom(2048)
        #nickname = nickname.decode()
        if nickname in nicknames:
            server_socket.sendto("This nickname is already taken, please choose another one.".encode(), clientAddress)
            break
        else:
            nicknames[nickname] = clientAddress
            answer = "Who do you want to chat with:\n"
            server_socket.sendto(answer.encode(), clientAddress)
            break

def chatPartnerChooser(server_socket, chatPartner, nicknames, clientAddress):
    #server_socket.sendto("Who would you like to chat with?".encode(), clientAddress)
    while True:
        #chatPartner, clientAddress = server_socket.recvfrom(2048) 
        #chatPartner = chatPartner.decode()
        if chatPartner in nicknames:
            #partnerInformation = "Write to your chat partner with this adress: {}".format(nicknames[chatPartner])
            partnerInformation = "{}".format(nicknames[chatPartner])
            server_socket.sendto(partnerInformation.encode(), clientAddress)
            break
        else:
            server_socket.sendto("not registered".encode(), clientAddress)
            break

def startChat(chatPartner_address, client, nickname):
    #print(chatPartner_address)

    # Removing single quotes around the tuple
    #chatPartner_address = chatPartner_address.strip("()")
    # Using ast.literal_eval() to safely evaluate the string
    # Splitting the string and removing parentheses
    parts = chatPartner_address.strip("()").split(",")

    # Check if there are enough parts
    if len(parts) == 2:
        # Extracting IP address and port number
        ip_address = parts[0].strip().strip("' ")
        port_number = parts[1].strip()
        try:
            port_number = int(port_number)
        except ValueError:
            print("Invalid port number:", port_number)
            # Handle the error, perhaps by exiting or using a default port number
        else:
            # Constructing the tuple
            result_tuple = (ip_address, port_number)
            #print("Result tuple:", result_tuple)

            # Assuming client is a socket object
            while True:
                #print("Chat to your partner: ")
                message = input("")
                message = nickname[3:] + ": " + message
                client.sendto(message.encode(), result_tuple)
    else:
        print("Invalid chatPartner_address format")

def receive_messages(sock, nickname):

    chatPartner = input()
    client_socket.sendto(chatPartner.encode(), (serverName, serverPort))
    
    while True:
        serverMessage, serverAddress = client_socket.recvfrom(2048)
        if (serverMessage.decode() == "not registered"):
            chatPartner = input("This person is not registered yet, choose somebody else to chat with:\n")
            client_socket.sendto(chatPartner.encode(), (serverName, serverPort))
            continue
        else:
            #Here you have to then send the message to the person
            chatPartner_address = serverMessage.decode()
            print("Opening chat to: " + chatPartner_address)
            send_thread = threading.Thread(target=startChat, args=(chatPartner_address,client_socket,nickname,))
            send_thread.start()
            break
    while True:
            data, addr = sock.recvfrom(1024)
            print(data.decode())


if (typeOfService == "server"): #maybe the server and clients have to be startet in a threaded way? idk, so you could start multiple servers -> But I d0n't think we need to be able to have multiple servers
    nicknames = {}

    #start server
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(('', serverPort))
    print("The server is ready.")

    while True:
        message, clientAddress = server_socket.recvfrom(2048)
        receive_thread = threading.Thread(target=serverRequestHandler, args=(server_socket, nicknames, message, clientAddress))
        receive_thread.start()
        #[[[ signifies its a nickname so a new thread should get started
        #print(message.decode())
        #message = message.decode()
        #if(message.startswith("[[[")):
            #nickname = message
            #nickname = nickname[3:]
            #nickNameChooser(server_socket, nickname, clientAddress)
            #receive_thread = threading.Thread(target=serverRequestsHandler, args=(server_socket, nicknames, nickname, clientAddress))
            #receive_thread.start()
        #else:
            #chatPartner = message.decode()
            #chatPartnerChooser(server_socket, chatPartner, clientAddress)
            #print("We ended up here :(")
        
#output info of the server for clients to be able to connect to it
        

elif(typeOfService == "client"):
        #start client
    client_socket = socket(AF_INET, SOCK_DGRAM) #Note that operating system chooses the port number here

        #wantsToFindOut = True
        #while (wantsToFindOut):
        #print("If you want to disconnect press exit")

        #What server to you want to send it to?
    client_target_server = input("Please choose your server: ")
    nickname = input("Please choose your nickname: ")
    nickname = "[[[" + nickname
    client_socket.sendto(nickname.encode(), (client_target_server, serverPort)) 
        
        
        #client_socket.sendto(nickname.encode(), (serverName, serverPort)) #The server will be listening for new nicknames

    serverMessage, serverAddress = client_socket.recvfrom(2048)

    serverAnswer = serverMessage.decode()
    #WHO DO YOU WANT TO CHAT WITH?
    print(serverAnswer) #maybe has to be decoded first, if the client sees this he knows where to chat to or that his partner doesn't exist

    while(serverAnswer == "This nickname is already taken, please choose another one."):
        nickname = input("Please choose a new nickname: ")
        nickname = "[[[" + nickname
        client_socket.sendto(nickname.encode(), (client_target_server, serverPort))
        serverMessage, serverAddress = client_socket.recvfrom(2048)
        serverAnswer = serverMessage.decode()
        print(serverAnswer)
    
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, nickname,))
    receive_thread.start()

    #last print will have been "who do you want to chat with?"
    #If you pass the while loop, the last print will have been: "Who would you like to chat with?"
"""
    wantsToFindOutMore = True
    while(wantsToFindOutMore):
        chatPartner = input()
        client_socket.sendto(chatPartner.encode(), (serverName, serverPort))

        while True:
            serverMessage, serverAddress = client_socket.recvfrom(2048)
            if (serverMessage.decode() == "not registered"):
                chatPartner = input("This person is not registered yet, choose somebody else to chat with:\n")
                client_socket.sendto(chatPartner.encode(), (serverName, serverPort))
                continue
            else:
                #Here you have to then send the message to the person
                chatPartner_address = serverMessage.decode()
                send_thread = threading.Thread(target=startChat, args=(chatPartner_address,client_socket,))
                send_thread.start()
                #print(serverMessage.decode())
                #break
        #condition = input("Do you want information on anybody else? Type 'yes' or 'no': ")
        #if (condition == "no"):
        #    print("Have a nice day!")
        #    wantsToFindOutMore = False
        #else:
        #    print("Who do you want to chat with: ")
"""