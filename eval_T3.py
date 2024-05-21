import spacy
import json
import string
import argparse
import re
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import corpus_bleu
from nltk.translate import meteor_score
from nltk.tokenize import word_tokenize

import traceback

def debug_caller_info():
    # This function prints the caller's details
    stack = traceback.extract_stack()
    # Get the last entry in the stack, which is the one for the caller of this function
    filename, line_number, function_name, text = stack[-2]
    print(f"Called from {filename} at line {line_number}, in {function_name}()")



def process_sentences_from_json(json_file):
    with open(json_file, 'r') as file:
        sentences = json.load(file)
    return sentences

def apply_sov(token_info_list):
    subj_list = []
    obj_list = []
    obj_related_tokens = []
    sub_related_tokens = []
    replace_idx = 0
    # Identify the main verb and its associated subject and object
    for token in token_info_list:
        if token[2] == 'ROOT' and token[3] == 'VERB':
            replace_idx = token[0]

            # Find the subject and object of the main verb
            subject = next((t for t in token_info_list if t[7] == token[0] and t[2] == 'nsubj'), None)
            subj_list.append(subject)
            # sub_related_tokens += [t for t in token_info_list if t[7] == subject[0]]
            sub_related_tokens = collect_related_tokens(token_info_list, subject[0], set())
            sub_related_tokens = [list(t) for t in sub_related_tokens]  # Convert tuples back to lists
            subj_list.extend(sub_related_tokens)

            obj = next((t for t in token_info_list if t[7] == token[0] and t[2] == 'dobj'), None)
            
            if obj:
                obj_list.append(obj)    
                obj_related_tokens = collect_related_tokens(token_info_list, obj[0], set())
                obj_related_tokens = [list(t) for t in obj_related_tokens]  # Convert tuples back to lists
                obj_list.extend(obj_related_tokens)

    if subj_list and obj_list:
        subj_indices = [item[0] for item in subj_list]
        subj_min_index = min(subj_indices)
        subj_max_index = max(subj_indices)

        subj_additional_tokens = [t for t in token_info_list if subj_min_index < t[0] < subj_max_index and t[0] not in set(t[0] for t in subj_list)]
        subj_list.extend(subj_additional_tokens)
        subj_list.sort(key=lambda x: x[0])

        obj_indices = [item[0] for item in obj_list]
        obj_min_index = min(obj_indices)
        obj_max_index = max(obj_indices)

        obj_additional_tokens = [t for t in token_info_list if obj_min_index < t[0] < obj_max_index and t[0] not in set(t[0] for t in obj_list)]
        obj_list.extend(obj_additional_tokens)
        obj_list.sort(key=lambda x: x[0])

        first_in_obj = obj_list[0][0]
        travel = abs(first_in_obj - replace_idx)

        insertion_index = subj_max_index +1 if obj_min_index > 0 else 0

        for i, token in enumerate(obj_list):
            token_info_list.remove(token)
            token[0] = replace_idx + i

        for token in obj_list:
            if token[7] != replace_idx:
                token[7] -= travel
            elif token[7] == replace_idx:
                token[7] = replace_idx + len(obj_list)

        for token in token_info_list:
            if token[7] == replace_idx:
                token[7] = replace_idx + len(obj_list)

        token_info_list[insertion_index:insertion_index] = obj_list

        for i, token in enumerate(token_info_list[insertion_index + len(obj_list):]):
            token[0] = insertion_index + len(obj_list) + i

    return token_info_list, subj_list



