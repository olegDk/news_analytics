import os
import json
from typing import Optional, Dict, Any
from analytics.aiclient.openai_client import get_chat_completion
from analytics.fred_utils import (
    calculate_yield_metrics,
    get_effective_ffr_data,
    get_target_ffr_data,
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from models.models import DocumentMetadataFilter
from analytics.date import to_unix_timestamp
from dotenv import load_dotenv
import tiktoken
import logging


LOG_FILENAME = "analytics_client.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)


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


def semantic_search(
    text: Optional[str] = None,
    assets: Optional[list] = None,
    dates: Optional[str] = None,
) -> Dict:
    # 1. Query most similar documents
    # 2. Parse them into joined text
    # 3. Create prompt
    # 4. ChatGPT completion
    # 5. Return result.

    chosen_sections = []
    chosen_sections_len = 0
    source_ids = set()

    docsearch = Pinecone.from_existing_index(
        index_name=INDEX_NAME, embedding=embeddings
    )
    try:
        metadata_filter = DocumentMetadataFilter(assets=assets, dates=dates)
        pinecone_filter = get_pinecone_filter(filter=metadata_filter)
        logging.info(f"Created filter: {pinecone_filter}")

        docs = docsearch.similarity_search(text, filter=pinecone_filter)
        logging.info(f"Docs: {docs}")

        for doc in docs:
            try:
                source_ids.add(doc.metadata["source_id"])
            except:
                continue

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
            + f"provide responses as if you were the author of the original context. "
            + f"If context is not empty - you must provide an answer from that context, you cannot say that you don't know. "
            + f"Always refer to yourself and never to the author.\n\nContext:\n"
        )

        prompt = header + "".join(chosen_sections) + "\n\n Q: " + text + "\n A:"
        logging.info(f"Prompt: {prompt}")
        messages = [{"role": "user", "content": prompt}]

        answer = get_chat_completion(messages)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

    return {"reply": answer, "source_ids": list(source_ids), "type": "semantic_search"}


def yield_metrics(
    asset_casual: Optional[str] = None,
    starting: Optional[str] = None,
    ending: Optional[str] = None,
):
    answer = calculate_yield_metrics(asset_casual, starting, ending)
    return {
        "reply": answer,
        "source_ids": ["https://fred.stlouisfed.org/"],
        "type": "yield_metrics",
    }


def effective_ffr_data():
    answer = get_effective_ffr_data()
    return {
        "reply": answer,
        "source_ids": ["https://fred.stlouisfed.org/"],
        "type": "effective_ffr_data",
    }


def target_ffr_data():
    answer = get_target_ffr_data()
    return {
        "reply": answer,
        "source_ids": ["https://fred.stlouisfed.org/"],
        "type": "target_ffr_data",
    }


command_to_processor = {
    "/text": semantic_search,
    "/yield_metrics": yield_metrics,
    "/effective_ffr_rate": effective_ffr_data,
    "/target_ffr_rate": target_ffr_data,
}


def process_query(query: str) -> Dict:
    parsed_query = query_to_json(query)
    command = parsed_query["command"]

    if command == "/unknown" or command not in command_to_processor.keys():
        return {
            "reply": {
                "reply": "Sorry, I can not respond to this query with expected result for now.",
                "sources": [],
                "type": "",
            }
        }

    args = {key: value for key, value in parsed_query.items() if key != "command"}
    return command_to_processor[command](**args)


def get_pinecone_filter(
    filter: Optional[DocumentMetadataFilter] = None,
) -> Dict[str, Any]:
    if filter is None:
        return {}

    pinecone_filter = []

    # Check if assets are provided and add the corresponding pinecone filter expression
    if filter.assets:
        # Create an $or condition for each asset
        assets_conditions = [{"assets": asset} for asset in filter.assets]
        pinecone_filter.append({"$or": assets_conditions})

    # Check if dates are provided and add the corresponding pinecone filter expression
    if filter.dates:
        pinecone_filter.append({"date": {"$in": filter.dates}})

    # Combine all conditions using $and
    return {"$and": pinecone_filter}
