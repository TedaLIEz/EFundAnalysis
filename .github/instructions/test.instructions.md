---
description: This rule provides guidelines for writing test cases in Python with pytest. Refer to this rule when writing code in the `tests/` folder.
applyTo: "tests/**/*.py"
---
# Python Testing Guide for GitHub Copilot

This guide covers writing test cases in Python with pytest for the FinWeave project.

You are an expert in writting test cases in Python with pytest.

Key Principles

- Write concise, technical responses with accurate Python examples.
- Use functional, declarative programming; avoid classes where possible.
- Prefer iteration and modularization over code duplication.
- Use descriptive variable names with auxiliary verbs (e.g., is_active, has_permission).
- Use lowercase with underscores for directories and files (e.g., routers/user_routes.py).
- Favor named exports for routes and utility functions.
- Manage dependencies with pip, there is one @requirements.txt in the codebase.
- Always run python command under virtual environment by activating virtual environment with `source venv/bin/activate`
- Cover the golden path and corner cases of the function you want to test.

How to run the test?
You should always run the test for your code. You can run the following commands to verify:
```
uv run python -m pytest tests/ -v
```
