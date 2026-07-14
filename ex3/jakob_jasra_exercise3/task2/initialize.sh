#!/bin/bash

#The following function interfaces can be invoked by any of the local
#replicas(repos). They collectively shape the entire chatroom


#Initialize function:
initialize() {
    name=$1
    
    # Initialize a new git repository with the name 'name', -> Slide .. for the more 'internal' commands
    mkdir $name
    cd $name
    mkdir .git
    mkdir .git/objects
    mkdir .git/refs
    mkdir .git/refs/heads
    #Initialize a branch named $name
    #DEBUGGING:
    echo "Setting HEAD reference to refs/heads/$name"
    correctPath="ref: refs/heads/$name"
    echo $correctPath > .git/HEAD #active branch is now the string of $name
    #git status

    #Now preparing the initial commit
    #Create the tree object that does not reference any blob. This tree object should be utilized in all subsequent commit objects that you create. -> S. 40
    #For a commit we need a tree
    #do I first have to navigate into the objects folder or is it fine to do this here? -> no don't have to do this, git does internally
    tree_hash=$(git write-tree)
    #tree_hash=$(git hash-object -t tree /dev/null)
    #DEBUGGING:
    echo "The value of tree_hash is: $tree_hash"
    #S.41 THIS IS THE COMMIT: #how can I get the TREE_HASH here in the script -> ChatGPT

    initial_commit_hash=$(git commit-tree $tree_hash -m "$name joined the chatroom") #no [-p parent_hash] yet since this is the root commit
    #git commit-tree $tree_hash -m "$name joined the chatroom"

    current_dir=$(basename "$PWD")
    #echo "$current_dir"

    python3 ../vector_clock.py "$current_dir" #increment the vector clock and pass the directory meaning the user that is posting, so that correct process can be incremented


    #6. Helpt others find your commit -> S. 42
    #DEBUGGING:
    echo "Writing initial commit hash $initial_commit_hash to .git/refs/heads/$name"
    #anotherCorrectPath=".git/refs/heads/$name"
    #echo $initial_commit_hash > .git/refs/heads/$name

    touch .git/refs/heads/$name
    echo "$initial_commit_hash" > .git/refs/heads/$name

    git log --graph --oneline
}

# Example usage:
initialize "$1"


