import time

import openai
from .config import config

# find more instructions at
# https://platform.openai.com/docs/api-reference/chat


def get_answer_4(prompt):

    openai.api_key = config['openai_key']
    input_text = prompt
    messages = [{"role": "user", "content": input_text}]
    # role: user or assistant
    # find all models at
    # https://platform.openai.com/docs/models
    t = 0
    success = False

    while not success:
        try:
            response = openai.ChatCompletion.create(
                # model="gpt-3.5-turbo-1106",
                model='gpt-4-1106-preview',
                messages=messages,
                temperature=0.4,
                max_tokens=2048,
                top_p=0,
                frequency_penalty=0,
                presence_penalty=0,
                seed=42,
                logprobs=True,
                top_logprobs=2
            )
            success = True
        except Exception as e:
            t += 1
            time.sleep(10)
            print('request failed, try {}'.format(t))
            # print("Error type:", type(e).__name__)
            # print("Error message:", str(e))

    response_text = response['choices'][0]['message']['content']
    return response_text


def get_answer_3(prompt):
    openai.api_key = config['openai_key']
    input_text = prompt
    messages = [{"role": "user", "content": input_text}]
    # role: user or assistant
    # find all models at
    # https://platform.openai.com/docs/models

    t = 0
    success = False

    while not success:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-1106",
                # model='gpt-4-1106-preview',
                messages=messages,
                temperature=0.4,
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            success = True
        except Exception:
            t += 1
            time.sleep(10)
            print('request failed, try {}'.format(t))

    response_text = response['choices'][0]['message']['content']
    return response_text
