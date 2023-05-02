# %%
import openai
import os
from time import time, sleep
import textwrap
import re
import os

if not os.path.exists('gpt3_logs'):
    os.makedirs('gpt3_logs')


def open_file(filepath):
    with open(filepath, 'r', encoding='latin-1') as infile:
        return infile.read()


openai.api_key = open_file('openaiapikey.txt')


def save_file(content, filepath):
    with open(filepath, 'w', encoding='latin-1') as outfile:
        outfile.write(content)


def gpt3_completion(prompt, engine='gpt-3.5-turbo', temp=0.6, top_p=1.0, tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    message = prompt.encode(encoding='ASCII', errors='ignore').decode()
    prompt = [{"role": "system", "content": "Summarise and extract key insights"}, {
        "role": "user", "content": message}]
    text = ''
    while True:
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=prompt,
                temperature=temp
            )
            text = response.choices[0].message["content"].strip()
            text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            prompt_str = '\n'.join(
                [f"{item['role']}: {item['content']}" for item in prompt])
            with open('gpt3_logs/%s' % filename, 'a') as outfile:
                outfile.write('PROMPT:\n\n' + prompt_str +
                              '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def recursive_summary(input_text):
    version = 0
    alltext = input_text
    filename = f"output_v{version}.txt"
    save_file('\n\n'.join(alltext), filename)
    len(alltext)

    while len(alltext) > 500:
        inputfile = f"output_v{version}.txt"
        summarytext = open_file(inputfile)
        chunks = textwrap.wrap(summarytext, 2000)
        result = list()
        count = 0
        for chunk in chunks:
            count = count + 1
            prompt = open_file('prompt.txt').replace('<<SUMMARY>>', chunk)
            prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
            summary = gpt3_completion(prompt)
            print('\n\n\n', count, 'of', len(chunks), ' - ', summary)
            result.append(summary)
        version = version + 1
        filename = f"output_v{version}.txt"
        save_file('\n\n'.join(result), filename)
        alltext = open_file(filename)
    return alltext
