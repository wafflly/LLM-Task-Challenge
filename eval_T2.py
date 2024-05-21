import json
import re
import time
import os
from src.api.chat import get_answer_4

if __name__ == '__main__':
    path = 'datasets/task 2'
    outs = os.listdir(path)
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)) and filename[-1] == 'n':
            data_acc = dict()
            with open(os.path.join(path, filename), 'r') as f:
                all_data = json.load(f)
                total_correct = 0
                total_invalid = 0
                for key in all_data:
                    data_acc[key] = dict()
                    for key2 in all_data[key]:
                        pairs = all_data[key][key2]
                        data_acc[key][key2] = dict()
                        total = len(pairs)
                        correct = 0
                        inval = 0
                        new_data = []
                        # for each [quest, answer]
                        for pair in pairs:
                            quest = pair[0]
                            gold = pair[1]
                            cont = get_answer_4(quest)
                            print('$$$$$')
                            print(cont)
                            # extract things in [] or (), get the last one
                            result = 'Invalid'
                            if '[' in cont:
                                num_result = re.findall(r'\[(.*?)\]', cont)
                                if num_result:
                                    # in case more, get last one
                                    bracket = num_result[-1]
                                    # in case there's an equation within [], [8 + 9 = 17], split, and get the last one
                                    bracket = bracket.replace('\\', '')
                                    result = bracket.split()[-1]
                                else:
                                    inval += 1
                                    total_invalid += 1

                            else:
                                inval += 1
                                total_invalid += 1

                            new_pair = (quest, gold, result, cont)
                            new_data.append(new_pair)
                            if result == gold:
                                correct += 1
                                total_correct += 1
                        acc = correct/total
                        invalid = inval/total
                        total_acc = total_correct / 200
                        total_inval_rate = total_invalid / 200
                        data_acc['overall_accuracy'] = '{}/200={}'.format(str(total_correct), str(total_acc))
                        data_acc['overall_invalid'] = '{}/200={}'.format(str(total_invalid), str(total_inval_rate))
                        data_acc[key][key2]['accuracy'] = '{}/{}={}'.format(str(correct), str(total), str(acc))
                        data_acc[key][key2]['invalid'] = '{}/{}={}'.format(str(inval), str(total), str(invalid))
                        data_acc[key][key2]['data'] = new_data
                        output_file = 'results/task 2/acc_{}'.format(filename)
                        with open(output_file, 'w', encoding='utf8') as f1:
                            json.dump(data_acc, f1, ensure_ascii=False, indent=4)
