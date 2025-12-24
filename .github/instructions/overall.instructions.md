---
description: Overall project rules and conventions for FinWeave
applyTo: "**/*"
---
## Overall Rules for FinWeave Project

## Python Command Execution

**CRITICAL: Always use `uv run` prefix for any Python command or tool execution.**

- ✅ **CORRECT**: `uv run python app.py`
- ✅ **CORRECT**: `uv run python -m http.server 8080`
- ✅ **CORRECT**: `uv run pytest`
- ✅ **CORRECT**: `uv run --dev pre-commit install`
- ❌ **WRONG**: `python app.py`
- ❌ **WRONG**: `pytest`
- ❌ **WRONG**: `python -m http.server`

When running development tools or scripts that require dev dependencies, use `uv run --dev`:
- ✅ `uv run --dev pre-commit install`
- ✅ `uv run --dev pre-commit run --all-files`

## Dependency Management

This project uses `uv` (a fast Python package installer and resolver) for dependency management.

- **Install/update dependencies**: `uv sync --dev`
- **Install a new package**: `uv pip install package_name` (then add to pyproject.toml and run `uv sync`)
- **Add dependency**: Add to `pyproject.toml` dependencies list, then run `uv sync`
- **Remove dependency**: Remove from `pyproject.toml`, then run `uv sync`
- **If VIRTUAL_ENV warning appears**: Use `uv sync` (the `--active` flag is handled automatically)

## Python Version

- **Required**: Python 3.11 or higher (but less than 3.13)
- Ensure compatible Python version is installed before setup

## Virtual Environment

- The project uses `uv` which manages virtual environments automatically
- When using `uv run`, the virtual environment is automatically activated
- If manual activation is needed: `source .venv/bin/activate` (macOS/Linux) or `.\.venv\Scripts\activate` (Windows)

## Testing

- Run tests using: `uv run pytest` in `tests/unit/`
- Run tests using: `uv run python <test_file>.py` in `tests/integration`

## Code Quality

- Git hooks are set up via: `uv run --dev pre-commit install`
- Pre-commit runs automatically on git commit
- Manual run: `uv run --dev pre-commit run --all-files`

## Running the Application

- Development mode: `uv run python app.py`
- The service runs at `http://localhost:5001` by default

## Docker Development

- Use Docker Compose for local testing: `docker-compose up -d`
- This starts both API service (port 5001) and dev UI (port 8080)
- Stop services: `docker-compose down`

## Code Style and Formatting

### Ruff Configuration
- **Line length**: Maximum 120 characters
- **Quote style**: Use double quotes (`"`) for strings
- **Indentation**: Use spaces (not tabs)
- **Trailing commas**: Include trailing commas in multi-line structures

### Code Formatting Commands
- Format code: `uv run --dev ruff format --exclude dev_ui --exclude tests ./`
- Lint and auto-fix: `uv run --dev ruff check --fix --exclude dev_ui --exclude tests ./`
- Check environment variables: `uv run --dev dotenv-linter ./.env.example`
- Format all (via script): `./tools/format` (runs formatting, linting, and env checks)

### Type Checking
- Run type checking: `uv run --dev --with pip python -m mypy --install-types --non-interactive --cache-fine-grained --sqlite-cache .`
- Type check script: `./tools/mypy_check`
- **Always use type hints** for function signatures and method definitions
- Use `typing` module for complex types (e.g., `Callable`, `Any`, `cast`)
- Enable strict type checking: `warn_return_any`, `check_untyped_defs` are enabled

## Import Organization

- **Import order**: Standard library → Third-party → First-party (analyzer, core, data_provider)
- Use `isort` for automatic import sorting (configured in ruff)
- Known first-party packages: `["analyzer", "core", "data_provider"]`
- Force sort within sections and split on trailing comma
- Relative imports are allowed (TID252 is ignored)

## Module Dependencies

