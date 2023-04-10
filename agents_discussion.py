# %%
import json
from enum import Enum
import os
import openai
import time
from dotenv import load_dotenv
load_dotenv()

OPENAI_CHAT_MODEL = "gpt-3.5-turbo"


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


os.environ["OPENAI_API_KEY"] = open_file('Keys/openai_api_key.txt')
openai.api_key = open_file('Keys/openai_api_key.txt')
openai_api_key = openai.api_key

SYSTEM_INSTRUCTION_TEMPLATE = "You are an extremely bright Stanford graduate and my real-time assistant in a discussion I'm having."
USER_INSTRUCTION_TEMPLATE = "My name is $NAME and I am a $ROLE. I work with $PARTNER. Our shared is to $GOAL. My private goal is $PRIVATE_GOAL."


def save_ideas(ideas, filepath):
    with open(filepath, "w") as outfile:
        json.dump(ideas, outfile)


def load_ideas(filepath):
    try:
        with open(filepath, "r") as infile:
            return json.load(infile)
    except FileNotFoundError:
        return []


class Agent:
    def __init__(self, name: str, role: str, goal: str, private_goal: str, style: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.private_goal = private_goal
        self.style = style  # Personality add
        self.partner_message = None
        self.memory = None
        self.partner = None
        self.task_list = []
        self.ideas = []

    def __str__(self):
        return self.name

    def set_partner(self, partner):
        self.partner = partner

    def initialize(self):
        self.ideas = load_ideas(f"{self.name}_ideas.json")
        system_instruction = SYSTEM_INSTRUCTION_TEMPLATE
        user_instruction = USER_INSTRUCTION_TEMPLATE.replace("$NAME", self.name).replace("$ROLE", self.role).replace(
            "$GOAL", self.goal).replace("$PRIVATE_GOAL", self.private_goal).replace("$PARTNER", self.partner.name)
        self.memory = [{"role": "system", "content": system_instruction}, {"role": "user", "content": user_instruction}, {
            "role": "user", "content": f"Here's my personality': {self.style}"}]

    def __repr__(self):
        return f"{self.name} ({self.description})"

    def create_task_list(self, query):
        instructions = f"Create a task list to solve the following query: '{query}'."
        self.memory.append({"role": "user", "content": instructions})
        return instructions

    def choose_task(self):
        if not self.task_list:
            return f"I need a list of tasks before I can choose one."

        task_list_string = "\n".join(self.task_list)
        instructions = f"From the following task list, rewrite and rearrange it to be better able to solve the goal '{self.goal}':\n{task_list_string}"
        self.memory.append({"role": "user", "content": instructions})

        completion = openai.ChatCompletion.create(
            model=OPENAI_CHAT_MODEL,
            messages=self.memory,
            max_tokens=500,
        )

        choice = completion['choices'][0]
        message = choice['message']['content']

        return message

    # Let's have some memories for these bots!
    def evaluate_and_save_idea(self, idea):
        # Define your evaluation function here, for example:
        # Cosplaying a garrulous interlocutor who likes the longest ideas best
        evaluation = len(idea)
        if len(self.ideas) < 5 or evaluation > min([i["evaluation"] for i in self.ideas]):
            self.ideas.append({"content": idea, "evaluation": evaluation})
            self.ideas = sorted(
                self.ideas, key=lambda x: x["evaluation"], reverse=True)[:5]
            save_ideas(self.ideas, f"{self.name}_ideas.json")


def generate_output(goal: str):
    agent1 = Agent("A_GPT-6", "Large Language Model", goal, "I will create a perfect list to figure out how to accomplish this goal",
                   "I am extremely creative and able to figure out how to cleverly solve the hardest problems. I only speak in numbered lists.")
    agent2 = Agent("B_GPT-6", "Large Language Model", goal, "I will critique the list given, and modify it to be even better using my superior intellect and logic.",
                   "I am highly analytical, precise and very logical. I only speak in numbered lists.")

    agent1.set_partner(agent2)
    agent2.set_partner(agent1)

    agent1.initialize()
    agent2.initialize()

    # print(agent1.memory)
    # print(agent2.memory)

    talker = agent1
    listener = agent2
    create_task_list_instructions = talker.create_task_list(goal)

    # def _dump_memory(agent: Agent):
    #     for i, msg in enumerate(agent.memory):
    #         print(f"  {i:2d} {msg['role']:6s} {msg['content']}")

    current_round = 0
    MAX_ROUNDS = 4
    while current_round < MAX_ROUNDS:
        completion = openai.ChatCompletion.create(
            model=OPENAI_CHAT_MODEL,
            messages=talker.memory,
            max_tokens=500,
        )
        current_round += 1

        choice = completion['choices'][0]
        finish_reason = choice['finish_reason']
        if finish_reason != "stop" and finish_reason is not None:
            print(f"Finish reason: {finish_reason}")
            break
        message = choice['message']['content']
        print(f"\n{talker.name}")
        print(f"{message}")
        print()
        talker.memory.append({"role": "assistant", "content": message})

        message = choice['message']['content']
        talker.evaluate_and_save_idea(message)

        listener.partner_message = message

        if talker == agent1:
            task_string = message.strip().split("\n")  # Split the message into lines
            # Strip extra spaces and add tasks to agent2's task_list
            agent2.task_list = [t.strip() for t in task_string]
            # Update agent2's memory with the task list
            agent2.memory.append(
                {"role": "assistant", "content": f"I need to find the action to take from: {talker.partner_message}"})
        elif talker == agent2:
            agent1.memory.append(
                {"role": "user", "content": f"From this description what should my steps be: '{chosen_task}'."})

        talker, listener = listener, talker
        if talker == agent2:
            chosen_task = agent2.choose_task()

        # time.sleep(2)

    return chosen_task
