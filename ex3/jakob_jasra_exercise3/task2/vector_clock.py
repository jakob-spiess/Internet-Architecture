import json
import sys
import os

# Function to load vector clock from a JSON file
def load_vector_clock(file_path):

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return {}

# Function to save vector clock to a JSON file
def save_vector_clock(file_path, vector_clock):
    with open(file_path, 'w') as file:
        json.dump(vector_clock, file)

# Main function
def main():
    # Check if command line argument is provided
    if len(sys.argv) != 2:
        print("Usage: python script.py <key>")
        return

    key = sys.argv[1]

    #FOR DEBUGGING
    #current_dir = os.getcwd()
    #print("Current working directory:", current_dir)

    # Load vector clock from JSON file
    vector_clock = load_vector_clock('../vector_clock.json')

    #FOR DEBUGGING
    #print("Vector clock:", vector_clock)

    # Increment value for the provided key or initialize it to 1 if it doesn't exist
    vector_clock[key] = vector_clock.get(key, 0) + 1

    # Save vector clock to JSON file
    save_vector_clock('../vector_clock.json', vector_clock)

    #FOR DEBUGGING
    print("Vector clock:", vector_clock)

if __name__ == "__main__":
    main()
