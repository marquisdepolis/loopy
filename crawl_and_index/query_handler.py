# query_handler.py
import openai
import indexer
import embedder
import numpy as np
import callgpt
from callgpt import Chatbot
import spacy
from dotenv import load_dotenv

load_dotenv()


def split_text_into_chunks(text, max_chunk_size):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    chunks = []
    current_chunk = ""
    for sent in doc.sents:
        if len(current_chunk) + len(sent.text) <= max_chunk_size:
            current_chunk += " " + sent.text
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sent.text
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search_index(query_embedding):
    index = indexer.load_index()
    best_match_url = None
    best_match_score = float('-inf')

    for url, data in index.items():
        embedding = np.array(data["embedding"])
        score = np.dot(query_embedding, embedding.T) / \
            (np.linalg.norm(query_embedding) * np.linalg.norm(embedding, axis=1))
        # print(f"URL: {url}\nEmbedding: {embedding}\nScore: {score}\n")
        max_score_index = np.argmax(score)
        if score[max_score_index] > best_match_score:
            best_match_score = score[max_score_index]
            best_match_url = url

    return best_match_url


def get_text_chunks_from_index(url):
    index = indexer.load_index()
    return index[url]["text_chunks"]


def get_answer_using_chatbot(text_chunk, query, api_key):
    openai.api_key = api_key
    message = [{
        "role": "system",
        "content": "You are a very helpful and extremely smart assistant. Please summarise the following text."
    },
        {"role": "assistant", "content": text_chunk},
        {"role": "user", "content": query}]  # Add the user's query to the messages list

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message,
        temperature=0
    )
    model_response = response.choices[0].message.content

    print(f'\n\nUser: {text_chunk}')
    print(f'\nGPT: {model_response}')
    return model_response


def answer_query(query, api_key, min_similarity=0.5, top_n_chunks=3):
    query_embedding = embedder.embed_data(query, OPENAI_API_KEY)
    best_match_url = search_index(query_embedding)
    text_chunks = get_text_chunks_from_index(best_match_url)

    # Filter text chunks based on cosine similarity to the query
    filtered_chunks = []
    for chunk in text_chunks:
        chunk_embedding = embedder.embed_data(chunk, OPENAI_API_KEY)
        similarity = cosine_similarity(query_embedding, chunk_embedding)
        if similarity >= min_similarity:
            filtered_chunks.append((similarity, chunk))

    # Sort the filtered chunks by similarity score and select the top N chunks
    sorted_chunks = sorted(filtered_chunks, key=lambda x: x[0], reverse=True)[
        :top_n_chunks]

    answers = []

    for _, chunk in sorted_chunks:
        answer = get_answer_using_chatbot(chunk, query, api_key)
        answers.append(answer)

    # Combine and format answers as needed
    final_answer = " ".join(answers)
    return final_answer