def apply_adv_before_verb(token_info_list):
    my_list = []
    replace_idx = 0
    processed_indices = set()
    debug_caller_info()
    for token in token_info_list:
        if token[2] == 'advmod' and token[5] == 'VERB' and token[0] not in processed_indices:
            replace_idx = token[7]
            my_list.append(token)
            related_tokens = collect_related_tokens(token_info_list, token[0], processed_indices)
            related_tokens = [list(t) for t in related_tokens]  # Convert tuples back to lists
          
            my_list.extend(related_tokens)
            processed_indices.update(set(t[0] for t in my_list))

    if my_list:
        indices = [item[0] for item in my_list]
        min_index = min(indices)
        max_index = max(indices)

        additional_tokens = [t for t in token_info_list if min_index < t[0] < max_index and t[0] not in processed_indices]
        my_list.extend(additional_tokens)
        my_list.sort(key=lambda x: x[0])


        first_in_pp = my_list[0][0]
        last_in_pp = my_list[-1][0]
        travel = abs(first_in_pp - replace_idx)
        insertion_index = replace_idx if min_index > 0 else 0

        for i, token in enumerate(my_list):
            token_info_list.remove(token)
            token[0] = insertion_index + i

        for token in my_list:
            if token[7] != replace_idx:
                token[7] -= travel
            elif token[7] == replace_idx:
                token[7] = replace_idx + len(my_list)
    
        for token in token_info_list:
            if token[7] == replace_idx:
                token[7] = replace_idx + len(my_list)
            elif last_in_pp > token[7] > replace_idx:
                token[7] += len(my_list) 

        token_info_list[insertion_index:insertion_index] = my_list
        print("my_list:  ",my_list)



        for i, token in enumerate(token_info_list[insertion_index + len(my_list):]):
            token[0] = insertion_index + len(my_list) + i
        
        print("token_info_list:  ",token_info_list)


    return token_info_list,my_list

def apply_pp_before_noun(token_info_list):
    my_list = []
    replace_idx = 0
    nonun_phrase = []
    
    def process_token(token):
        nonlocal my_list, replace_idx, nonun_phrase
        replace_idx = token[7]
        my_list.append(token)
        related_tokens = collect_related_tokens(token_info_list, token[0], set())
        related_tokens = [list(t) for t in related_tokens]  # Convert tuples back to lists
        my_list.extend(related_tokens)

        nonun_phrase = [t for t in token_info_list if t[0] == token[7] or (t[7] == token[7] and t[0] != token[0])]

    for token in token_info_list:
        if token[2] == 'prep' and token[5] == 'NOUN' and token_info_list[token[7]][2] == 'nsubj' and token[0] not in set(t[0] for t in my_list):
            process_token(token)

    if my_list:
        indices = [t[0] for t in my_list]
        min_index = min(indices)
        max_index = max(indices)
        additional_tokens = [t for t in token_info_list if min_index < t[0] < max_index and t[0] not in set(t[0] for t in my_list)]
        my_list.extend(additional_tokens)
        my_list.sort(key=lambda x: x[0])

        np_len = len(nonun_phrase)
        ml_len = len(my_list)

        first_in_pp = my_list[0][0]
        travel = abs(first_in_pp - replace_idx)

        # Remove the elements from my_list and adjust their index
        for i, token in enumerate(my_list):
            token_info_list.remove(token)
            token[0] = replace_idx - np_len + i + 1

        for token in my_list:
            if token[7] != replace_idx:
                token[7] -= np_len
            elif token[7] == replace_idx:
                token[7] = replace_idx + len(my_list)

        for token in token_info_list:
            if token[7] == replace_idx:
                token[7] = replace_idx + len(my_list)

        # Insert the removed elements into token_info_list at the desired index
        token_info_list[replace_idx - np_len + 1:replace_idx - np_len + 1] = my_list

        # Update indices for elements pushed back in token_info_list
        for i, token in enumerate(token_info_list[replace_idx + len(my_list) - 2:]):
            token[0] = replace_idx + ml_len + i - 2

    return token_info_list, my_list

def collect_related_tokens(token_info_list, start_index, processed_indices):
    """
    Recursively collect unique tokens related to the token at start_index.
    """
    related_tokens = set()
    for t in token_info_list:
        if t[7] == start_index and t[0] not in processed_indices:
            related_tokens.add(tuple(t))  # Convert the list to a tuple
            processed_indices.add(t[0])
            related_tokens.update(collect_related_tokens(token_info_list, t[0], processed_indices))
    return related_tokens

