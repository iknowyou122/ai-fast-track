import json
from typing import Any, Dict

def parse_json(json_str: str) -> Dict[str, Any]:
    """
    Parse a JSON string into a dictionary.
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}

def format_json(data: Any) -> str:
    """
    Format data as a JSON string with indentation.
    """
    return json.dumps(data, indent=2, ensure_ascii=False)
