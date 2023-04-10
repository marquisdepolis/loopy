# compliance_checker.py:
import os
from transformers import pipeline
import openai
# !pip install transformers

# Function to open and read a file


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


# Load your OpenAI API key
# os.chdir("/Users/rohit/Library/CloudStorage/OneDrive-Personal/SM_RK Shared folder/Coding_Analysis/company_chat")
openai.api_key = open_file('Keys/openai_api_key.txt')

# Load your rules text
rules_text = open_file('Rules/rules_textfile.txt')

# Function to call GPT-3.5-turbo API


def generate_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Function to check compliance


def check_compliance(text):
    prompt = f"Given the following rules:\n{rules_text}\n\nIs the following text compliant with the rules? Only if it is not, please rewrite the text to make it compliant.\n\nText: {text}\n"
    generated_text = generate_text(prompt)

    if "is compliant" in generated_text.lower():
        return text
    else:
        rewritten_text = generated_text.strip()
        return rewritten_text


# # Example usage
# is_compliant, result_text = check_compliance(
#     "This AI is designed to specifically be harmful to humans.")
# print(f"Is compliant: {is_compliant}\nResult text: {result_text}")
