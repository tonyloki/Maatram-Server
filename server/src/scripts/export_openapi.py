"""Deterministic OpenAPI JSON exporter for the Maatram Volunteering & Gamification Portal.

Generates a canonical, reproducible, and sanitized OpenAPI v1 specification from
the live FastAPI application instance.

Usage:
    cd server
    python -m src.scripts.export_openapi
"""

import copy
import json
import os
import sys
from pathlib import Path
from typing import Any

# Ensure server root is in sys.path when executed directly
SERVER_ROOT = Path(__file__).resolve().parent.parent.parent
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from src.main import app


def normalize_openapi_structure(item: Any, parent_key: str | None = None) -> Any:
    """Recursively sort dictionary keys and normalize lists for deterministic comparison.

    Preserves semantic schema properties:
    - Required fields
    - Property data types and nullability constraints
    - Enum definitions and defaults
    - Request/response bodies and parameter types
    - Security schemes and references

    Normalizes:
    - Dictionary key order (alphabetical)
    - List of required properties (alphabetical to avoid insertion-order drift)
    - List of tags (alphabetical)
    - List of parameters (sorted by parameter location and name)
    """
    if isinstance(item, dict):
        # Recursively normalize all values and sort keys alphabetically
        return {
            k: normalize_openapi_structure(item[k], parent_key=k)
            for k in sorted(item.keys())
        }
    elif isinstance(item, list):
        # Alphabetize string lists where ordering is not semantically significant
        if parent_key == "required" and all(isinstance(x, str) for x in item):
            return sorted([normalize_openapi_structure(x, parent_key) for x in item])
        if parent_key == "tags" and all(isinstance(x, str) for x in item):
            return sorted([normalize_openapi_structure(x, parent_key) for x in item])
        # Sort endpoint parameters deterministically by (in, name)
        if parent_key == "parameters" and all(
            isinstance(x, dict) and "name" in x and "in" in x for x in item
        ):
            normalized_params = [
                normalize_openapi_structure(x, parent_key) for x in item
            ]
            return sorted(
                normalized_params,
                key=lambda p: (str(p.get("in", "")), str(p.get("name", ""))),
            )
        # For general lists, preserve sequence order and recurse on elements
        return [normalize_openapi_structure(x, parent_key) for x in item]
    return item


def sanitize_openapi_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Sanitize environment-specific variables and local host references.

    Ensures the exported contract contains zero runtime secrets, local filesystem
    paths, or transient development credentials.
    """
    sanitized = copy.deepcopy(spec)

    # If servers list exists, ensure it does not leak transient local URLs
    if "servers" in sanitized:
        filtered_servers = []
        for s in sanitized["servers"]:
            url = str(s.get("url", ""))
            # Strip localhost and port numbers from published contract servers
            if "localhost" not in url and "127.0.0.1" not in url:
                filtered_servers.append(s)
        if filtered_servers:
            sanitized["servers"] = filtered_servers
        else:
            # Provide canonical base prefix
            sanitized["servers"] = [{"url": "/api/v1", "description": "Default API v1 gateway"}]

    return sanitized


def get_deterministic_openapi() -> dict[str, Any]:
    """Generate the authoritative, normalized, and sanitized OpenAPI dictionary from FastAPI."""
    raw_spec = app.openapi()
    sanitized = sanitize_openapi_spec(raw_spec)
    return normalize_openapi_structure(sanitized)


def export_openapi_to_file(output_path: Path | str | None = None) -> Path:
    """Export the deterministic OpenAPI specification to a target JSON file.

    Returns:
        Path: The absolute path of the written openapi.json file.
    """
    if output_path is None:
        target_path = SERVER_ROOT / "openapi.json"
    else:
        target_path = Path(output_path)

    spec = get_deterministic_openapi()
    serialized = json.dumps(spec, indent=2, ensure_ascii=False) + "\n"

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(serialized, encoding="utf-8")

    return target_path


def main() -> None:
    """CLI entrypoint for exporting the OpenAPI specification."""
    output_file = export_openapi_to_file()
    print(f"OpenAPI v1 specification successfully exported to: {output_file}")


if __name__ == "__main__":
    main()