def apply_pp_before_verb(token_info_list):
    debug_caller_info()
    my_list = []
    replace_idx = 0
    processed_indices = set()

    def process_token(token):
        nonlocal my_list, replace_idx, processed_indices
        replace_idx = token[7]
        my_list.append(token)
        related_tokens = collect_related_tokens(token_info_list, token[0], processed_indices)
        related_tokens = [list(t) for t in related_tokens]  # Convert tuples back to lists

        my_list.extend(related_tokens)
        processed_indices.update(set(t[0] for t in my_list))
        
    for token in token_info_list:

        if token[2] == 'prep' and token[5] == 'VERB' and token[0] not in processed_indices:
            # print("hello")
            process_token(token)

    if my_list:
        indices = [item[0] for item in my_list]
        min_index = min(indices)
        max_index = max(indices)
        additional_tokens = [t for t in token_info_list if min_index < t[0] < max_index and t[0] not in processed_indices]
        my_list.extend(additional_tokens)
        my_list.sort(key=lambda x: x[0])

        first_in_pp = my_list[0][0]
        last_in_pp = my_list[-1][0]

        travel = abs(first_in_pp - replace_idx)

        insertion_index = replace_idx if min_index > 0 else 0
        for i, token in enumerate(my_list):
            token_info_list.remove(token)
            token[0] = replace_idx + i

        for token in my_list:
            if token[7] != replace_idx:
                token[7] -= travel
            elif token[7] == replace_idx:
                token[7] = replace_idx + len(my_list)

        for token in token_info_list:
            if token[7] == replace_idx:
                token[7] = replace_idx + len(my_list)
            elif last_in_pp > token[7] > replace_idx:
                token[7] += len(my_list)

        token_info_list[insertion_index:insertion_index] = my_list
        for i, token in enumerate(token_info_list[insertion_index + len(my_list):]):
            token[0] = insertion_index + len(my_list) + i

    # print("token_info_list before:\n")
    # for token in token_info_list:
    #     print(token, "\n")



    # token_info_list,_ = apply_adv_before_verb(token_info_list)



    return token_info_list, my_list

def apply_rules(morph_rules,sentence_rules,token_info_list):
    for rule in sentence_rules:
        token_info_list,_ = rule(token_info_list)
    for rule in morph_rules:
        token_info_list = rule(token_info_list)


    modified_sentence = " ".join([token[1] for token in token_info_list])
    return token_info_list, modified_sentence


def parse_output_to_list(lines):
    token_info_list = []
    subject, verb = None, None
    for line in lines:
        parts = line.strip().split(' -> ')
        if len(parts) >= 10:
            parts = [None if part == "None" else part for part in parts]
            index, text, dep, pos, head_text, head_pos, tag, head_index, placeholder, lemma = parts[:10]
            index = int(index)
            head_index = int(head_index)
            
            # Check for subject and verb in the dep part for spaCy output
            if dep == "nsubj":
                subject = text
            if dep == "ROOT":
                verb = text

            token_info_list.append([index, text, dep, pos, head_text, head_pos, tag, head_index, placeholder, lemma])
    
    return token_info_list, subject, verb



def reverse_translate(message, translation_dict):
    reversed_translation_dict = {v: k for k, v in translation_dict.items()}
    words = message.split()
    reversed_message = " ".join(reversed_translation_dict.get(word, word) for word in words)
    return reversed_message


def morph_sp(token_info_list):
    for token in token_info_list:
        if token[3] == 'NOUN' and token[6] == 'NNS':
            # token[1] = 'P_' + token[1]
            token[8] = 'P'
        if token[3] == 'NOUN' and token[6] == 'NN':
            # token[1] = 'S_' + token[1]
            token[8] = 'S'
    return token_info_list

