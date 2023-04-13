# %%
import os
import openai
from dotenv import load_dotenv
load_dotenv()

OPENAI_CHAT_MODEL = "gpt-3.5-turbo"


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


os.environ["OPENAI_API_KEY"] = open_file('Keys/openai_api_key.txt')
openai.api_key = open_file('Keys/openai_api_key.txt')
openai_api_key = openai.api_key

SYSTEM_INSTRUCTION_TEMPLATE = "You are an expert in my field and you are my real-time assistant in an effort to draft a joint document that we can all agree on."
USER_INSTRUCTION_TEMPLATE = "My name is $NAME and I am a $ROLE. Our shared is to $GOAL. My private goal is $PRIVATE_GOAL. I usually communicate in $STYLE."


class Agent:
    def __init__(self, name: str, role: str, goal: str, private_goal: str, beliefs: str, style: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.private_goal = private_goal
        self.beliefs = beliefs
        self.style = style
        self.memory = None

    def __str__(self):
        return self.name

    def initialize(self):
        system_instruction = SYSTEM_INSTRUCTION_TEMPLATE
        user_instruction = USER_INSTRUCTION_TEMPLATE.replace("$NAME", self.name).replace("$ROLE", self.role).replace(
            "$GOAL", self.goal).replace("$PRIVATE_GOAL", self.private_goal).replace("$STYLE", self.style)
        self.memory = [{"role": "system", "content": system_instruction}, {"role": "user", "content": user_instruction}, {
            "role": "user", "content": f"Here are my strongly held views: {self.beliefs}"}]

    def set_current_proposal(self, current_proposal):
        self.initialize()
        self.memory.append(
            {"role": "user", "content": f"Here is the current proposal: {current_proposal}"})

    def __repr__(self):
        return f"{self.name} ({self.role}, {self.goal})"

    def make_drafter(self, participants):
        self.role = "drafter"
        self.participants = participants

    def make_participant(self, drafter):
        self.role = "participant"
        self.drafter = drafter

    def provide_feedback(self, agent, feedback):
        self.memory.append(
            {"role": "user", "content": f"{agent.name} said: {feedback}"})


def _dump_memory(agent: Agent):
    print(f"=== MEMORY {agent.name} ===")
    for i, msg in enumerate(agent.memory):
        print(f"  {i:2d} {msg['role']:6s} {msg['content']}")


def extract_completion(completion):
    return completion['choices'][0]['message']['content']


def make_willingness_to_sign_dict(completion_text: str):
    split_text = completion_text.split("Willingness to Sign: ")
    if len(split_text) >= 2:
        score_str = split_text[1][:3]
    else:
        score_str = "0"
    try:
        score = float(score_str.strip())
    except ValueError:
        score = 0
    return {"score": score, "feedback": completion_text}


def create_joint_letter(goal: str):
    drafter = Agent("Max Tegmark", "President of Future of Life Institute", goal, "I want to be a brilliant philosopher",
                    "I need to be specific in my thoughts and logical.", "I am a philosopher.")
    participants = [Agent("Tyler Cowen", "Economist", goal, "I want to be a brilliant economist", "It is critical to have a holistic and humanistic view into topics to get to the truth.", "I usually allude to historical events and figures, am pithy and Straussian in my communiques. I speak in brief sentences."),
                    Agent("Scott Alexander", "Writer", goal, "I want to get to the truth regardless of anything.", "The way to get to truth is by focusing on facts and rationalism",
                          "I am an empiricist. I am quite funny and draw interesting parallels between distinct fields. I am a rationalist."),
                    Agent("Peter Thiel", "Investor", goal, "I want to invest in world changing ideas.", "Girardian memetics rule most people's thoughts", "I speak in dichotomies often, in dialectic, I am a Girardian, and I like making grand theories.")]

    drafter.make_drafter(participants)
    for participant in participants:
        participant.make_participant(drafter)

    drafter.initialize()
    for participant in participants:
        participant.initialize()

    drafter.memory.extend([{"role": "user", "content": "Write an initial formal proposal that is meant to be signed by all parcipants. Just include the proposal, no greeting or closing. Use bullet points. Be aggressive in representing my strongly-held views. Use my vast knowledge wisdom of my intellectual tradition. Use formal language. Don't expose my private goal."}])
    completion = openai.ChatCompletion.create(
        model=OPENAI_CHAT_MODEL,
        messages=drafter.memory,
        max_tokens=500,
    )
    current_proposal = extract_completion(completion)
    drafter.set_current_proposal(current_proposal)

    current_round = 0
    MAX_ROUNDS = 3

    PARTICIPANT_INSTRUCTION = "Write a short para or bullet points of feedback to the current proposal from my perspective. Then Rate the current proposal on a 'Willingness to Sign' scale of 1-10 of  (1=definitely no, 10=definitely yes). Be aggressive in representing my strongly-held views. Use my vast knowledge wisdom of my intellectual tradition. Use some metaphors. No greeting or closing or preamble."

    participant_responses = []

    print(f"# Negotiation")
    while current_round < MAX_ROUNDS:
        print(f"## Round {current_round}")
        print(f"### Current proposal:\n{current_proposal}")

        current_round += 1

        for participant in participants:
            participant.set_current_proposal(current_proposal)
            participant.memory.extend(
                [{"role": "user", "content": PARTICIPANT_INSTRUCTION}])
            completion = openai.ChatCompletion.create(
                model=OPENAI_CHAT_MODEL,
                messages=participant.memory,
                max_tokens=150,
            )
            completion_text = extract_completion(completion)
            print(f"### {participant.name}'s response\n{completion_text}\n\n")
            participant_responses.append(
                make_willingness_to_sign_dict(completion_text))
            drafter.provide_feedback(participant, completion_text)

        drafter.memory.extend(
            [{"role": "user", "content": "Take the feedback and synthesize a new draft proposal that increases average Willingness To Sign amongst all participants."}])
        completion = openai.ChatCompletion.create(
            model=OPENAI_CHAT_MODEL,
            messages=drafter.memory,
            max_tokens=500,
        )
        current_proposal = extract_completion(completion)

    print(f"# Final proposal")
    print(current_proposal)

    # Filter signatories based on willingness to sign score
    signers = [drafter] + [p for p,
                           resp in zip(participants, participant_responses) if resp["score"] >= 5]

    signer_names = ', '.join([signer.name for signer in signers])

    # signers = drafter.name
    # for participant in participants:
    #     signers += f", {participant.name}"

    completion = openai.ChatCompletion.create(
        model=OPENAI_CHAT_MODEL,
        messages=[{"role": "system", "content": "You are an expert drafter of constitutions and manifestos"},
                  {"role": "user", "content": f"The final proposal is: \n===\n{current_proposal}\n===\n"},
                  {"role": "user", "content": f"The signers are: {signers}"},
                  {"role": "user", "content": f"Write a joint letter with a beautiful premable saying that the undersigned all agree to this proposal. Include the final proposal verbatim. Sign the letters by the signers: {current_proposal}"}],
        max_tokens=1000,
    )
    final_letter = extract_completion(completion)
    return final_letter
