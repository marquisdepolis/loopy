# %%
# %%
import re
import httpx
import os
import openai
import gsearch
import slcindex
import callgpt


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


os.environ["OPENAI_API_KEY"] = open_file('openai_api_key.txt')
openai.api_key = open_file('openai_api_key.txt')
openai_api_key = openai.api_key


class ChatBot:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        # chat = callgpt.Chat()
        # completion = chat.gpt_creative(self.messages)
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages)
        # Uncomment this to print out token usage each time, e.g.
        # {"completion_tokens": 86, "prompt_tokens": 26, "total_tokens": 112}
        print(completion)
        # return completion
        return completion.choices[0].message.content


prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

goog:
e.g. search for queries
If you don't know the answer to a query, searches Google via the function, which returns a summary of the results it found

wikipedia:
e.g. wikipedia: England
Returns a summary from searching Wikipedia

slc_search:
e.g. slc_search: Django
Search what Rohit wrote on Strange Loop Canon for "Django"

Always look things up on Wikipedia if you have the opportunity to do so.

Example session:
Question: What is the capital of France?
Thought: I should look up France on Wikipedia
Action: wikipedia: France
PAUSE

You will be called again with this:

Observation: France is a country. The capital is Paris.

You then output:

Answer: The capital of France is Paris

Example session:
Question: Where are the best pizza places in London?
Thought: I should look up pizza places in London
Action: goog: top pizza places
PAUSE

You will be called again with this:

Observation: In 2023, the best pizza places in London include Fatto a Mano in King's Cross, Flat Earth in Bethnal Green, and Happy Face in King's Cross. Fatto a Mano offers locally sourced Neapolitan-style pizzas.

You then output:

Answer: The best pizza in London is Fatto o Mano in Kings Cross
""".strip()


action_re = re.compile('^Action: (\w+): (.*)$')


def query(question, max_turns=5):
    i = 0
    bot = ChatBot(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [action_re.match(a) for a in result.split(
            '\n') if action_re.match(a)]
        if actions:
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception(
                    "Unknown action: {}: {}".format(action, action_input))
            print(" -- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return


def wikipedia(q):
    return httpx.get("https://en.wikipedia.org/w/api.php", params={
        "action": "query",
        "list": "search",
        "srsearch": q,
        "format": "json"
    }).json()["query"]["search"][0]["snippet"]


def slc_search(q):
    results = slcindex.inputquery(q)
    return results  # This line is just an example, you need to parse the actual results


def goog(q):
    gsearch.execute(q)


def calculate(what):
    return eval(what)


known_actions = {
    "wikipedia": wikipedia,
    "goog": goog,
    "calculate": calculate,
    "slc_search": slc_search
}


ques = input("What do you want to know?")
query(ques)
