def connect_to_milvus():
    """Connect to Milvus database."""

    milvus_uri = "MILVUS_URI"
    token = "MILVUS_TOKENS"

    milvus_client = MilvusClient(uri=milvus_uri, token=token)

    return milvus_client