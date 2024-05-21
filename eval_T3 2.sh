#!/bin/bash

# Set the directory where the JSON files are located
directory="datasets/task 3/base"
# Loop through all JSON files in the specified directory
for json_file in "$directory"/*.json; do
    # Get the base name of the file without the extension
    base_name=$(basename "$json_file" .json)
     
    # Define the output file name by replacing json extension with txt
    txt_file="$directory/$base_name.txt"

    # Run the python script to process the JSON file and output to TXT
    python3.10 goldstd.py "$json_file" > "$txt_file"
done