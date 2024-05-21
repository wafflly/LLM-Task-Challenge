import json
import re
import os

# Function to create and update the confusion matrix
def update_confusion_matrix(matrix, actual, predicted, labels):
    if actual in labels and predicted in labels:
        matrix[actual][predicted] += 1

# Specify the directory containing JSON files
input_directory = 'datasets/task 4/original'
output_directory = 'datasets/task 4/original'

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

files = [f for f in os.listdir(input_directory) if f.endswith('.json')]

for input_file_name in files:
    input_file_path = os.path.join(input_directory, input_file_name)
    output_file_name = input_file_name.replace('.json', '.txt')
    output_file_path = os.path.join(output_directory, output_file_name)

    with open(input_file_path, 'r') as file:
        data = json.load(file)

    if "SOV" in input_file_name:
        labels = ["SOV", "SVO", "VSO", "SVO&SOV"]
    elif "PP_before_verb" in input_file_name:
        labels = ["PP after", "PP before", "no PP", "before&after"]
    elif "PP_before_noun" in input_file_name:
        labels = ["PP after", "PP before", "no PP", "before&after"]

    output_data = []
    conf_matrix = {label: {inner_label: 0 for inner_label in labels} for label in labels}
    total_questions = 0
    correct_answers = 0

    response_to_label = {
        # Map responses to labels (abbreviated for brevity)
        "Language A follows SVO word order": "SVO",
        "Language A follows SOV word order": "SOV",
        "Language A follows VSO word order": "VSO",
        "Language A follows either SVO or SOV word order": "SVO&SOV",
        "Language A follows only SVO word order": "SVO",
        "Language A follows only SOV word order": "SOV",
        "Language A follows only VSO word order": "VSO",
        "Language A follows either SVO or SOV word order": "SVO&SOV",
        "Prepositional phrase appears only after the modified verb": "PP after",
        "Prepositional phrase appears only before the modified verb": "PP before",
        "Language A does not have prepositional phrases that modify the verb; it has only postpositional phrases": "no PP",
        "Prepositional phrase can appear either before or after the modified verb": "before&after",
        "Prepositional phrase appears only after the modified noun": "PP after",
        "Prepositional phrase appears only before the modified noun": "PP before",
        "Language A does not have prepositional phrases that modify the noun; it has only postpositional phrases": "no PP",
        "Prepositional phrase can appear either before or after the modified noun": "before&after"
    }

    for item in data:
        prompt_data = {
            "Prompt": item.get("data", ""),
            "Correct_Answer": item.get("correct_answer", ""),
            "LLM_Output_Content": item.get("llm-output", ""),
            "correctness": "Wrong"
        }

        correct_answer = item.get("correct_answer", "").strip()
        llm_output = item.get("llm-output", "").strip()
        options = item.get("options", [])
        pattern1 = re.search(r"\[([A-D])\.\s[^\]]+\]", llm_output)
        pattern2 = re.search(r"\[([A-D])\]", llm_output)
        llm_response = None

        if pattern1:
            llm_response = pattern1.group(0).strip('[]')
        elif pattern2:
            option_letter = pattern2.group(1)
            if option_letter and len(options) >= ord(option_letter) - ord('A'):
                llm_response = options[ord(option_letter) - ord('A')]

        correct_answer_text = re.sub(r'^[A-D]\.\s', '', correct_answer)
        llm_response_text = re.sub(r'^[A-D]\.\s', '', llm_response) if llm_response else None
        actual_label = response_to_label.get(correct_answer_text, None)
        predicted_label = response_to_label.get(llm_response_text, None)

        if actual_label and predicted_label:
            update_confusion_matrix(conf_matrix, actual_label, predicted_label, labels)
            total_questions += 1
            if actual_label == predicted_label:
                correct_answers += 1
                prompt_data["correctness"] = "CORRECT"
            else:
                prompt_data["correctness"] = "INCORRECT"
        output_data.append(prompt_data)

    accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    with open(output_file_path, 'w') as output_file:
        count = 0
        for prompt_data in output_data:
            count += 1
            output_file.write("Index: " + str(count) + "\n")
            output_file.write("Prompt:\n" + prompt_data["Prompt"] + "\n\n")
            output_file.write("Correct Answer:\n" + prompt_data["Correct_Answer"] + "\n\n")
            output_file.write("LLM Output Content:\n" + prompt_data["LLM_Output_Content"] + "\n\n")
            output_file.write("R/W:\n" + prompt_data["correctness"] + "\n\n")
            output_file.write("------------------------------------------------------------\n")
        
        output_file.write("\nConfusion Matrix:\n")
        output_file.write(" " * (max(len(label) for label in labels) + 2))
        for label in labels:
            output_file.write(f"{label:{max(len(label) for label in labels) + 2}}")
        output_file.write("\n")

        for actual, preds in conf_matrix.items():
            output_file.write(f"{actual:{max(len(label) for label in labels) + 2}}")
            for pred in labels:
                output_file.write(f"{preds[pred]:<{max(len(label) for label in labels) + 2}}")
            output_file.write("\n")

        output_file.write(f"\nAccuracy: {accuracy:.2f}%\n")

    print(f"Output file '{output_file_path}' created successfully.")

print("All files processed successfully.")
