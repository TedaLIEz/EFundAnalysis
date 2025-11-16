from llama_index.core import PromptTemplate, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms.function_calling import FunctionCallingLLM


class Rag:
    def __init__(self, llm: FunctionCallingLLM, embedding_model: BaseEmbedding):
        self.llm = llm
        self.embedding_model = embedding_model

    def load_document(self, document_path: str):
        documents = SimpleDirectoryReader(document_path).load_data()
        return VectorStoreIndex.from_documents(documents, embed_model=self.embedding_model)

    async def query(self, document_path: str, query: str) -> str:
        index = self.load_document(document_path)
        query_engine = index.as_query_engine(llm=self.llm)
        prompt_tmpl = (
            "Context information is below.\n---------------------\n{context_str}\n---------------------\nYou are a helpful assistant. \
                Use the above pieces of retrieved context to answer the question. \
                Keep the answer concise. \
                If you don't know the answer, just say 'I don't know'.Query: {query_str}\nAnswer: "
        )
        new_summary_tmpl = PromptTemplate(prompt_tmpl)
        query_engine.update_prompts({"response_synthesizer:summary_template": new_summary_tmpl})
        rst: str = query_engine.query(query)
        return rst
