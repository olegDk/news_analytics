from models.models import (
    Document,
    DocumentMetadataFilter,
    QuerySemantic,
    QuerySemanticResult,
)
from pydantic import BaseModel
from typing import List, Optional, Union
from enum import Enum
from datetime import date, datetime


class ResponseType(str, Enum):
    image = "image"
    text = "text"


class UpsertSemanticRequest(BaseModel):
    documents: List[Document]


class UpsertSemanticResponse(BaseModel):
    ids: List[str]


class Query(BaseModel):
    query_text: str


class SourceDetail(BaseModel):
    content: str
    sources: List[str]
    timestamp: str


class Reply(BaseModel):
    reply: str
    sources: List[Union[SourceDetail, str]]
    type: str


class QueryResponse(BaseModel):
    reply: Reply


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


class News(BaseModel):
    content: str
    timestamp: datetime
    sources: List[str]


class Summary(BaseModel):
    summary: str
    date: date
    sources: List[News]


class NewsRequest(BaseModel):
    symbol: str
    date: date


class SummaryRequest(BaseModel):
    symbol: str
    date: date


class NewsResponse(BaseModel):
    news: List[News]


class SummaryResponse(BaseModel):
    summary: Summary
