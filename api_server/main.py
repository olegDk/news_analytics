from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, Depends, Body, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from models.api import (
    DeleteSemanticRequest,
    DeleteSemanticResponse,
    Query,
    QueryResponse,
    QuerySemanticRequest,
    QuerySemanticResponse,
    UpsertSemanticRequest,
    UpsertSemanticResponse,
    ResponseType,
    News,
    Summary,
    NewsRequest,
    NewsResponse,
    SummaryRequest,
    SummaryResponse,
)
from db_clients.vector_datastore_client.factory import get_datastore
from db_clients.postgres_client.postgres_client import PostgresClient
from analytics.file import get_document_from_file
from analytics.analytics_client import process_query
from datetime import date

from models.models import DocumentMetadata, Source
import logging


LOG_FILENAME = "analytics_client.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

pg_client = PostgresClient()


@app.post(
    "/upsert-file-semantic",
    response_model=UpsertSemanticResponse,
)
async def upsert_file_semantic(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
):
    try:
        metadata_obj = (
            DocumentMetadata.parse_raw(metadata)
            if metadata
            else DocumentMetadata(source=Source.file)
        )
    except:
        metadata_obj = DocumentMetadata(source=Source.file)

    document = await get_document_from_file(file, metadata_obj)

    try:
        ids = await datastore.upsert([document])
        return UpsertSemanticResponse(ids=ids)
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=f"str({e})")


@app.post(
    "/upsert-semantic",
    response_model=UpsertSemanticResponse,
)
async def upsert_semantic(
    request: UpsertSemanticRequest = Body(...),
):
    try:
        ids = await datastore.upsert(request.documents)
        return UpsertSemanticResponse(ids=ids)
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error")


@app.post("/query", response_model=QueryResponse)
async def query(request: Query = Body(...)):
    try:
        response_data = process_query(request.query_text)
        print(response_data)

        # Reshape the response_data to fit the model
        reply_data = {"reply": response_data.get("reply"), "sources": []}

        if response_data.get("type", "") == "semantic_search":
            source_ids_int = [int(sid) for sid in response_data["source_ids"]]
            news_details = await pg_client.get_news_details_by_source_ids(
                source_ids_int
            )
            reply_data["sources"] = news_details
            reply_data["type"] = response_data["type"]
        else:
            # Just ensure that 'sources' is an empty list if not semantic_search
            reply_data["sources"] = response_data["source_ids"]
            reply_data["type"] = response_data["type"]

        # Wrap the reshaped reply data in another dictionary for the QueryResponse model
        reshaped_response = {"reply": reply_data}
        logging.info(
            f"Reply data keys: {reshaped_response.keys()}, inside reply data keys: {reshaped_response['reply'].keys()}"
        )

        return reshaped_response
    except Exception as e:
        print("Error:", e)
        # raise HTTPException(status_code=500, detail="Internal Service Error")
        # INFO:root:Reply data keys: dict_keys(['reply']), inside reply data keys: dict_keys(['reply', 'sources', 'type'])

        reply_data = {
            "reply": {
                "reply": "Unfortunatelly, I cannot answer this question at the moment, but I will improve",
                "sources": ["unknown"],
                "type": "unknown",
            },
        }
        logging.info(
            f"Reply data keys: {reply_data.keys()}, inside reply data keys: {reply_data['reply'].keys()}"
        )
        return reply_data


@app.post(
    "/query-semantic",
    response_model=QuerySemanticResponse,
)
async def query_main(
    request: QuerySemanticRequest = Body(...),
):
    try:
        results = await datastore.query(
            request.queries,
        )
        return QuerySemanticResponse(results=results)
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error")


@app.delete(
    "/delete-semantic",
    response_model=DeleteSemanticResponse,
)
async def delete_semantic(
    request: DeleteSemanticRequest = Body(...),
):
    if not (request.ids or request.filter or request.delete_all):
        raise HTTPException(
            status_code=400,
            detail="One of ids, filter, or delete_all is required",
        )
    try:
        success = await datastore.delete(
            ids=request.ids,
            filter=request.filter,
            delete_all=request.delete_all,
        )
        return DeleteSemanticResponse(success=success)
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error")


@app.post("/get-news", response_model=NewsResponse)
async def get_news(request: NewsRequest = Body(...)):
    try:
        raw_news = await pg_client.get_news_by_symbol(request.symbol, request.date)

        if not raw_news:
            raise HTTPException(
                status_code=404,
                detail=f"There is no news for symbol {request.symbol} on date {request.date}.",
            )

        # Map fetched data to NewsResponse model
        news = [
            News(content=n["content"], timestamp=n["timestamp"], sources=n["sources"])
            for n in raw_news
        ]
        return NewsResponse(news=news)

    except HTTPException as he:  # Handle our raised HTTPException first
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-summary", response_model=SummaryResponse)
async def get_summary(request: SummaryRequest = Body(...)):
    try:
        data = await pg_client.get_summary_by_symbol(request.symbol, request.date)

        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"There is no summary for symbol {request.symbol} on date {request.date}.",
            )

        # Transforming the news_records to the required format.
        news_sources = [
            News(
                content=record["content"],
                sources=[record["source"]],
                timestamp=record["timestamp"].isoformat()
                + "Z",  # Convert to the expected timestamp format
            )
            for record in data["news"]
        ]

        summary = Summary(
            summary=data["summary"]["summary"],
            date=data["summary"]["date"],
            sources=news_sources,
        )
        return SummaryResponse(summary=summary)

    except HTTPException as he:  # Handle our raised HTTPException first
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup():
    global datastore
    datastore = await get_datastore()
    await pg_client.connect()


@app.on_event("shutdown")
async def shutdown():
    await pg_client.close()
