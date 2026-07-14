#!/bin/bash

#The following function interfaces can be invoked by any of the local
#replicas(repos). They collectively shape the entire chatroom

# Function to perform topological sort
topological_sort() {
    local branch=$1
    local commit=$2

    # Mark commit as visited
    visited["$commit"]=true

    # Visit parent commits
    for parent_commit in $(git log --pretty=format:%P -n 1 $commit); do
        # Check if parent commit is from the same branch
        if [[ $(git branch --contains $parent_commit) == *$branch* && ! ${visited["$parent_commit"]} ]]; then
            topological_sort $branch $parent_commit
        fi
    done

    # Output commit message
    git log --pretty=format:"%s" -n 1 $commit
}

#Show function: Use the hash from HEAD as the starting point for the topsort
show() {
    local branches=("Bob" "Alice") #Get these programatically from the .git/refs/heads folder (maybe do later)

    # Iterate through branches
    for branch in "${branches[@]}"; do
        #echo "Branch: $branch"
        local commits=$(git rev-list --topo-order $branch)
        
        # Initialize visited array
        declare -A visited
        
        # Iterate through commits
        for commit in $commits; do
            # Check if commit has already been visited
            if [[ ! ${visited["$commit"]} ]]; then
                topological_sort $branch $commit
            fi
        done
    done
}

# Example usage:
show


