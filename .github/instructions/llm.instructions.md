---
description: This rule is helpful for building an AI agent in the project, you should refer to this rule when you write AI agent like RAG, ReAct agents, etc.
applyTo: "core/llm/**/*.py"
---
# LLM and AI Agent Development Guide for GitHub Copilot

This guide covers LLM, agent, RAG, and related AI functionality for the FinWeave project.


You are an expert in Python, building AI agents by leveraging llamaindex.

## Key Principles

- Write concise, technical responses with accurate Python examples.
- Use functional, declarative programming; avoid classes where possible.
- Prefer iteration and modularization over code duplication.
- Use descriptive variable names with auxiliary verbs (e.g., is_active, has_permission).
- Use lowercase with underscores for directories and files (e.g., routers/user_routes.py).
- Favor named exports for routes and utility functions.
- Use the Receive an Object, Return an Object (RORO) pattern.
- Manage runtime within python virtual envrionment, this has been already included in the @venv folder.
- Manage dependencies with uv, there is one [pyproject.toml] in the codebase.
- Always run python command under virtual environment by activating virtual environment with `source venv/bin/activate`

## LLM Chat Functions

- **Always prioritize streaming for LLM chat functions**: When implementing chat functionality with LLMs, streaming should be the primary approach.
- **Provide both sync and async streaming methods**: Implement both synchronous (`stream_chat`) and asynchronous (`astream_chat`) streaming methods for maximum flexibility.
- **Streaming benefits**: Streaming provides better user experience (progressive response display), lower perceived latency, and more efficient memory usage for long responses.
- **Implementation pattern**:
  - Use generators (`Generator[str, None]`) for synchronous streaming
  - Use async generators (`AsyncGenerator[str, None]`) for asynchronous streaming
  - Yield chunks as they arrive from the LLM or workflow
  - Handle errors gracefully within the streaming loop
- **Non-streaming as fallback**: Non-streaming methods (`chat`) can be provided as convenience methods, but streaming should be the default implementation.
- **Memory management**: Ensure conversation memory is updated appropriately after streaming completes (either incrementally or at the end).

## Folder Structure

The LLM module is organized into the following components:

### Core Components

- **`core/llm/agent/agent.py`**: ReActAgent implementation with function calling capabilities
  - Uses `ReActAgent` from LlamaIndex
  - Supports tool registration and function calling
  - Provides `run()` method for synchronous execution
  - Returns `FunctionDescription` objects for registered functions
  - Handles max iteration errors gracefully

- **`core/llm/chat/chatbot.py`**: Basic chatbot with conversation memory
  - Uses `SimpleChatEngine` from LlamaIndex
  - Implements both sync (`stream_chat`) and async (`astream_chat`) streaming
  - Provides non-streaming `chat()` method as fallback
  - Uses `ChatMemoryBuffer` for conversation history
  - Supports system prompts

- **`core/llm/rag/rag.py`**: RAG (Retrieval-Augmented Generation) implementation
  - Uses `VectorStoreIndex` for document indexing
  - Supports document loading from directories
  - Provides async `query()` method with custom prompt templates
  - Requires both LLM and embedding model

### Model Management

- **`core/llm/model/factory.py`**: Factory pattern for creating LLM instances
  - `LLMFactory` class supports multiple providers (azure_openai, siliconflow)
  - Uses environment variable `LLM_PROVIDER` to determine default provider
  - Supports provider registration for extensibility
  - Returns `FunctionCallingLLM` instances

- **`core/llm/model/aopenai.py`**: Azure OpenAI provider implementation
  - Creates `AzureOpenAI` instances
  - Uses environment variables: `AZURE_OPENAI_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_VERSION`, `AZURE_OPENAI_MODEL_NAME`, `AZURE_OPENAI_DEPLOYMENT`

- **`core/llm/model/siliconflow.py`**: SiliconFlow provider implementation
  - Creates `SiliconFlow` instances
  - Uses environment variables: `ENDPOINT`, `API_KEY`, `LLM_MODEL`, `MAX_TOKENS`

- **`core/llm/model/__init__.py`**: Exports `create_llm()`, `LLMFactory`, and `LLMProvider`
  - Maintains backward compatibility with `create_llm()` function

### Embedding Models

- **`core/llm/embedding/siliconflow.py`**: SiliconFlow embedding model
  - Creates `SiliconFlowEmbedding` instances
  - Uses environment variables: `ENDPOINT`, `API_KEY`, `EMBEDDING_MODEL`
  - Returns `BaseEmbedding` instances

### Memory Management

