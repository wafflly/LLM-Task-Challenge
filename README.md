# Challenging LLMs with New Tasks

This repository is for our paper: Challenging Large Language Models with New Tasks: A Study on their Adaptability and Robustness. This repository contains the datasets for the six tasks; GPT-4 evaluation scripts for these tasks; and the evaluation results used in the paper.


1. The 'datasets' directory contains prompts for six tasks.

    - **Brief introduction of each task**:
        - **Task 1-2**: Arithmetic expressions with newly defined precedence. In these two tasks, we redefine the precedence of four elementary operators, and test if LLMs can work out the math problems with the new precedence.
        - **Task 3-4**: Machine translation with an artificial language. Task 3 involves translating English sentences into Language A using provided syntactic and morphological rules. Task 4 requires inferring the syntactic rules of Language A from given translation pairs.
        - **Task 5-6**: Basic deduction with a twist. Task 5 is adopted and modified from the basic deduction test in the bAbI dataset; Task 6 is designed to test models' understanding of four types of predicates.

    - **Naming of the files in the 'datasets' directory**:
        - **Task 1** files are in the format of `XXX_n_m_YYY.json`, where 'XXX' denotes the number of moves or how different the new precedence is from the standard one, 'n' the length of arithmetic expressions, 'm' the number of digits, 'YYY' prompt type. For instance, `two_3_1_cot1.json` is length three one-digit expressions (`2+3/4-9`) with two new defined precedence changes with chain of thought (CoT) instructions in the prompt.
        - **Task 2** files have similar naming to those in Task 1, 'cot', 'cot_p', and 'cot_f' denote simple, partial, and full CoT prompts.
        - **Task 3** Files are in the format of nSnM.json, where nS and nM denote the number of syntactic rules and morphology rules, respectively, under different directories. For instance, cot/3SSM.json indicates 3 syntactic rules and morphology rules.
        - **Task 4** Files are in the format of (n)ord_noise_XXX_2.json, where n denotes the number of grammatical orders and XXX specifies the grammar rule it focuses on. For example, 1ord_noise_SOV.json represents 1 grammatical order focused on SOV (Subject-Object-Verb).
        - For **Task 5**, `origin.json` is the original bAbI basic deduction prompts in the format of multiple choice. 'neg' and 'quant' denote adding 'not' and 'some' to the reasoning chain respectively. 'random' is when we replace the nouns in the prompts with random strings. 'derived' is when we extend the reasoning chain.
        - For **Task 6**, 'NTNS', 'TNS', 'NTS', and 'TS' refer to the four types of predicates detailed in our paper: non-transitive and non-symmetrical, transitive and non-symmetrical, non-transitive and symmetrical, and transitive and symmetrical.

2. **'results' directory**:.
    - The results were from our GPT-4 experiments done November 2023 - March 2024. After small scaled experiments on sampling strategy, we used the 'gpt-4-1106-preview' model with `top_p` set to 0 and `temperature` to 0.4.
    - Please note that GPT-4, by the date when the paper is accepted, was undeterministic. Thus, running the same experiments with the same setting might not achieve the same output as ours, though the results will not vary much.

3. **Evaluation script**:
    - The evaluation scripts are Python files that begin with 'eval'. T1-T6 stands for six tasks. For instance, `eval_T2.py` is the evaluation script for Task 2. Please note Task 1 has two evaluation scripts for length two and length three expressions respectively.
    - For Task 3, please use `eval_T3.sh` .
    - The OpenAI API key is in the `config.py` under 'src'. Please replace it with your own key when calling the evaluation scripts.

### Requirements
The `requirements.txt` file lists all necessary dependencies for running the evaluation scripts. You can install them using:
```bash
pip install -r requirements.txt

### How to Run

1. **Activate the virtual environment (if used)**:
    ```bash
    source venv/bin/activate
    ```

2. **Run the evaluation scripts** using the provided `run.sh` script:
    ```bash
    ./run.sh
    ```
