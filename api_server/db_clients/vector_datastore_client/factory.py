from db_clients.vector_datastore_client.vector_datastore import (
    VectorDataStore,
)
import os
from dotenv import load_dotenv

load_dotenv()


async def get_datastore() -> VectorDataStore:
    datastore = os.environ.get("VECTOR_DATASTORE")
    assert datastore is not None

    if datastore == "pinecone":
        from db_clients.vector_datastore_client.pinecone_datastore import (
            PineconeDataStore,
        )

        return PineconeDataStore()
    else:
        raise ValueError(f"Unsupported vector database: {datastore}")
