import openai
from config import config 
import json
from tqdm import tqdm
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

openai.api_key = config['openai_key']

def get_response(messages, model='gpt-4-1106-preview'):  #gpt-3.5-turbo-0125 gpt-4-1106-preview
    t = 0
    success = False
    response = None

    while not success and t < 5:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.4,
                max_tokens=2048,
                top_p=0,
                frequency_penalty=0,
                presence_penalty=0,
                seed=42
                # logprobs=True,
                # top_logprobs=2
            )
            success = True
        except Exception as e:
            print(f'Request failed with exception: {e}')
            t += 1
            time.sleep(20)
            print(f'Retry #{t}')

    if response:
        response_text = response['choices'][0]['message']['content']
        return response
    else:
        return "Error: Failed to get response after multiple attempts."

def process_file(input_file, output_dir):
    output_file = os.path.join(output_dir, os.path.basename(input_file))
    print(f"Processing {input_file}... Output will be saved to {output_file}")

    with open(input_file, 'r', encoding='utf8') as prompts_file:
        prompt_data = json.load(prompts_file)

    existing_output_content = []
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf8') as f:
            existing_output_content = json.load(f)

    prompt_data = prompt_data[len(existing_output_content):]

    for entry in tqdm(prompt_data, desc=f"Processing {os.path.basename(input_file)}"):
        input_text = entry['data']
        messages = [{"role": "user", "content": input_text}]


        response = get_response(messages)
        response_text = response['choices'][0]['message']['content']


        entry['llm_output'] = {'content': response_text}
        entry['sys_info'] = {'content': response}
        existing_output_content.append(entry)

    with open(output_file, 'w', encoding='utf8') as f:
        json.dump(existing_output_content, f, indent=2, ensure_ascii=False)

def main(input_files, output_dir):
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_file, input_file, output_dir): input_file for input_file in input_files}
        for future in as_completed(futures):
            input_file = futures[future]
            try:
                future.result() 
            except Exception as exc:
                print(f'{input_file} generated an exception: {exc}')

if __name__ == '__main__':

########### read in files ##############
    # input_files = [
    #     'exemple.txt'
    # ]
    # output_dir = 'xx/xx'
    # os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists
    # main(input_files, output_dir)

########### read in directory ##############


    input_directory = 'datasets/task 3'
    output_dir = 'results/task 3/intermediate'
    input_files = [os.path.join(input_directory, filename) for filename in os.listdir(input_directory) if filename.endswith(".json")]
    os.makedirs(output_dir, exist_ok=True) 
    main(input_files, output_dir)

    input_directory2 = 'datasets/task 4'
    output_dir2 = 'results/task 4'
    input_files2 = [os.path.join(input_directory2, filename) for filename in os.listdir(input_directory2) if filename.endswith(".json")]
    os.makedirs(output_dir2, exist_ok=True)
    main(input_files2, output_dir2)