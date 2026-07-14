#!/bin/bash

#This script automates the process from the previous steps in this exercise

./initialize.sh Alice >/dev/null
./initialize.sh Bob >/dev/null
cd Alice/
git remote add bob ../Bob >/dev/null
git push -q bob Alice >/dev/null
cd ../Bob #dont need this
cd ../Alice
../post.sh "Hello, everyone! I'm here." >/dev/null
git push -q bob Alice >/dev/null
cd ../Bob
../post.sh "Hello, Alice! I'm new here too." >/dev/null
git remote add alice ../Alice >/dev/null
git push -q alice Bob >/dev/null

#Some new commands not done manually before
cd ../Alice
../post.sh "How are you Bob?" >/dev/null
git push -q bob Alice >/dev/null
cd ../Bob
../post.sh "Good thx and you?" >/dev/null
git push -q alice Bob >/dev/null
cd ../Alice
../post.sh "Doing fine." >/dev/null
git push -q bob Alice >/dev/null

../show.sh



#automate() {
    
#}

# Example usage:
#automate


