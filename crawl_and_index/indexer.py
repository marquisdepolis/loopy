# indexer.py
import json
import os

# Add these lines
current_directory = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(current_directory, "index.json")


def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as f:
            index = json.load(f)
    else:
        index = {}
    return index


def update_index(url, embedding, text_chunk):
    index = load_index()
    if url not in index:
        index[url] = {
            "embedding": [embedding],  # Wrap the embedding in a list
            "text_chunks": [text_chunk]
        }
    else:
        index[url]["text_chunks"].append(text_chunk)
        index[url]["embedding"].append(embedding)  # Append the new embedding

    with open(INDEX_FILE, "w") as f:
        json.dump(index, f)
