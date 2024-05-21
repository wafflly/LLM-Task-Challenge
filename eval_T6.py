import json
import re
import time
import os
from src.api.chat import *

if __name__ == '__main__':

    path = 'datasets/task 6'
    # path = 'src/deduction/error_test/'

    files = os.listdir(path)
    for file in files:
        data_acc = dict()
        data_acc['accuracy'] = ''
        data_acc['invalid'] = ''
        data_acc['data'] = list()
        file_path = os.path.join(path, file)
        # Check if the path is a file (not a subdirectory)
        # if os.path.isfile(file_path):
        if os.path.isfile(file_path) and file[-1] == 'n':
            with open(file_path, 'r') as f:
                all_data = json.load(f)
                total = len(all_data)
                correct = 0
                inval = 0
                for i in all_data:
                    j = dict()
                    prompt = i['prompt']
                    j['prompt'] = prompt
                    cont = get_answer_4(prompt)
                    print(cont)
                    j['output'] = cont

                    # find all the sentence numbers mentioned in the response
                    digits = re.findall(r'\b\d\b', cont)
                    if digits:
                        uni_d = set()
                        for d in digits:
                            new_d = d.replace('\'', '')
                            uni_d.add(new_d)
                        out_evidence = sorted(list(uni_d))
                    else:
                        out_evidence = None

                    results = re.findall(r'\[(.*?)\]', cont)
                    if results:
                        result = results[-1]
                        word = result.split()[0]
                        out_label = word.rstrip('.').upper()
                        if out_label == i['gold_choice']:
                            correct += 1
                            j['result'] = 'right'
                        else:
                            j['result'] = 'wrong'
                    else:
                        inval += 1
                        out_label = None
                        j['result'] = 'invalid'
                    j['gold_label'] = i['gold_label']
                    j['gold_choice'] = i['gold_choice']
                    j['out_choice'] = out_label
                    j['gold_evidence'] = i['gold_evidence']
                    j['out_evidence'] = out_evidence
                    data_acc['data'].append(j)

                data_acc['accuracy'] = '{}/{}={}'.format(str(correct), str(total), str(correct/total))
                data_acc['invalid'] = '{}/{}={}'.format(str(inval), str(total), str(inval/total))

            with open('results/task 6/acc_{}'.format(file), 'w', encoding='utf8') as f1:
                json.dump(data_acc, f1, ensure_ascii=False, indent=4)

