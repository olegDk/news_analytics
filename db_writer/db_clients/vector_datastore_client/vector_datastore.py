from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
import hashlib
from models.models import (
    Document,
    DocumentChunk,
    DocumentMetadataFilter,
    QuerySemantic,
    QuerySemanticResult,
    QuerySemanticWithEmbedding,
)
from analytics.chunks import get_document_chunks
from analytics.aiclient.openai_client import get_embeddings


class VectorDataStore(ABC):
    async def insert_news(self, news_id: str, document: str) -> List[str]:
        tokenizer = tiktoken.get_encoding("cl100k_base")

        # create the length function
        def tiktoken_len(text):
            tokens = tokenizer.encode(text, disallowed_special=())
            return len(tokens)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=20,  # number of tokens overlap between chunks
            length_function=tiktoken_len,
            separators=["\n\n", "\n", " ", ""],
        )

        m = hashlib.md5()
        source = news_id
        m.update(source.encode("utf-8"))
        uid = m.hexdigest()[:12]
        chunks = text_splitter.split_text(document)
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append(
                Document(id=f"{uid}-{i}", text=chunk, metadata={"source_id": source})
            )

        return await self.upsert(documents)

    async def upsert(
        self, documents: List[Document], chunk_token_size: Optional[int] = None
    ) -> List[str]:
        """
        Takes in a list of documents and inserts them into the database.
        First deletes all the existing vectors with the document id (if necessary, depends on the vector db), then inserts the new ones.
        Return a list of document ids.
        """
        # Delete any existing vectors for documents with the input document ids
        await asyncio.gather(
            *[
                self.delete(
                    filter=DocumentMetadataFilter(
                        document_id=document.id,
                    ),
                    delete_all=False,
                )
                for document in documents
                if document.id
            ]
        )

        chunks = get_document_chunks(documents, chunk_token_size)

        return await self._upsert(chunks)

    @abstractmethod
    async def _upsert(self, chunks: Dict[str, List[DocumentChunk]]) -> List[str]:
        """
        Takes in a list of list of document chunks and inserts them into the database.
        Return a list of document ids.
        """

        raise NotImplementedError

    async def query(self, queries: List[QuerySemantic]) -> List[QuerySemanticResult]:
        """
        Takes in a list of queries and filters and returns a list of query results with matching document chunks and scores.
        """
        # get a list of of just the queries from the Query list
        query_texts = [query.query for query in queries]
        query_embeddings = get_embeddings(query_texts)
        # hydrate the queries with embeddings
        queries_with_embeddings = [
            QuerySemanticWithEmbedding(**query.dict(), embedding=embedding)
            for query, embedding in zip(queries, query_embeddings)
        ]
        return await self._query(queries_with_embeddings)

    @abstractmethod
    async def _query(
        self, queries: List[QuerySemanticWithEmbedding]
    ) -> List[QuerySemanticResult]:
        """
        Takes in a list of queries with embeddings and filters and returns a list of query results with matching document chunks and scores.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[DocumentMetadataFilter] = None,
        delete_all: Optional[bool] = None,
    ) -> bool:
        """
        Removes vectors by ids, filter, or everything in the datastore.
        Multiple parameters can be used at once.
        Returns whether the operation was successful.
        """
        raise NotImplementedError
