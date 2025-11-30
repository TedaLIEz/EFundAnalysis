# FinWeave Project

This project uses `uv` (a fast Python package installer and resolver) for dependency management.

## Prerequisites

1. Install `uv` if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies:

```bash
uv sync --dev
```

3. Set up git hooks for automatic code formatting and linting:

```bash
uv run --dev pre-commit install
# (Optional) Run pre-commit on all files to test the setup
uv run --dev pre-commit run --all-files
```

## Development

1. Always activate the virtual environment before working on the project
2. Managing dependencies:
   - Install a new package: `uv pip install package_name`
   - Update dependencies: `uv sync`
   - Add a new dependency to pyproject.toml: Add it to the dependencies list and run `uv sync`
   - Uninstall a package: Remove it from pyproject.toml and run `uv sync`
3. Run the application:
   - Development mode: `uv run python app.py`

## Project Structure

```text
.
├── README.md               # Project documentation
├── pyproject.toml         # Project and dependency configuration
├── uv.lock                # Locked dependency versions
├── mypy.ini               # Type checking configuration
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
├── .gitignore            # Git ignore rules
├── app.py                # Flask application entry point
├── data/                 # Directory for storing data files
├── tests/                # Test files and test resources
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── data/             # Test data files
├── analyzer/             # Analysis modules and algorithms
│   └── portfolio_analyzer.py
├── api/                  # API endpoints and resources
│   └── observability/
│       └── health.py     # Health check endpoint
├── core/                 # Core functionality and utilities
│   ├── llm/              # LLM-related modules
│   │   ├── agent/        # AI agent implementation
│   │   ├── chat/         # Chatbot functionality
│   │   ├── model/        # LLM model integrations
│   │   └── rag/          # Retrieval-Augmented Generation
│   └── sockets/          # WebSocket handlers
├── data_provider/        # Data acquisition and processing modules
│   ├── common_util.py
│   └── fund.py
├── docker/               # Docker-related scripts
│   └── entrypoint.sh     # Container entrypoint script
└── tools/                # Development tools and scripts
    ├── format            # Code formatting script
    └── mypy_check        # Type checking script
```

## Docker Compose

The easiest way to run the application is using Docker Compose:

1. Make sure you have Docker and Docker Compose installed on your system.

2. Create a `.env` file in the project root with your environment variables (if not already present).

3. Start the application:

```bash
docker-compose up -d
```

4. The application will be available at `http://localhost:5001`

5. Check the health endpoint:

```bash
curl http://localhost:5001/health
```

6. View logs:

```bash
docker-compose logs -f
```

7. Stop the application:

```bash
docker-compose down
```

The Docker Compose setup includes:
- Automatic health checks
- Port mapping (5001:5001)
- Volume mounting for persistent data storage
- Environment variable support via `.env` file
- Automatic restart on failure

## Environment Variables

The project uses a `.env` file for configuration. Make sure to set up your environment variables properly before running the application. The Docker Compose setup automatically loads environment variables from the `.env` file.

## Testing

The project includes a test suite in the `tests/unit` directory. To run the tests:

```bash
pytest
```

## Python Version

This project requires Python 3.11 or higher (but less than 3.13). Make sure you have a compatible Python version installed before setting up the project.

## Common Issues

1. If you see a warning about VIRTUAL_ENV not matching when using `uv sync`, always use the `--active` flag:

```bash
uv sync
```

2. Make sure to activate your virtual environment (`.venv`) before running any commands:

```bash
source .venv/bin/activate  # on macOS/Linux
.\.venv\Scripts\activate   # on Windows
```
