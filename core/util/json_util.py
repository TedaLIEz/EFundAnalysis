import json
import re
from typing import Any


def extract_json_from_response(response_text: str) -> dict[Any, Any]:
    """Extract and parse JSON from LLM response.

    Handles various formats:
    - JSON wrapped in markdown code blocks (```json ... ```)
    - JSON wrapped in plain code blocks (``` ... ```)
    - Raw JSON text
    - JSON with newlines and whitespace (formatted JSON)

    Args:
        response_text: Raw response text from LLM

    Returns:
        Parsed JSON as dictionary

    Raises:
        json.JSONDecodeError: If JSON cannot be parsed
        ValueError: If no valid JSON found

    """
    # First, try to extract JSON from markdown code blocks
    # Use a more robust pattern that handles nested braces
    json_str = None

    # Try to find JSON in markdown code blocks
    code_block_match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL)
    if code_block_match:
        json_str = code_block_match.group(1).strip()
    else:
        # Try to find JSON object in the text (look for { ... } with balanced braces)
        # Find the first { and then find the matching }
        start_idx = response_text.find("{")
        if start_idx != -1:
            brace_count = 0
            end_idx = start_idx
            for i in range(start_idx, len(response_text)):
                if response_text[i] == "{":
                    brace_count += 1
                elif response_text[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            if brace_count == 0:
                json_str = response_text[start_idx:end_idx].strip()

    # If still no JSON found, try the entire response text
    if not json_str:
        json_str = response_text.strip()

    # Clean up the JSON string - remove leading/trailing whitespace
    # but preserve newlines within the JSON (they're valid in JSON)
    json_str = json_str.strip()

    # Try to parse the JSON
    try:
        result: dict[Any, Any] = json.loads(json_str)
        return result
    except json.JSONDecodeError as e:
        # Try to provide more helpful error message
        raise json.JSONDecodeError(f"Invalid JSON format. Original error: {e.msg}", e.doc, e.pos) from e
