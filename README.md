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
├── README.md
├── requirements.txt
└── src/
    └── main.py
``` 