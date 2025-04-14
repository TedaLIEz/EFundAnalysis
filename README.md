# EFund Analysis Project

This project is set up with Python virtual environment for development.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- On macOS/Linux:
```bash
source venv/bin/activate
```
- On Windows:
```bash
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development

1. Always activate the virtual environment before working on the project
2. Add new dependencies to requirements.txt:
```bash
pip freeze > requirements.txt
```

## Project Structure

```
.
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── .gitignore            # Git ignore rules
├── data/                 # Directory for storing data files
├── tests/                # Test files and test resources
└── src/                  # Source code directory
    ├── __init__.py      # Makes src a Python package
    ├── main.py          # Main application entry point
    ├── analyzer/        # Analysis modules and algorithms
    ├── core/            # Core functionality and utilities
    └── data_provider/   # Data acquisition and processing modules
```

## Environment Variables

The project uses a `.env` file for configuration. Make sure to set up your environment variables properly before running the application.

## Testing

The project includes a test suite in the `tests/` directory. To run the tests:

```bash
pytest
``` 