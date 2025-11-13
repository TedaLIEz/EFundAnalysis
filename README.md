# EFund Analysis Project

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
   - Run `uv run flask run --host 0.0.0.0 --port=5000 --debug`

## Project Structure

```
.
├── README.md               # Project documentation
├── pyproject.toml         # Project and dependency configuration
├── .gitignore            # Git ignore rules
├── data/                 # Directory for storing data files
├── tests/                # Test files and test resources
├── analyzer/             # Analysis modules and algorithms
├── core/                 # Core functionality and utilities
└── data_provider/        # Data acquisition and processing modules
```

## Environment Variables

The project uses a `.env` file for configuration. Make sure to set up your environment variables properly before running the application.

## Testing

The project includes a test suite in the `tests/` directory. To run the tests:

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
