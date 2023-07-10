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
)
from db_clients.vector_datastore_client.factory import get_datastore
from analytics.file import get_document_from_file
from analytics.analytics_client import process_query

from models.models import DocumentMetadata, Source


app = FastAPI()


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


@app.on_event("startup")
async def startup():
    global datastore
    datastore = await get_datastore()