**CRITICAL: Separate dependencies between `api/`, `core/`, and `tests/` folders. Production code must never import from test modules.**

### Dependency Rules

- ✅ **CORRECT**: Code in `api/` can import from `core/`, `analyzer/`, `data_provider/`, and `extensions/`
- ✅ **CORRECT**: Code in `core/` can import from `analyzer/`, `data_provider/`
- ✅ **CORRECT**: Code in `tests/` can import from `api/`, `core/`, `analyzer/`, `data_provider/`, and `extensions/`
- ✅ **CORRECT**: Code in `tests/` can import from other test modules (e.g., `tests/mock/`, `tests/data/`)
- ❌ **WRONG**: Code in `api/` importing from `tests/` (e.g., `from tests.mock import ...`)
- ❌ **WRONG**: Code in `core/` importing from `tests/` (e.g., `from tests.mock import ...`)
- ❌ **WRONG**: Production code importing test utilities or mocks

### Dependency Flow

```
┌─────────────┐
│   tests/    │ ──┐
└─────────────┘   │
                  │ Can import from
┌─────────────┐   │
│    api/     │ ──┼──┐
└─────────────┘   │  │
                  │  │ Can import from
┌─────────────┐   │  │
│   core/     │ ──┼──┼──┐
└─────────────┘   │  │  │
                  │  │  │ Can import from
┌─────────────┐   │  │  │
│  analyzer/  │ ──┼──┼──┼──┐
└─────────────┘   │  │  │  │
                  │  │  │  │ Can import from
┌─────────────┐   │  │  │  │
│data_provider│ ──┼──┼──┼──┼──┐
└─────────────┘   │  │  │  │  │
                  │  │  │  │  │
                  ▼  ▼  ▼  ▼  ▼
            Standard library & Third-party
```

### Examples

**✅ CORRECT - API importing from core:**
```python
## api/chat/chat.py
from core.llm.chat.chatbot import Chatbot
```

**✅ CORRECT - Test importing from core:**
```python
## tests/integration/test_chatbot.py
from core.llm.chat.chatbot import Chatbot
```

**✅ CORRECT - Test importing from mock:**
```python
## tests/integration/test_memory.py
from tests.mock.mock_vector_store import MockVectorStore
```

**❌ WRONG - API importing from tests:**
```python
## api/chat/chat.py
from tests.mock.mock_vector_store import MockVectorStore  # ❌ NEVER DO THIS
```

**❌ WRONG - Core importing from tests:**
```python
## core/llm/memory/memory.py
from tests.mock.mock_vector_store import MockVectorStore  # ❌ NEVER DO THIS
```

### Rationale

- **Separation of concerns**: Production code (`api/`, `core/`) should be independent of test infrastructure
- **Deployment**: Test code should not be included in production deployments
- **Maintainability**: Clear boundaries prevent circular dependencies and improve code organization
- **Testing**: Tests can use production code, but production code should not depend on test utilities

## Code Quality Standards

### Linting Rules
- Follow PEP 8 style guide (enforced via ruff)
- Use descriptive variable names with auxiliary verbs (e.g., `is_active`, `has_permission`)
- Maximum cyclomatic complexity: 10 (enforced via mccabe)
- Remove commented-out code (eradicate checks enabled)
- Use pathlib for file paths (PTH checks enabled)
- Follow pandas best practices (PD checks enabled)

### Error Handling
- Handle errors and edge cases at the beginning of functions
- Use early returns for error conditions to avoid deeply nested if statements
- Place the happy path last in the function for improved readability
- Avoid unnecessary else statements; use the if-return pattern instead
- Use guard clauses to handle preconditions and invalid states early
- Implement proper error logging and user-friendly error messages

### Code Patterns
- Prefer functional, declarative programming; use classes only when necessary (e.g., for complex resource management)
- Prefer iteration and modularization over code duplication
- Use the Receive an Object, Return an Object (RORO) pattern where applicable
- Use list/dict comprehensions when appropriate (C4 checks enabled)
- Simplify code where possible (SIM checks enabled)