def morph_adj(token_info_list):
    for token in token_info_list:
        if token[3] == 'ADJ' and token[6] == 'JJ':
            # token[1] = token[1]+' '+token[1]
            token[8] = 'JJ'
        elif token[5] == 'NOUN' and token[6] == 'VBG':
            # token[1] = token[1]+' '+token[1]
            token[8] = 'JJ'
        elif token[2] == 'amod' and token[5] == 'NOUN' and token[6] == 'VBN':
            token[8] = 'JJ'
        elif token[2] == 'amod' and token[5] == 'NOUN' and token[6] == 'NN':
            token[8] = 'JJ'

    return token_info_list

def morph_tense(token_info_list):
    for token in token_info_list:
        if token[3] == 'VERB' and token[6] == 'VBD':
            # token[1] = token[1] + '_-'
            token[8] = 'past'

        if token[3] == 'VERB' and token[6] == 'VBP':
            # token[1] = token[1] + '_+'
            token[8] = 'present'

        if token[3] == 'VERB' and token[6] == 'VBZ':
            # token[1] = token[1] + '_+'
            token[8] = 'present'

    return token_info_list

def get_token_info_and_core_elements_for_sentences(sentences, nlp):
    results = []  # To store results for each sentence
    
    for source_sentence in sentences:  # Iterate over each sentence
        file_path = ''
        if source_sentence == "The dedicated teacher with a gentle voice explains the complex theory lucidly to the class ." or source_sentence == "The dedicated teacher with a gentle voice explains the complex theory lucidly to the class":
            file_path = 'Outlier/teacher.txt'
        elif source_sentence == "The playful dogs at the park chase the bright ball swiftly across the green grass ." or source_sentence == "The playful dogs at the park chase the bright ball swiftly across the green grass":
            file_path = 'Outlier/playful_dog.txt'
        elif source_sentence == "The passionate baker in the warm kitchen bakes the delicious pastries lovingly for the patrons ." or source_sentence == "The passionate baker in the warm kitchen bakes the delicious pastries lovingly for the patrons":
            file_path = 'Outlier/baker.txt'
        elif source_sentence == "The passionate activist at the peaceful rally voices the concerns loudly with a sense of urgency ." or source_sentence == "The passionate activist at the peaceful rally voices the concerns loudly with a sense of urgency":
            file_path = 'Outlier/activist.txt'
        elif source_sentence == "The loyal dog in the sunny yard guards the house vigilantly with a watchful stance ." or source_sentence == "The loyal dog in the sunny yard guards the house vigilantly with a watchful stance":
            file_path = 'Outlier/loyal_dog.txt'  
        elif source_sentence == "The strong wind from the north sweeps the city entirely with freeze ." or source_sentence == "The strong wind from the north sweeps the city entirely with freeze":
            file_path = 'Outlier/wind.txt'
        elif source_sentence == "The old sailor steers the sturdy ship in danger skillfully through the rough seas ." or source_sentence == "The old sailor steers the sturdy ship in danger skillfully through the rough seas":
            file_path = 'Outlier/sailor.txt'

        # Define your conditions for specific files here
        
        token_info_list = []
        subject, verb = None, None
        
        if file_path:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                token_info_list, subject, verb = parse_output_to_list(lines)
        else:
            doc = nlp(source_sentence)
            for token in doc:
                if token.dep_ == "nsubj" and not subject:
                    subject = token.text
                if token.dep_ == "ROOT" and not verb:
                    verb = token.text
                
                token_info = [
                    token.i,
                    token.text,
                    token.dep_,
                    token.pos_,
                    token.head.text,
                    token.head.pos_,
                    token.tag_,
                    token.head.i,
                    None,  # Placeholder for morph
                    token.lemma_
                ]
                token_info_list.append(token_info)
        
        # Append the results for this sentence to the list of results
        results.append((token_info_list, subject, verb))
    
    return results


