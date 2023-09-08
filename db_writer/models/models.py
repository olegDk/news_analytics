from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class Source(str, Enum):
    email = "email"
    file = "file"
    chat = "chat"


class ResponseType(str, Enum):
    image = "image"
    text = "text"


class DocumentMetadata(BaseModel):
    source: Optional[Source] = None
    source_id: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[str] = None
    author: Optional[str] = None


class DocumentChunkMetadata(DocumentMetadata):
    document_id: Optional[str] = None


class DocumentChunk(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: DocumentChunkMetadata
    embedding: Optional[List[float]] = None


class DocumentChunkWithScore(DocumentChunk):
    score: float


class Document(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: Optional[DocumentMetadata] = None


class DocumentWithChunks(Document):
    chunks: List[DocumentChunk]


class DocumentMetadataFilter(BaseModel):
    document_id: Optional[str] = None
    source: Optional[Source] = None
    source_id: Optional[str] = None
    author: Optional[str] = None
    start_date: Optional[str] = None  # any date string format
    end_date: Optional[str] = None  # any date string format
    assets: Optional[List[str]] = None
    dates: Optional[List[str]] = None


class QuerySemantic(BaseModel):
    query: str
    filter: Optional[DocumentMetadataFilter] = None
    top_k: Optional[int] = 3


class QuerySemanticWithEmbedding(QuerySemantic):
    embedding: List[float]


class QuerySemanticResult(BaseModel):
    query: str
    results: List[DocumentChunkWithScore]


class SemanticModel(BaseModel):
    text: str


class CalculateCorrelationModel(BaseModel):
    assets: List[str]
    duration: Optional[int] = None
    duration_measure: Optional[str] = None
    starting: Optional[str] = None
    ending: Optional[str] = None


class CalculateBetaModel(BaseModel):
    assets: List[str]
    duration: Optional[int] = None
    duration_measure: Optional[str] = None
    starting: Optional[str] = None
    ending: Optional[str] = None


class CreatePlotModel(BaseModel):
    assets: List[str] = None
    duration: int = None
    type: str = None
    duration_measure: str = None
    starting: str = None
    ending: str = None
