# embedder.py
import openai
import json
import spacy

nlp = spacy.load("en_core_web_md")

def embed_data(text, api_key):
    doc = nlp(text)
    return doc.vector
    openai.api_key = api_key
    try:
        response = openai.Embedding.create(
            engine="text-embedding-ada-002",
            input=text
    #        max_tokens=50,
    #        n=1,
    #        stop=None,
    #        temperature=0.5,
        )
        embedding_text = response['data'][0]['embedding']
        embedding = json.loads(embedding_text)
        return embedding
    except openai.error.RateLimitError as e:
        print(f"API call failed with rate limit error: {e}. Retrying after {delay} seconds...")
        time.sleep(delay)
        delay *= backoff_factor
