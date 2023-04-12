# %%
from bs4 import BeautifulSoup
from tkinter import filedialog
import tkinter as tk
import os
import requests
import openai
import callgpt
# from googlesearch import search

# %%

# class Gsearch:


def ask_gpt(your_question):
    with open("Keys/openai_api_key.txt", "r") as f:
        openai.api_key = f.read().strip()

    query1 = []
    google_it = f"What are the key terms you can extract from this query that, if searched, will help find the answers to {your_question}"
    model1 = "text-davinci-003"
    params1 = {
        "prompt": google_it,
        "temperature": 0.5,
        "max_tokens": 100,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    query1 = openai.Completion.create(engine=model1, **params1)
    # print(query1.choices[0].text.strip())
    google_it = f"Return exactly one Google search query, phrased as a question, I could Google to find information regarding {your_question}"
    model1 = "text-davinci-003"
    params1 = {
        "prompt": google_it,
        "temperature": 0.5,
        "max_tokens": 100,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    query2 = openai.Completion.create(engine=model1, **params1)
    query2

    return query1, query2

# %%


def clean_query(query1, query2):
    query = query2.choices[0].text.strip()
    return query

# %%


def iterate_google(query):
    # Iterate over the search results and append each URL to the list
    # programmatically search Google
    import requests
    import sys
    import os

    def open_file(filepath):
        with open(filepath, 'r', encoding='utf-8') as infile:
            return infile.read()

    # directory = filedialog.askdirectory(
    #     "Choose the folder with Google API files")
    # os.chdir(directory)

    # API KEY from: https://developers.google.com/custom-search/v1/overview
    API_KEY = open_file('Keys/google_api_key.txt')
    # get your Search Engine ID on your CSE control panel
    SEARCH_ENGINE_ID = open_file('Keys/google_searchengine_id.txt')
    # print(API_KEY)
    # print(SEARCH_ENGINE_ID)
    try:
        page = int(sys.argv[2])
        # make sure page is positive
        assert page > 0
    except:
        print("Page number isn't specified, defaulting to 1")
        page = 1
    # constructing the URL
    # doc: https://developers.google.com/custom-search/v1/using_rest
    # calculating start, (page=2) => (start=11), (page=3) => (start=21)
    # for some reason it's best to copy paste the query here
    # query = "{query}"
    print(query)
    start = (page - 1) * 10 + 1
    url = f"https://www.googleapis.com/customsearch/v1?cx={SEARCH_ENGINE_ID}&key={API_KEY}&q={query}&start={start}"
    #    print(url)
    # make the API request
    response = requests.get(url)
    # print("Status code:", response.status_code)
    # print("Response content:", response.text)
    data = response.json()
    # get the result items
    search_items = data.get("items")
    # print(search_items)
    if search_items is None:
        print("No search results found")
        exit()
    # iterate over 10 results found
    links = []
    for i, search_item in enumerate(search_items, start=1):
        try:
            long_description = search_item["pagemap"]["metatags"][0]["og:description"]
        except KeyError:
            long_description = "N/A"
        # get the page title
        title = search_item.get("title")
        # page snippet
        snippet = search_item.get("snippet")
        # alternatively, you can get the HTML snippet (bolded keywords)
        html_snippet = search_item.get("htmlSnippet")
        # extract the page url
        link = search_item.get("link")
        links.append(link)
        # print the results
        # print("="*10, f"Result #{i+start-1}", "="*10)
        # print("Title:", title)
        # print("Description:", snippet)
        # print("Long description:", long_description)
        # print("URL:", link, "\n")
    return links

# %%


def scrape_results(links):
    import openai
    from bs4 import BeautifulSoup
    with open("Keys/openai_api_key.txt", "r") as f:
        openai.api_key = f.read().strip()

    # Cycle through the urls to get the summarised answer
    answer = []
    num_results = 3

    for x in range(num_results):
        # Get the page content
        html = requests.get(links[x]).text
        # Extract the page title and text
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string
        text = "\n".join([p.text for p in soup.find_all("p")])

        # Set up the GPT-3 API request
        request = f"Please summarize the following article:\nTitle: {title}\n\n{text[:3000]}"
        model = "text-davinci-003"
        params = {
            "prompt": request,
            "temperature": 0.5,
            "max_tokens": 100,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        # Call the GPT-3 API and print the response
        response = openai.Completion.create(engine=model, **params)
        summary = response.choices[0].text.strip()
        answer.append(summary)
    return answer

# %%
# Clean the output
# Define function to clean text using GPT-3 API


def clean_text(t):
    # Define parameters for GPT-3 API
    max_tokens = 2000
    temperature = 0.7
    stop = "\n\n"
    # Split text into smaller chunks and process each chunk separately
    chunk_size = 2000
    chunks = [t[i:i+chunk_size] for i in range(0, len(t), chunk_size)]
    cleaned_chunks = []
    for chunk in chunks:
        # Generate cleaned text using GPT-3 API
        # Define prompt for GPT-3 API
        prompt = (f"Please clean up the following text:\n\n{chunk}\n\n"
                  "The cleaned text is:")
        print(prompt)
        cleaned_chunk = callgpt.gptclean(prompt)
        cleaned_chunks.append(cleaned_chunk)

    # Join cleaned chunks into a single string and return it
    cleaned_text = "".join(cleaned_chunks)
    return cleaned_text.strip()


# %%
# Ask the questions
# query = input("Input what you are curious about: ")
def execute(query):
    q1, q2 = ask_gpt(query)
    query_clean = clean_query(q1, q2)
    query_clean = query_clean.replace('"', '')
    query_clean = query_clean.replace("'", '')
    google_links = iterate_google(query_clean)
    text_scraped = scrape_results(google_links)
    # Convert to a string
    text_string = ' '.join(text_scraped)
    cleaned_text = clean_text(text_string)
    return cleaned_text


# execute("What's the best 10 day itinerary I can make for me and my family, including two children, to Iceland, if we love animals?")
