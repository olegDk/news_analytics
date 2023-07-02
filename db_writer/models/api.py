from models.models import (
    Document,
    DocumentMetadataFilter,
    QuerySemantic,
    QuerySemanticResult,
)
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class ResponseType(str, Enum):
    image = "image"
    text = "text"


class UpsertSemanticRequest(BaseModel):
    documents: List[Document]


class UpsertSemanticResponse(BaseModel):
    ids: List[str]


class Query(BaseModel):
    query_text: str


class QueryResponse(BaseModel):
    response_type: ResponseType
    response_text: str


class QuerySemanticRequest(BaseModel):
    queries: List[QuerySemantic]


class QuerySemanticResponse(BaseModel):
    results: List[QuerySemanticResult]


class DeleteSemanticRequest(BaseModel):
    ids: Optional[List[str]] = None
    filter: Optional[DocumentMetadataFilter] = None
    delete_all: Optional[bool] = False


class DeleteSemanticResponse(BaseModel):
    success: bool