## Documentation

### Cursor Rules Maintenance

**CRITICAL: Every time when code is updated, you should update the cursor rules under `.cursor/rules/` according to your changes.**

- ✅ **CORRECT**: Update relevant rule files (e.g., `python-llm-rule.mdc`, `python-kyc-module.mdc`, `overall-rule.mdc`) when making code changes
- ✅ **CORRECT**: Keep project structure documentation in `overall-rule.mdc` synchronized with actual codebase structure
- ✅ **CORRECT**: Update module-specific rules when adding new features or changing implementations
- ❌ **WRONG**: Make code changes without updating corresponding documentation in cursor rules

### When to Update Rules

- **New modules or components**: Add documentation to appropriate rule files
- **Changed project structure**: Update `overall-rule.mdc` Project Structure section
- **New patterns or conventions**: Document in relevant rule files
- **API changes**: Update `python-api-rule.mdc` if applicable
- **LLM/Agent changes**: Update `python-llm-rule.mdc`
- **KYC workflow changes**: Update `python-kyc-module.mdc`
- **Data provider changes**: Update `python-data-akshare.mdc` if applicable

### Rule File Organization

- `overall-rule.mdc`: General project rules, structure, and conventions (always applies)
- `python-llm-rule.mdc`: LLM, agent, RAG, and related AI functionality
- `python-kyc-module.mdc`: KYC workflow and customer management
- `python-api-rule.mdc`: API development patterns and FastAPI conventions
- `python-data-akshare.mdc`: Data provider implementations
- `python-test.mdc`: Testing standards and patterns
- `liquid-prompt.mdc`: Liquid template syntax and prompt management

## File and Directory Naming

- **Directories and files**: Use lowercase with underscores (e.g., `api/observability/health.py`)
- **Test files**: Must match patterns `test_*.py` or `*_test.py`
- **Module organization**: Organize by domain/feature (e.g., `api/observability/`, `core/llm/agent/`)

## Project Structure

### Core Modules
- `analyzer/`: Analysis modules and algorithms
  - `portfolio_analyzer.py`: Portfolio analysis functionality
- `core/`: Core functionality and utilities
  - `llm/`: LLM-related modules
    - `agent/`: ReActAgent implementation with function calling
    - `chat/`: Chatbot with streaming support
    - `embedding/`: Embedding model implementations (SiliconFlow)
    - `memory/`: Advanced memory system with multiple memory types
    - `model/`: LLM factory and provider implementations (Azure OpenAI, SiliconFlow)
    - `prompt/`: Liquid template-based prompt loader
    - `rag/`: RAG (Retrieval-Augmented Generation) implementation
    - `tool/`: Utility functions for use as LlamaIndex function tools
  - `kyc/`: KYC workflow modules
    - `models/`: KYC data models (e.g., `customer.py`)
    - `workflows/`: KYC agent and workflow implementations
  - `sockets/`: WebSocket handlers for real-time communication
  - `util/`: Utility functions (e.g., `json_util.py`)
- `api/`: API endpoints and resources (organized by domain)
  - `chat/`: Chat API endpoints
  - `observability/`: Health check and observability endpoints
- `data_provider/`: Data acquisition and processing modules
  - `fund.py`: Fund data provider
  - `stock.py`: Stock data provider
- `extensions/`: FastAPI extensions
  - `ext_blueprint.py`: Blueprint registration
  - `ext_error_handling.py`: Global error handlers
  - `ext_logging.py`: Logging configuration
- `tests/`: Test files
  - `unit/`: Unit tests
  - `integration/`: Integration tests
  - `data/`: Test data files
- `prompt/`: Liquid template prompt files (`.liquid` extension)
- `dev_ui/`: Development UI (HTML/JavaScript)
- `frontend/`: Production frontend
  - `react/`: React-based frontend application
