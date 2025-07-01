import os
from dotenv import load_dotenv
from pymilvus import MilvusClient

load_dotenv()

def connect_to_milvus():
    """Connect to Milvus database."""

    milvus_uri = os.getenv("MILVUS_URI")
    token = os.getenv("MILVUS_TOKENS")

    if not milvus_uri or not token:
        raise ValueError("MILVUS_URI or MILVUS_TOKENS not set in .env")

    milvus_client = MilvusClient(uri=milvus_uri, token=token)

    return milvus_client
