# %%
# Import necessary libraries
import openai
import json
import os
import tiktoken
import time
import callgpt
import react_chain
import compliance_checker


def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(text))
    return num_tokens


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


os.environ["OPENAI_API_KEY"] = open_file('openai_api_key.txt')
openai.api_key = open_file('openai_api_key.txt')
openai_api_key = openai.api_key
callgpt = callgpt.Ask()


class BusinessAnalyst:
    def __init__(self):
        self.role_system = {
            "role": "system", "content": "You are a highly organised and detail oriented business analyst."}
        self.messages = [self.role_system]

    def chat_with_gpt3(self, prompt, max_retries=3, delay=2):
        user_message = {"role": "user", "content": prompt}
        new_message_tokens = count_tokens(prompt)
        total_tokens = sum(count_tokens(m["content"])
                           for m in self.messages) + new_message_tokens

        while total_tokens + 1 > 3500:
            # Remove the oldest user-assistant message pair to stay within the token limit
            self.messages.pop(1)
            self.messages.pop(1)
            total_tokens = sum(count_tokens(m["content"])
                               for m in self.messages) + new_message_tokens

        self.messages.append(user_message)

        # Retry logic
        retries = 0
        while retries < max_retries:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=self.messages,
                )
                assistant_message = {
                    "role": "assistant", "content": response.choices[0].message["content"]}
                self.messages.append(assistant_message)
                return assistant_message["content"]
            except openai.error.OpenAIError as e:
                print(f"Error occurred during API call: {e}")
                retries += 1
                if retries < max_retries:
                    time.sleep(delay)  # Delay between retries
                else:
                    raise  # Raise the exception if all retries have failed

    def process_input(self, user_query):
        prompt = f"You are an AI who wants to solve the following user query: '{user_query}' with a numbered list of tasks. Response: "
        processed_query = self.chat_with_gpt3(prompt)
        print("\033[92m\033[1m"+"\n*****Processed query:*****\n" +
              "\033[0m\033[0m"+processed_query)
        return processed_query

    # Not strictly speaking necessary, unless we want to do nested tasks
    def decompose_tasks(self, processed_query):
        prompt = f"You are an AI whose job is to decompose the following processed query into sub-tasks: '{processed_query}'. Response: "
        sub_tasks = self.chat_with_gpt3(prompt)
        print("\033[92m\033[1m"+"\n*****Subtasks*****\n" +
              "\033[0m\033[0m" + (sub_tasks))
        return sub_tasks

    def select_task(self, sub_tasks):
        prompt = f"Select the first task to analyse from the sub-tasks: '{sub_tasks}'. Response: "
        selected_task = self.chat_with_gpt3(prompt)
        print("\033[92m\033[1m"+"\n*****Selected Tasks:*****\n" +
              "\033[0m\033[0m" + (selected_task))
        return selected_task

    def execute_tasks(self, selected_task):
        results = []
        # for task in selected_task: --> for this to loop through all tasks
        prompt = f"You are an AI focused on executing the following task: '{selected_task}'. Response: "
        compliant_prompt = compliance_checker.check_compliance(prompt)
        # result = self.chat_with_gpt3(prompt)
        print("\033[92m\033[1m"+"\n*****Compliant Prompt*****\n" +
              "\033[0m\033[0m" + compliant_prompt)
        result = react_chain.query(compliant_prompt)
        # results.append(result)
        print("\033[92m\033[1m"+"\n*****Results Of Execution*****\n" +
              "\033[0m\033[0m" + result)
        return result

    def analyze_results(self, results):
        prompt = f"You are an AI focused on analysing the results from executing the task: '{results}'. Response: "
        analysis = self.chat_with_gpt3(prompt)
        print("\033[92m\033[1m"+"\n*****Analysis*****\n" +
              "\033[0m\033[0m" + (analysis))
        return analysis

    def refine_tasks(self, analysis):
        prompt = f"Considering the results, let's refine and create new list of tasks based on the following analysis: {analysis}. The response should be in a numbered list with one sentence each. Response: "
        new_tasks = self.chat_with_gpt3(prompt)
        print("\033[92m\033[1m"+"\n*****Refined new Tasks*****\n" +
              "\033[0m\033[0m" + (new_tasks))
        return new_tasks

    def generate_output(self, analysis):
        prompt = f"You are an analyst who will create a readable document from the whole discussion summarising it and clearly articulating key theories, ideas and actions to be done. Please generate a user-friendly output based on the following analysis: {analysis}. Response: "
        output = self.chat_with_gpt3(prompt)
        print("\033[92m\033[1m"+"\n*****Generated Output*****\n" +
              "\033[0m\033[0m" + (output))
        return output

    def run_analysis(self, user_query):
        processed_query = self.process_input(user_query)
        sub_tasks = self.decompose_tasks(processed_query)
        selected_tasks = self.select_task(sub_tasks)
        results = self.execute_tasks(selected_tasks)
        analysis = self.analyze_results(results)
        new_tasks = self.refine_tasks(analysis)
        while len(new_tasks) > 0:  # Loop!
            sub_tasks = self.execute_tasks(new_tasks)
            selected_tasks = self.select_task(sub_tasks)
            results = self.execute_tasks(selected_tasks)
            analysis = self.analyze_results(results)
            new_tasks = self.refine_tasks(analysis)
        output = self.generate_output(analysis)
        return output


user_query = "How can you create a company that can run itself with the help of an AI?"
ba = BusinessAnalyst()
result = ba.run_analysis(user_query)
print(result)
