import os
import json
from typing import List, Optional
from analytics.aiclient.openai_client import get_chat_completion
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from dotenv import load_dotenv
import tiktoken


load_dotenv()


COMLETION_MODEL = "gpt-3.5-turbo"
SEPARATOR = "\n* "
MAX_SECTION_LEN = 2048
ENCODING = "gpt2"

INDEX_NAME = os.environ.get("PINECONE_INDEX")

embeddings = OpenAIEmbeddings()
encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))


def load_system_prompt() -> str:
    with open("analytics/system_prompt.txt", "r", encoding="utf-8") as file:
        content = file.read()

    return content


SYSTEM_PROMPT = load_system_prompt()


def query_to_json(query: str) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Respond in json only:\n{query}"},
    ]

    completion = get_chat_completion(messages=messages, model=COMLETION_MODEL)
    try:
        result_json = json.loads(completion)
    except json.decoder.JSONDecodeError:
        result_json = {"command": "/unknown"}

    return result_json


def semantic_search(text: Optional[str] = None) -> str:
    # 1. Query most similar documents
    # 2. Parse them into joined text
    # 3. Create prompt
    # 4. ChatGPT completion
    # 5. Return result.

    chosen_sections = []
    chosen_sections_len = 0

    docsearch = Pinecone.from_existing_index(
        index_name=INDEX_NAME, embedding=embeddings
    )

    docs = docsearch.similarity_search(text)

    for doc in docs:
        # Add contexts until run out of space.
        try:
            doc_content = doc.page_content
            chosen_sections_len += len(encoding.encode(doc_content)) + separator_len
            chosen_sections.append(SEPARATOR + doc_content)

            if chosen_sections_len > MAX_SECTION_LEN:
                break
        except:
            continue

    header = (
        f"Answer the question as truthfully as possible using the provided context, "
        + f"you are the author of the context, speak from yourself, "
        + f"provide responses as if you were the author of the original context, "
        + f"always refer to yourself and never to the author, and if the answer is not contained within the text below, say "
        + f"Content that I have access to doesn't contain the exact answer.\n\nContext:\n"
    )

    prompt = header + "".join(chosen_sections) + "\n\n Q: " + text + "\n A:"
    messages = [{"role": "user", "content": prompt}]

    answer = get_chat_completion(messages)

    return answer


command_to_processor = {
    "/text": semantic_search,
}


def process_query(query: str) -> str:
    parsed_query = query_to_json(query)
    command = parsed_query["command"]

    if command == "/unknown" or command not in command_to_processor.keys():
        return f"Sorry, I can not respond to this query with expected result for now."

    args = {key: value for key, value in parsed_query.items() if key != "command"}

    try:
        result = command_to_processor[command](**args)
        return result
    except Exception as e:
        print(e)
        return f"Sorry, I can not respond to this query with expected result for now."
