from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, Depends, Body, UploadFile


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


app = FastAPI()
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
def query(
    request: Query = Body(...),
):
    try:
        response_text = process_query(request.query_text)
        return QueryResponse(
            response_type=ResponseType.text, response_text=response_text
        )
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error")


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
async def get_news(
    request: NewsRequest = Body(...),
):
    try:
        raw_news = await pg_client.get_news_by_symbol(request.symbol, request.date)
        print(len(raw_news))
        news = [News(**n) for n in raw_news]
        return NewsResponse(news=news)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-summary", response_model=SummaryResponse)
async def get_summary(
    request: SummaryRequest = Body(...),
):
    try:
        raw_summary = await pg_client.get_summary_by_symbol(
            request.symbol, request.date
        )
        print(raw_summary)
        summary = Summary(summary=raw_summary)
        return SummaryResponse(summary=summary)
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