- **`core/llm/memory/memory.py`**: Advanced memory system using LlamaIndex's Memory framework
  - `LLMMemory` class wraps LlamaIndex's `Memory` class
  - Supports multiple memory types:
    - **Short-term memory**: Chat history with token limits
    - **Static memory**: Fixed information that persists across conversations
    - **Fact extraction memory**: Automatically extracts and stores facts from conversations
    - **Vector memory**: Semantic search over conversation history
  - Factory methods:
    - `from_defaults()`: Short-term memory only
    - `with_static_memory()`: Adds static memory block
    - `with_fact_extraction()`: Adds fact extraction memory block
    - `with_vector_memory()`: Adds vector memory block
    - `with_all_memory_types()`: Combines all memory types
  - Returns `BaseMemory` compatible instances via `get_memory()`

### Prompt Management

- **`core/llm/prompt/prompt_loader.py`**: Liquid template-based prompt loader
  - `PromptLoader` class loads prompts from `.liquid` template files
  - Uses `CachingFileSystemLoader` for efficient template loading
  - Supports template rendering with context variables
  - Default prompt directory: `./prompt`
  - Methods:
    - `load_prompt()`: Load prompt without variables
    - `load_prompt_with_context()`: Load prompt with variable substitution

### Tools

- **`core/llm/tool/`**: Utility functions for use as LlamaIndex function tools
  - `date_util.py`: Date utility functions (e.g., `get_current_date()`)
  - Functions can be registered with agents using `FunctionTool.from_defaults()`

## Error Handling and Validation

- Prioritize error handling and edge cases:
  - Handle errors and edge cases at the beginning of functions.
  - Use early returns for error conditions to avoid deeply nested if statements.
  - Place the happy path last in the function for improved readability.
  - Avoid unnecessary else statements; use the if-return pattern instead.
  - Use guard clauses to handle preconditions and invalid states early.
  - Implement proper error logging and user-friendly error messages.
  - Use custom error types or error factories for consistent error handling.

## Usage Patterns

### Creating an Agent

```python
from core.llm.agent import Agent
from core.llm.tool.date_util import get_current_date

## Create agent with default LLM
agent = Agent(tools=[get_current_date])

## Run agent
response = agent.run("What is today's date?")
```

### Creating a Chatbot with Streaming

```python
from core.llm.chat import Chatbot

## Create chatbot
chatbot = Chatbot(system_prompt="You are a helpful assistant.")

## Stream response (async)
async for token in chatbot.astream_chat("Hello!"):
    print(token, end="", flush=True)

## Stream response (sync)
for token in chatbot.stream_chat("Hello!"):
    print(token, end="", flush=True)
```

### Using RAG

```python
from core.llm.rag import Rag
from core.llm.model import LLMFactory
from core.llm.embedding import create_embedding_model

llm = LLMFactory.create()
embedding = create_embedding_model()
rag = Rag(llm=llm, embedding_model=embedding)

response = await rag.query(document_path="./documents", query="What is this about?")
```

### Using Advanced Memory

```python
from core.llm.memory import LLMMemory
from core.llm.model import LLMFactory
from core.llm.embedding import create_embedding_model

llm = LLMFactory.create()
embedding = create_embedding_model()

## Create memory with all types
memory = LLMMemory.with_all_memory_types(
    llm=llm,
    embed_model=embedding,
    static_content="User preferences: prefers concise answers",
    token_limit=3000
)

## Use with agent or chatbot
from core.llm.agent import Agent
agent = Agent(llm=llm, memory=memory.get_memory())
```

### Loading Prompts

```python
from core.llm.prompt import PromptLoader

prompt_loader = PromptLoader()
## Load prompt without variables
prompt = prompt_loader.load_prompt("template.liquid")

## Load prompt with variables
prompt = prompt_loader.load_prompt_with_context(
    "template.liquid",
    {"variable_name": "value"}
)
```

### Using LLM Factory

```python
from core.llm.model import LLMFactory

## Create with default provider (from LLM_PROVIDER env var)
llm = LLMFactory.create()

## Create with specific provider
llm = LLMFactory.create(provider="azure_openai")

## Get supported providers
providers = LLMFactory.get_supported_providers()
```

## Dependencies

- **Pydantic v2**: For data validation and serialization
- **LlamaIndex 0.12.24**: Core framework for agents, RAG, embeddings, memory, and chat engines
- **Liquid**: For template rendering in prompt loader
- **python-dotenv**: For environment variable management

Refer to LlamaIndex documentation for Agents, RAG, Embeddings, Memory, Query Engines and Multi-Model for best practices.
