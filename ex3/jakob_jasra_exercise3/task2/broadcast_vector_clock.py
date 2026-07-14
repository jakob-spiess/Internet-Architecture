import json
import socket
import threading
import time
import os

global_frontier = {}
differences_for_each_user = {}

def broadcast_vector_clock(file_path, broadcast_address, broadcast_port, interval):
    
    while True:
        # Load vector clock from JSON file
        with open(file_path, 'r') as file:
            vector_clock = json.load(file)

        # Convert vector clock to string
        vector_clock_str = json.dumps(vector_clock)
        

        # Get the current working directory
        cwd = os.getcwd()

        # Prepend the current working directory followed by "$" to the string
        vector_clock_str = f"{cwd}$" + vector_clock_str

        # Create UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Enable broadcast option
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Send vector clock as broadcast message
            s.sendto(vector_clock_str.encode(), (broadcast_address, broadcast_port))

            #FOR DEBUGGING
            #print("Broadcast sent: " + vector_clock_str)
        
        # Wait for interval before broadcasting again
        time.sleep(interval)

def listen_broadcasts_vector_clock(broadcast_port):
    global global_frontier
    global differences_for_each_user

    # Create UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # Bind socket to listen for broadcasts
        s.bind(('0.0.0.0', broadcast_port))
        
        while True:
            # Receive broadcasted vector clock
            data, _ = s.recvfrom(1024)

            # Assuming 'data' contains the received broadcasted message
            received_message = data.decode()

            #FOR DEBUGGING
            #print("Broadcast received: " + received_message)

            # Split the message at the first occurrence of "$" and take the second part
            received_user, vector_clock_str = received_message.split("$", 1)

            # Deserialize the vector clock string to a dictionary
            received_vector_clock = json.loads(vector_clock_str)

            #received_vector_clock = json.loads(data.decode())

            # Update global_frontier based on received vector clock
            for key, value in received_vector_clock.items():
                if key in global_frontier:
                    global_frontier[key] = max(global_frontier[key], value)
                else:
                    global_frontier[key] = value

            #Write down the global_frontier
            with open('../global_frontier.json', 'w') as file:
                json.dump(global_frontier, file)

            #Store how far behind the current user is:
            # Load vector clock from JSON file
            with open('../vector_clock.json', 'r') as file:
                vector_clock = json.load(file)

            # Iterate through keys of vector_clock.json and global_frontier
            for key in set(vector_clock.keys()).union(global_frontier.keys()):
                # Calculate difference based on key presence in vector_clock and global_frontier
                if key in vector_clock and key in global_frontier:
                    difference = vector_clock[key] - global_frontier[key]
                elif key in vector_clock:
                    difference = vector_clock[key]
                else:
                    difference = -global_frontier[key]

                # Store the difference in differences_for_each_user dictionary
                differences_for_each_user[key] = difference
            
            #write down the differences_for_each_user
            with open('differences_for_each_user.json', 'w') as file: #Put this in the repo since this is individual to each user
                json.dump(differences_for_each_user, file)


            # FOR DEBUGGING:
            #print(differences_for_each_user)


            #Now solve part 3 of the ex2 which is comparing the received vector clock to the global vector clock and
            #setting all the branch references to the latest commits of the different branches:
            update_local_references(received_user, received_vector_clock)


def update_local_references(received_user, received_vector_clock):
    # Check if the branch exists locally
    branch_path = f'.git/refs/heads/{received_user}'
    if os.path.exists(branch_path):
        # Read the commit hash from the local branch
        with open(branch_path, 'r') as file:
            local_commit_hash = file.read().strip()

        # Update the equivalent remote reference
        remote_branch_path = f'.git/refs/remotes/{received_user}'
        with open(remote_branch_path, 'w') as file:
            file.write(local_commit_hash)

        with open('../vector_clock.json', 'r') as file:
            vector_clock = json.load(file)

        # Calculate the difference between local and received vector clocks
        diff = vector_clock.get(received_user, 0) - received_vector_clock.get(received_user, 0)

        # Move back the remote reference if necessary
        if diff > 0:
            for _ in range(diff):
                # Read the (same branch) parent commit hash from the commit message
                parent_commit_hash = get_parent_commit_hash(local_commit_hash, received_user)
                if parent_commit_hash:
                    # Update the remote reference to point to the parent commit
                    with open(remote_branch_path, 'w') as file:
                        file.write(parent_commit_hash)
                    # Update local_commit_hash for next iteration
                    local_commit_hash = parent_commit_hash
                else:
                    # Unable to find parent commit, stop looping
                    break

def get_parent_commit_hash(commit_hash, received_user):
    # Command to get the parent commit hashes of a given commit
    command = f'git log --format=%P -n 1 {commit_hash}'

    # Execute the command and capture the output
    output = os.popen(command).read()

    # Parse the output to get the parent commit hashes
    parent_commit_hashes = output.strip().split()

    # Iterate through parent commit hashes
    for parent_commit_hash in parent_commit_hashes:
        # Check if the commit message starts with the received_user value
        if commit_starts_with_user(parent_commit_hash, received_user):
            return parent_commit_hash
    
    return None

def commit_starts_with_user(commit_hash, user):
    # Command to get the commit message of a given commit
    command = f'git log --format=%s -n 1 {commit_hash}'

    # Execute the command and capture the output
    output = os.popen(command).read()

    # Check if the commit message starts with the user value
    if output.startswith(user):
        return True
    return False

def reinitialize_dictionaries():
    global global_frontier
    global differences_for_each_user

    if os.path.exists('../global_frontier.json'):
        with open('../global_frontier.json', 'r') as file:
            global_frontier = json.load(file)

    if os.path.exists('differences_for_each_user.json'):
        with open('differences_for_each_user.json', 'r') as file:
            differences_for_each_user = json.load(file)



def main():
    file_path = '../vector_clock.json'
    broadcast_address = '<broadcast>'
    broadcast_port = 10000
    broadcast_interval = 10

    reinitialize_dictionaries()

    #if not os.path.exists(file_path):
        #with open(file_path, 'w'):
            #pass
            # You can optionally write initial content to the file
            #file.write("Initial content if needed\n")

    
    # Start broadcast_vector_clock thread
    broadcast_thread = threading.Thread(target=broadcast_vector_clock, args=(file_path, broadcast_address, broadcast_port, broadcast_interval))
    broadcast_thread.daemon = True
    broadcast_thread.start()

    # Start listen_broadcasts_vector_clock thread
    listen_thread = threading.Thread(target=listen_broadcasts_vector_clock, args=(broadcast_port,))
    listen_thread.daemon = True
    listen_thread.start()

    # Main thread can do other work or just wait for threads to finish
    while True:
        time.sleep(1)  # Do some other work here if needed

if __name__ == "__main__":
    main()
