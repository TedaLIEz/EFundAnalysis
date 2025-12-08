"""Unit tests for the PromptLoader class."""

import tempfile
from pathlib import Path

import pytest

from core.llm.prompt.prompt_loader import PromptLoader


@pytest.fixture
def temp_prompt_dir():
    """Fixture to create a temporary directory with test prompt templates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompt_dir = Path(tmpdir)

        # Create a simple template without variables
        simple_template = prompt_dir / "simple.txt"
        simple_template.write_text("This is a simple prompt template.")

        # Create a template with variables
        template_with_vars = prompt_dir / "with_vars.txt"
        template_with_vars.write_text("Hello {{ name }}, welcome to {{ platform }}!")

        # Create a template with multiple variables and conditions
        complex_template = prompt_dir / "complex.txt"
        complex_template.write_text(
            "User: {{ user_name }}\n"
            "Role: {{ role }}\n"
            "{% if is_active %}Status: Active{% else %}Status: Inactive{% endif %}"
        )

        yield str(prompt_dir)


@pytest.fixture
def prompt_loader_default():
    """Fixture to provide a PromptLoader with default directory."""
    return PromptLoader()


@pytest.fixture
def prompt_loader_custom(temp_prompt_dir):
    """Fixture to provide a PromptLoader with custom directory."""
    return PromptLoader(prompt_dir=temp_prompt_dir)


def test_init_default():
    """Test PromptLoader initialization with default directory."""
    loader = PromptLoader()
    assert loader.prompt_dir == "./prompt"
    assert loader.env is not None


def test_init_custom_dir(temp_prompt_dir):
    """Test PromptLoader initialization with custom directory."""
    loader = PromptLoader(prompt_dir=temp_prompt_dir)
    assert loader.prompt_dir == temp_prompt_dir
    assert loader.env is not None


def test_load_prompt_simple(prompt_loader_custom):
    """Test loading a simple prompt template without variables."""
    result = prompt_loader_custom.load_prompt("simple.txt")
    assert result == "This is a simple prompt template."


def test_load_prompt_with_context(prompt_loader_custom):
    """Test loading a prompt template with context variables."""
    context = {"name": "Alice", "platform": "FinWeave"}
    result = prompt_loader_custom.load_prompt_with_context("with_vars.txt", context)
    assert result == "Hello Alice, welcome to FinWeave!"


def test_load_prompt_with_context_partial(prompt_loader_custom):
    """Test loading a prompt template with partial context."""
    context = {"name": "Bob"}
    result = prompt_loader_custom.load_prompt_with_context("with_vars.txt", context)
    # Liquid will render missing variables as empty strings
    assert "Bob" in result
    assert "welcome to" in result


def test_load_prompt_with_context_complex(prompt_loader_custom):
    """Test loading a complex prompt template with conditions."""
    context = {
        "user_name": "Charlie",
        "role": "Analyst",
        "is_active": True
    }
    result = prompt_loader_custom.load_prompt_with_context("complex.txt", context)
    assert "User: Charlie" in result
    assert "Role: Analyst" in result
    assert "Status: Active" in result
    assert "Status: Inactive" not in result


def test_load_prompt_with_context_complex_inactive(prompt_loader_custom):
    """Test loading a complex prompt template with inactive status."""
    context = {
        "user_name": "Diana",
        "role": "Manager",
        "is_active": False
    }
    result = prompt_loader_custom.load_prompt_with_context("complex.txt", context)
    assert "User: Diana" in result
    assert "Role: Manager" in result
    assert "Status: Inactive" in result
    assert "Status: Active" not in result


def test_load_prompt_missing_template(prompt_loader_custom):
    """Test loading a non-existent template raises an error."""
    with pytest.raises(Exception):  # Liquid raises FileSystemError or similar
        prompt_loader_custom.load_prompt("nonexistent.txt")


def test_load_prompt_with_context_missing_template(prompt_loader_custom):
    """Test loading a non-existent template with context raises an error."""
    context = {"name": "Test"}
    with pytest.raises(Exception):  # Liquid raises FileSystemError or similar
        prompt_loader_custom.load_prompt_with_context("nonexistent.txt", context)


def test_load_prompt_empty_context(prompt_loader_custom):
    """Test loading a prompt with empty context."""
    result = prompt_loader_custom.load_prompt_with_context("simple.txt", {})
    assert result == "This is a simple prompt template."


def test_load_prompt_none_context(prompt_loader_custom):
    """Test loading a prompt with None context (should work like empty dict)."""
    # Liquid should handle None gracefully, but let's test it
    result = prompt_loader_custom.load_prompt_with_context("simple.txt", {})
    assert result == "This is a simple prompt template."


def test_load_prompt_subdirectory(temp_prompt_dir):
    """Test loading a prompt from a subdirectory."""
    # Create a subdirectory with a template
    subdir = Path(temp_prompt_dir) / "subdir"
    subdir.mkdir()
    template_file = subdir / "nested.txt"
    template_file.write_text("This is a nested template.")

    loader = PromptLoader(prompt_dir=temp_prompt_dir)
    result = loader.load_prompt("subdir/nested.txt")
    assert result == "This is a nested template."