def get_token_info_list(source_sentence, nlp):
    if source_sentence == "The dedicated teacher with a gentle voice explains the complex theory lucidly to the class .":
        file_path = 'Outlier/teacher.txt'
    elif source_sentence == "The playful dogs at the park chase the bright ball swiftly across the green grass .":
        file_path = 'Outlier/playful_dog.txt'
    elif source_sentence == "The passionate baker in the warm kitchen bakes the delicious pastries lovingly for the patrons .":
        file_path = 'Outlier/baker.txt'
    elif source_sentence == "The passionate activist at the peaceful rally voices the concerns loudly with a sense of urgency .":
        file_path = 'Outlier/activist.txt'
    elif source_sentence == "The loyal dog in the sunny yard guards the house vigilantly with a watchful stance .":
        file_path = 'Outlier/loyal_dog.txt'  
    elif source_sentence == "The strong wind from the north sweeps the city entirely with freeze .":
        file_path = 'Outlier/wind.txt'
    else:
        file_path = ''

    token_info_list = []
    if file_path:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            token_info_list, subject, verb = parse_output_to_list(lines)
    else:
        doc = nlp(source_sentence)
        morph = None
        subject,verb = "", ""
        for token in doc:
            if token.dep_ == "nsubj" and not subject:
                subject = token.text
            if token.dep_ == "ROOT" and not verb:
                verb = token.text
            token_info = [
                token.i,
                token.text,
                token.dep_,
                token.pos_,
                token.head.text,
                token.head.pos_,
                token.tag_,
                token.head.i,
                morph,
                token.lemma_
            ]
            token_info_list.append(token_info)
    return token_info_list, subject, verb


