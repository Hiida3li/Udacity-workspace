def connect_to_milvus():
    """Connect to Milvus database."""
    
    milvus_uri = "https://in03-0b7b3bf700c918d.serverless.gcp-us-west1.cloud.zilliz.com"
    token = "ea0499cffe5d78709fb7e7ee63ee0deb8dd7eca7d47b6dbd3e9eeba03c1108623347fe3fc0ad1ca2c71d7107cd6cc8a7984fe6ae"

    milvus_client = MilvusClient(uri=milvus_uri, token=token)

    return milvus_client