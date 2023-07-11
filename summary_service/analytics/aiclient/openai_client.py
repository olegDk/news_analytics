import os
from typing import List
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get("OPEN_AI_API_KEY")


from tenacity import retry, wait_random_exponential, stop_after_attempt
from langchain import PromptTemplate
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI


def setup_langchain():
    chat_llm = ChatOpenAI(
        temperature=1,
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
    )

    question_prompt_template = """
                    Please provide a summary of the following text.
                    TEXT: {text}
                    SUMMARY:
                    """

    question_prompt = PromptTemplate(
        template=question_prompt_template, input_variables=["text"]
    )

    refine_prompt_template = """
                Write a concise summary of the following text delimited by triple backquotes.
                Return your response in bullet points which covers the key points of the text.
                ```{text}```
                BULLET POINT SUMMARY:
                """

    refine_prompt = PromptTemplate(
        template=refine_prompt_template, input_variables=["text"]
    )

    refine_chain = load_summarize_chain(
        chat_llm,
        chain_type="refine",
        question_prompt=question_prompt,
        refine_prompt=refine_prompt,
        return_intermediate_steps=True,
    )

    return refine_chain


refine_chain = setup_langchain()


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Embed texts using OpenAI's ada model.

    Args:
        texts: The list of texts to embed.

    Returns:
        A list of embeddings, each of which is a list of floats.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    # Call the OpenAI API to get the embeddings
    response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")

    # Extract the embedding data from the response
    data = response["data"]  # type: ignore

    # Return the embeddings as a list of lists of floats
    return [result["embedding"] for result in data]


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def get_chat_completion(
    messages,
    model="gpt-3.5-turbo",  # use "gpt-4" for better results
):
    """
    Generate a chat completion using OpenAI's chat completion API.

    Args:
        messages: The list of messages in the chat history.
        model: The name of the model to use for the completion. Default is gpt-3.5-turbo, which is a fast, cheap and versatile model. Use gpt-4 for higher quality but slower results.

    Returns:
        A string containing the chat completion.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    # call the OpenAI chat completion API with the given messages
    response = openai.ChatCompletion.create(
        model=model, messages=messages, temperature=0.0
    )

    choices = response["choices"]  # type: ignore
    completion = choices[0].message.content.strip()
    print(f"Completion: {completion}")
    return completion


def create_summary(news_text: str) -> str:
    doc1 = Document(page_content=news_text)
    docs = [doc1]

    refine_outputs = refine_chain({"input_documents": docs})
    return refine_outputs["output_text"]


def update_summary(existing_summary: str, new_news_text: str) -> str:
    doc1 = Document(page_content=existing_summary)
    doc2 = Document(page_content=new_news_text)
    docs = [doc1, doc2]

    refine_outputs = refine_chain({"input_documents": docs})
    return refine_outputs["output_text"]