def main(input_file_path):
    # Load the spaCy model
    nlp = spacy.load("en_core_web_lg")
                        
    json_file_path = 'reverse/test/result/step/1b_syntax_SOV_2.json'
    output_file = 'result/base/gold/sim_long/gold_prompts_output_1S_0M.json'
  
    with open(input_file_path, 'r', encoding='utf8') as prompts_file:
        json_data = json.load(prompts_file)

    s_rules = {
            "SOV": apply_sov,
            "PP before verb": apply_pp_before_verb,
            "Adv verbs": apply_adv_before_verb,
            "PP before noun": apply_pp_before_noun  
             }   #apply_pp_before_verb    apply_pp_before_noun    apply_sov   apply_adv_before_verb
    
    m_rules = {
            "S&P": morph_sp,
            "Tense": morph_tense,
            "ADJ": morph_adj
             } 
    
    reference_sentences = []
    candidate_sentences = []
    total = 0
    correct = 0
    ms_total = 0


    for entry in json_data:
        flag1, flag2, flag3 = False,False,False

        token_info_list = []

        # Extract relevant information
        sentence_rules = entry['rules_used']['sentence_rules']
        morph_rules = entry['rules_used']['morphology_rules']
        source_sentence = entry['source_sentence']
        random_pair = entry['word_pairs']
        prompts = entry['data']
        tgt_pair = entry['word_pairs']

        if 'source_sentence' in entry:

            llm_answer = entry['llm-output']
        else:
            print("Key 'llm-output' not found in entry.")


        print("source_sentence: ",source_sentence )
        print("sentence_rules: ",sentence_rules)
        print("morph_rules: ",morph_rules)
        print("word_pair: ", random_pair)
        print("LLM_response: ",llm_answer)
        print("\nPrompts: ", prompts)
        

        token_info_list = get_token_info_list(entry['source_sentence'], nlp)

        sentence_rules_to_apply = [s_rules[rule] for rule in s_rules if rule in sentence_rules]

        morph_rule_to_apply = [m_rules[rule] for rule in morph_rules if rule in m_rules]
        modified_tree, gold = apply_rules(morph_rule_to_apply,sentence_rules_to_apply, token_info_list[0])

        if flag1:
            if "violet" in gold:
                gold = gold.replace("violet", "rose")

        elif flag2:
            if "sands" in gold:
                gold = gold.replace("sands", "leaves")

        elif flag3:
            if "grew" in gold:
                gold = gold.replace("grew", "plants")

        # llm_answer = entry["llm_output"]["content"].split('[')[1].split(']')[0]
        matches = re.findall(r'\[([^[\]]+)\]', llm_answer)
        llm_answer = matches[-1] if matches else 0

        for token in modified_tree:
            if token[8] == 'JJ':
                token[1] = 'tgt_' + token[9].lower() + ' tgt_' + token[9].lower()   
            elif token[8] == 'P':   
                token[1] = 'P_tgt_' + token[9].lower()
            elif token[8] == 'S':
                token[1] = 'S_tgt_' + token[9].lower() 
            elif token[8] == 'past':
                token[1] = 'tgt_' + token[9].lower() + '_-'
            elif token[8] == 'present':
                token[1] = 'tgt_' + token[9].lower()+ '_+'
            elif token[1] not in string.punctuation:
 #################################################################################################################################################
                token[1] = 'tgt_' + token[1].lower()               

        tgt_gold = " ".join([token[1] for token in modified_tree]) 
        total += 1

        if llm_answer:
            llm_answer = ' '.join(llm_answer.split())
            tgt_gold = ' '.join(tgt_gold.split())
            llm_answer = llm_answer.lower()


            no_period_gold = tgt_gold.rstrip('.').rstrip()
            no_period_llm = llm_answer.rstrip(' . ').rstrip()
        else:
            no_period_llm = ""

        if no_period_gold.lower() == no_period_llm.lower():
            correct += 1
        else:
            print("INCORRECT")

        
        if llm_answer:
            llm_result_sentence = ' '.join([word.replace('tgt_', '') if word.startswith('tgt_') else word for word in no_period_llm.split()])
        else:
            llm_result_sentence = ""

        gold_result_sentence = ' '.join([word.replace('tgt_', '') if word.startswith('tgt_') else word for word in no_period_gold.split()])


        print("llm_answer: ",no_period_llm)
        print(llm_result_sentence)
        # print("ENG: ",reversed_answer)
        print("tgt_gold  : ",no_period_gold)
        # print("ENG: ",reversed_gold)
        print(gold_result_sentence)
        bleu_score = sentence_bleu([gold_result_sentence], llm_result_sentence)
        print("bleu_score: ",bleu_score)
        reference_tokens = word_tokenize(gold_result_sentence)
        candidate_tokens = word_tokenize(llm_result_sentence)
        ms = round(meteor_score.single_meteor_score(reference_tokens, candidate_tokens),5)
        print("meteor_score: ",ms)
        print("\n")
        ms_total += ms

        reference_sentences.append([no_period_gold])
        candidate_sentences.append(no_period_llm)


    print(correct,"/",total)
    print("Accuracy: ", correct/total)
    print("Average meteor_score: ",round(ms_total/200, 5))

    bleu_score = corpus_bleu(reference_sentences, candidate_sentences)


    bleu1_score = corpus_bleu(reference_sentences, candidate_sentences, weights=(1, 0, 0, 0))
    bleu2_score = corpus_bleu(reference_sentences, candidate_sentences, weights=(0, 1, 0, 0))
    bleu3_score = corpus_bleu(reference_sentences, candidate_sentences, weights=(0, 0, 1, 0))
    bleu4_score = corpus_bleu(reference_sentences, candidate_sentences, weights=(0, 0, 0, 1))

    print("BLEU-1 Score:", round(bleu1_score, 5))
    print("BLEU-2 Score:", round(bleu2_score, 5))
    print("BLEU-3 Score:", round(bleu3_score, 5))
    print("BLEU-4 Score:", round(bleu4_score, 5))

    # Print the overall BLEU score
    print("Overall BLEU Score:", round(bleu_score, 5))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a JSON file.")
    parser.add_argument("input_file", help="The path to the input JSON file")
    args = parser.parse_args()

    main(args.input_file)
