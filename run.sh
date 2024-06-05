#!/bin/bash

# Activate the virtual environment if you are using one
# source venv/bin/activate

# Run all Python evaluation scripts
python3 eval_T1.py
python3 eval_T2.py

python3 src/api/concurrent_chat.py

directory="results/task 3/intermediate"
for json_file in "$directory"/*.json; do
    base_name=$(basename "$json_file" .json)
    txt_file="results/mis/$base_name.txt"
    python3 eval_T3.py "$json_file" > "$txt_file"
done

# Continue running remaining evaluation scripts
python3 eval_T4.py
python3 eval_T5.py
python3 eval_T6.py

# Deactivate the virtual environment if you are using one
# deactivate
