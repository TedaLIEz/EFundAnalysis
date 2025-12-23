import os
from typing import cast

from dotenv import load_dotenv
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.embeddings.siliconflow import SiliconFlowEmbedding  # type: ignore

load_dotenv()


def create_embedding_model() -> BaseEmbedding:
    endpoint = os.getenv("ENDPOINT")
    api_key = os.getenv("API_KEY")
    model = os.getenv("EMBEDDING_MODEL")
    if not all([endpoint, api_key, model]):
        raise ValueError("Missing required environment variables: ENDPOINT, API_KEY, or EMBEDDING_MODEL")
    return cast("BaseEmbedding", SiliconFlowEmbedding(api_base=endpoint, api_key=api_key, model=model))
