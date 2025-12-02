import os

from dotenv import load_dotenv
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.llms.azure_openai import AzureOpenAI

load_dotenv()


def create_llm() -> FunctionCallingLLM:
    aoai_api_key = os.getenv("AZURE_OPENAI_KEY")
    aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    aoai_api_version = os.getenv("AZURE_OPENAI_VERSION")
    aoai_model = os.getenv("AZURE_OPENAI_MODEL_NAME")
    aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    return AzureOpenAI(
        api_key=aoai_api_key,
        azure_endpoint=aoai_endpoint,
        api_version=aoai_api_version,
        model=aoai_model,
        engine=aoai_deployment,
    )
