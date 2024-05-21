import json
import re
import time
import os
from src.api.chat import get_answer_4

if __name__ == '__main__':
    path = 'datasets/task 1/length2'
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)):
            if filename == '.DS_Store':
                pass
            else:
                data_acc = dict()
                with open(os.path.join(path, filename), 'r') as f:
                    all_data = json.load(f)
                    total_correct = 0
                    for key in all_data:
                        pairs = all_data[key]
                        data_acc[key] = dict()
                        total = len(pairs)
                        correct = 0
                        inval = 0
                        new_data = []
                        # for each [quest, answer]
                        for pair in pairs:
                            quest = pair[0]
                            gold = round(float(pair[1]), 1)
                            cont = get_answer_4(quest)
                            print('$$$$$')
                            print(cont)
                            # extract things in [] or (), get the last one
                            if '[' in cont:
                                num_result = re.findall(r'\[(.*?)\]', cont)
                                if num_result:
                                    # in case more, get last one
                                    bracket = num_result[-1]
                                    # in case there's an equation within [], [8 + 9 = 17], split, and get the last one
                                    bracket = bracket.replace('\\', '')
                                    numeric = bracket.split()[-1]
                                    # get rid of the ... in the end like in 1.777...
                                    numeric = numeric.rstrip('.')
                                    # in case the final number has , eg 345,678,187; delete ,
                                    if ',' in numeric:
                                        nums = numeric.split(',')
                                        result = ''.join(nums)
                                    else:
                                        result = numeric

                                    try:
                                        result = round(eval(result), 1)
                                    except (ValueError, SyntaxError, NameError):
                                        inval += 1
                                else:
                                    inval += 1

                            else:
                                num_result = re.findall(r'-?\d+\.?\d*', cont)
                                if num_result:
                                    result = numeric[-1]
                                else:
                                    inval += 1

                            new_pair = (quest, gold, result, cont)
                            new_data.append(new_pair)
                            if result == gold:
                                correct += 1
                                total_correct += 1
                            time.sleep(1)
                        acc = correct/total
                        invalid = inval/total
                        total_acc = total_correct / 200
                        data_acc['overall_accuracy'] = '{}/200={}'.format(str(total_correct), str(total_acc))
                        data_acc[key]['accuracy'] = '{}/{}={}'.format(str(correct), str(total), str(acc))
                        data_acc[key]['invalid'] = '{}/{}={}'.format(str(inval), str(total), str(invalid))
                        data_acc[key]['data'] = new_data
                        output_file = 'results/task 1/length2/acc_{}'.format(filename)
                        with open(output_file, 'w', encoding='utf8') as f1:
                            json.dump(data_acc, f1, ensure_ascii=False, indent=4)