- `docker/`: Docker-related files
  - `entrypoint.sh`: Docker entrypoint script
- `tools/`: Development tools and scripts
  - `format`: Code formatting script
  - `mypy_check`: Type checking script

### Key Files
- `app.py`: FastAPI application entry point
- `pyproject.toml`: Project and dependency configuration
- `.ruff.toml`: Ruff linting and formatting configuration
- `mypy.ini`: Type checking configuration
- `.pre-commit-config.yaml`: Pre-commit hooks configuration
- `docker-compose.yml`: Docker Compose configuration
- `Dockerfile`: Docker image definition
- `uv.lock`: Dependency lock file (managed by uv)

## Environment Variables

- Use `.env` file for local development (not committed to git)
- Use `.env.example` as a template (committed to git)
- Load environment variables using `python-dotenv` (`load_dotenv()`)
- Never commit `.env` or `.env.local` files (they're in `.gitignore`)
- Validate environment variables using `dotenv-linter` before committing


## Prompt Management

### Using PromptLoader

**CRITICAL: Always use `PromptLoader` from `core/llm/prompt/prompt_loader.py` to load prompts. Never hardcode prompt strings in code.**

- ✅ **CORRECT**: Use `PromptLoader` to load prompts from `.liquid` files
- ❌ **WRONG**: Hardcode prompt strings directly in Python code

### Prompt File Organization

- **Location**: All prompt templates must be stored in the `prompt/` directory
- **File extension**: Use `.liquid` extension for all prompt templates
- **Naming**: Use descriptive, lowercase names with underscores (e.g., `intent_detection.liquid`, `kyc.liquid`)

### Creating Prompt Templates

1. **Create the template file** in `prompt/` directory with `.liquid` extension
2. **Add template metadata** in comments at the top:
   ```liquid
   {% comment %}
   Template: template_name.liquid
   Purpose: Brief description of what this prompt does
   Variables:
     - variable_name: Description of the variable
   {% endcomment %}
   ```
3. **Use Liquid syntax** for variables: `{{ variable_name }}`
4. **Load in code** using `PromptLoader`:
   ```python
   from core.llm.prompt.prompt_loader import PromptLoader

   prompt_loader = PromptLoader()
   # For prompts without variables
   prompt = prompt_loader.load_prompt("template_name.liquid")
   # For prompts with variables
   prompt = prompt_loader.load_prompt_with_context("template_name.liquid", {"variable_name": value})
   ```

### Initializing PromptLoader

- **In classes**: Initialize `PromptLoader` in `__init__`:
  ```python
  def __init__(self):
      self.prompt_loader = PromptLoader()
  ```
- **In functions**: Create instance when needed:
  ```python
  prompt_loader = PromptLoader()
  prompt = prompt_loader.load_prompt("template.liquid")
  ```

### Best Practices

- **Never hardcode prompts**: Always create `.liquid` files for prompts, even simple ones
- **Use variables**: Make prompts configurable through Liquid variables
- **Document variables**: Always document variables in template comments
- **Reuse templates**: Create reusable templates that can be used across different contexts
- **Follow Liquid syntax**: Use proper Liquid syntax (`{{ }}` for output, `{% %}` for logic)
- **Test templates**: Verify templates work with various variable combinations

### Example: Refactoring Hardcoded Prompts

**Before (❌ WRONG):**
```python
PROMPT = """You are a helpful assistant.
User input: {user_input}
Please respond."""
prompt = PROMPT.format(user_input=user_input)
```

**After (✅ CORRECT):**
```python
## In prompt/assistant.liquid:
{% comment %}
Template: assistant.liquid
Purpose: Basic assistant prompt
Variables:
  - user_input: User's input message
{% endcomment %}
You are a helpful assistant.
User input: {{ user_input }}
Please respond.

## In Python code:
from core.llm.prompt.prompt_loader import PromptLoader

prompt_loader = PromptLoader()
prompt = prompt_loader.load_prompt_with_context("assistant.liquid", {"user_input": user_input})
```

### Reference

- See `.cursor/rules/liquid-prompt.mdc` for detailed Liquid syntax guide
- Existing prompt examples: `prompt/kyc.liquid`, `prompt/intent_detection.liquid`, `prompt/asset_allocation.liquid`

## Git Workflow

### Pre-commit Hooks
- Pre-commit runs automatically on `git commit`
- Hooks include:
  - Code formatting (ruff format)
  - Linting (ruff check)
  - Environment variable validation (dotenv-linter)
  - Type checking (mypy)
  - Trailing whitespace removal
  - End-of-file fixer
  - YAML validation
  - Large file checks
  - Merge conflict detection
  - Debug statement detection

### Manual Pre-commit Run
- Test all hooks: `uv run --dev pre-commit run --all-files`
- Install hooks: `uv run --dev pre-commit install`

## Testing Standards

- **Test location**: `tests/unit/` for unit tests, `tests/integration/` for integration tests
- **Test naming**: Files must match `test_*.py` or `*_test.py` patterns
- **Run tests**: `uv run pytest` or `uv run pytest tests/unit -v`
- **Test data**: Store test data files in `tests/data/`
- Tests can use assertions (`S101` ignored for tests)
- Tests can have longer lines and unused imports (relaxed rules)

## Excluded Directories

The following directories are excluded from linting/formatting:
- `dev_ui/`: Development UI files (HTML/JavaScript)
- `tests/`: Test files have relaxed linting rules
- `__init__.py`: Unused imports allowed
- `app.py`: Unused imports allowed (FastAPI decorators)

## Logging

- Use Python's `logging` module consistently
- Create loggers: `logger = logging.getLogger(__name__)`
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Log errors with context and user-friendly messages

## Security Best Practices

- Validate and sanitize all user inputs
- Use environment variables for sensitive configuration (secrets, API keys)
- Never hardcode credentials or API keys
- Use HTTPS in production
- Implement proper authentication and authorization where needed
- Use CORS appropriately; avoid allowing all origins in production

## API Response Patterns

### HTTP API Responses
- **Success responses**: Return `{"data": ...}` or direct data dict
- **Error responses**: Return `{"error": "message"}` with appropriate HTTP status code
- Use `HTTPStatus` enum from `http` module for status codes (not magic numbers)
- Return dicts directly from route handlers (FastAPI handles JSON serialization automatically)
- Raise `HTTPException` for error responses: `raise HTTPException(status_code=HTTPStatus.XXX, detail="message")`

### WebSocket Responses
- **Success responses**: `{"type": "assistant"|"system", "message": "..."}`
- **Error responses**: `{"type": "error", "message": "..."}`
- Use `await sio.emit()` for sending responses: `await sio.emit("response", {...}, room=sid)` or `await sio.emit("error", {...}, room=sid)`
- All Socket.IO handlers must be async functions
- Handle connection lifecycle: `connect`, `disconnect`, `error` events
- Session ID (sid) is passed as the first parameter to handlers
- Use rooms for targeted broadcasting instead of broadcasting to all clients

### Error Handling Patterns
- Use try-except blocks with `logger.exception()` for error logging
- Return user-friendly error messages
- Don't expose internal error details to clients in production
- Use custom exception classes for domain-specific errors when appropriate
- Global error handlers are configured in `extensions/ext_error_handling.py`

## Data Validation

- Use Pydantic models (v2) for data validation and serialization (automatic with FastAPI)
- Use Pydantic models for request body validation (FastAPI automatically validates)
- Use FastAPI's Query, Path, and Body dependencies for query parameters, path parameters, and request bodies
- Validate required fields using Pydantic model fields (required=True, Optional, etc.)
- FastAPI automatically returns 422 Unprocessable Entity for validation errors with detailed messages
- Use Pydantic models as function parameters for automatic request body parsing and validation
