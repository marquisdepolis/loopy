# indexer.py
import json
import os

INDEX_FILE = "index.json"

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
            "embedding": embedding.tolist(),
            "text_chunks": [text_chunk]
        }
    else:
        index[url]["text_chunks"].append(text_chunk)
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f)
