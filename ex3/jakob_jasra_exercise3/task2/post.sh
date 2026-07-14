#!/bin/bash

#The following function interfaces can be invoked by any of the local
#replicas(repos). They collectively shape the entire chatroom

#THIS FUNCTION SHOULD NOW BE WORKING
#Post function:
post() {
    message=$1
    #Get the name of the repository to send the message under this name
    # Get the base name of the current working directory aka the sending repository
    current_dir=$(basename "$PWD")
    #echo "Current working directory/sending repository: $current_dir"
    # Get the current time
    current_time=$(date +"%H:%M:%S") #current_time=$(date +"%Y-%m-%d %H:%M:%S")

    # Create the commit message including the current directory name
    commit_message="$current_dir ($current_time): $message" #"$current_dir: $message"

    #echo $commit_message
    #make commit and

    #Choose as parent the hash currently stored in ./Bob/.git/refs/heads/Bob and all the hashes of all the other repos stored in
    #./Bob/.git/refs/heads/ because these are all the heads which should always be the most recent messages
    #First hash is Bobs own linked list parent so to speak

    # Run the git cat-file command and filter the output to find the tree hash
    tree_hash=$(git cat-file --batch-all-objects --batch-check | awk '$2 == "tree" {print $1}')

    # Print the hash of the tree object
    #echo "Hash of the tree object: $tree_hash"

    #DON'T GET BOBS PARENT SEPARATELY DO THIS CHECKING STH LIKE: PARENT HOWS HASH MESSAGE STARTS WITH Bob LATER!!!
    #Get Bobs actual bob parent
    # Store the contents of the file into a variable
    #bobs_parent=$(<".git/refs/heads/Bob")

    # Print the contents of the variable
    #echo "Bob's parent hash: $bobs_parent"

    # Initialize an empty array to store parent hashes
    parent_hashes=()

    # Iterate over files in the .git/refs/heads directory, only include branch heads
    for file in .git/refs/heads/*; do
        # Check if the file is a regular file (not a directory or symlink)
        if [ -f "$file" ]; then
            # Read the contents of each file and add it to the parent_hashes array
            parent_hashes+=($(<"$file"))
        fi
    done

    # Convert the array of parent hashes into a space-separated string
    parent_hashes_string=$(printf " -p %s" "${parent_hashes[@]}")

    # Remove leading whitespace from the parent_hashes_string
    parent_hashes_string=${parent_hashes_string# }

    #This seems to output the correct thing but somehow it doesn't work below :/
    echo "parent_hashes_string: $parent_hashes_string"

    #WORKS TILL HERE!
    # Create the commit with dynamically added parent hashes
    commit_hash=$(git commit-tree $tree_hash -m "$commit_message" $parent_hashes_string) #$parent_hashes_string)  #normally $ just after "

    #Now after creating the (offline message) update the vector clock, to keep track of the local frontiers

    python3 ../vector_clock.py "$current_dir" #increment the vector clock and pass the directory meaning the user that is posting, so that correct process can be incremented


    #Get all the frontiers programatically:

    # Create the commit with the generated commit message
    #commit_hash=$(git commit-tree $tree_hash -m "$commit_message" -p $bobs_parent -p)

    #git commit-tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904 -m "Bob joined the chatroom" -p 4d4a4d6fd54644451ac7ba5c2552d13687ec8b93


    #Move the HEAD, -> this means put the hash of the just created commit bzw. message into the ./Bob/.git/refs/heads/Bob file
    #(which Bobs .git/HEAD always points to anyways, basically change what the pointer points to)
    #I think this is also what this line basically means to say: "The commit should then be appended at the end of the branch associated with the user who is posting the message"
    #Because ./Bob/.git/refs/heads/Bob this file is basically the pointer I think because 'branches are pointers to commit objects' so by moving the head I think we append it because we can now find it
    #With the HEAD or the ./Bob/.git/refs/heads/Bob file but we also get the whole chat history because of the parents, of this new commit
    # Overwrite the contents of the file with the new commit hash
    echo "$commit_hash" > .git/refs/heads/$current_dir
}

# Example usage:
post "$1"


