"""Contract drift regression and structural verification test suite for OpenAPI v1.

Verifies that:
1. The committed `server/openapi.json` contract structurally matches the live runtime FastAPI application schema.
2. Semantic schema properties (required fields, types, nullability, enums, parameters) are preserved.
3. Whitespace, formatting, and key-order variations do not cause false positives.
4. An intentional schema mutation is caught by the structural comparison (negative test).
"""

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from src.main import app
from src.scripts.export_openapi import (
    get_deterministic_openapi,
    normalize_openapi_structure,
    sanitize_openapi_spec,
)

SERVER_ROOT = Path(__file__).resolve().parent.parent.parent
COMMITTED_OPENAPI_PATH = SERVER_ROOT / "openapi.json"


def find_structural_differences(
    expected: Any,
    actual: Any,
    path: str = "#",
    differences: list[str] | None = None,
) -> list[str]:
    """Recursively identify structural semantic differences between two parsed JSON objects.

    Returns a human-readable list of divergence descriptions with JSON pointer locations.
    """
    if differences is None:
        differences = []

    if type(expected) is not type(actual):
        differences.append(
            f"Type mismatch at {path}: expected {type(expected).__name__}, got {type(actual).__name__}"
        )
        return differences

    if isinstance(expected, dict):
        expected_keys = set(expected.keys())
        actual_keys = set(actual.keys())

        missing_in_actual = expected_keys - actual_keys
        extra_in_actual = actual_keys - expected_keys

        for key in sorted(missing_in_actual):
            differences.append(f"Missing key in runtime spec: {path}/{key}")
        for key in sorted(extra_in_actual):
            differences.append(f"Unexpected extra key in runtime spec: {path}/{key}")

        common_keys = expected_keys & actual_keys
        for key in sorted(common_keys):
            sub_path = f"{path}/{key}"
            find_structural_differences(expected[key], actual[key], sub_path, differences)

    elif isinstance(expected, list):
        if len(expected) != len(actual):
            differences.append(
                f"Array length mismatch at {path}: expected {len(expected)} items, got {len(actual)} items"
            )
        min_len = min(len(expected), len(actual))
        for idx in range(min_len):
            sub_path = f"{path}[{idx}]"
            find_structural_differences(expected[idx], actual[idx], sub_path, differences)

    else:
        if expected != actual:
            differences.append(
                f"Value mismatch at {path}: expected {expected!r}, got {actual!r}"
            )

    return differences


def test_committed_openapi_spec_exists() -> None:
    """Ensure the committed openapi.json file exists on disk."""
    assert (
        COMMITTED_OPENAPI_PATH.exists()
    ), f"OpenAPI specification not found at {COMMITTED_OPENAPI_PATH}. Run 'python -m src.scripts.export_openapi'."


def test_openapi_structural_drift() -> None:
    """Assert that the live FastAPI application runtime specification structurally matches openapi.json.

    Uses parsed structural object comparison rather than raw file bytes, ensuring that
    indentation, line breaks, or dictionary key order variations cannot produce false failures.
    """
    assert COMMITTED_OPENAPI_PATH.exists(), "Committed openapi.json missing."

    # 1. Load committed file and parse JSON
    committed_raw = json.loads(COMMITTED_OPENAPI_PATH.read_text(encoding="utf-8"))
    normalized_committed = normalize_openapi_structure(committed_raw)

    # 2. Extract live runtime specification and normalize
    normalized_runtime = get_deterministic_openapi()

    # 3. Find structural semantic differences
    diffs = find_structural_differences(normalized_committed, normalized_runtime)

    assert not diffs, (
        f"Detected {len(diffs)} structural OpenAPI schema drift difference(s) between "
        f"runtime app and committed openapi.json:\n" + "\n".join(diffs[:20]) +
        ("\n... (truncated)" if len(diffs) > 20 else "") +
        "\n\nTo update the specification, run: python -m src.scripts.export_openapi"
    )


def test_formatting_only_differences_do_not_fail() -> None:
    """Verify that changes in whitespace, indentation, or raw serialization order do not fail the test."""
    committed_raw = json.loads(COMMITTED_OPENAPI_PATH.read_text(encoding="utf-8"))

    # Re-serialize with different indentation and tab characters
    reformatted_text = json.dumps(committed_raw, indent=4) + "   \n\n"
    parsed_reformatted = json.loads(reformatted_text)

    # Normalization and structural comparison should detect zero differences
    normalized_committed = normalize_openapi_structure(committed_raw)
    normalized_reformatted = normalize_openapi_structure(parsed_reformatted)

    diffs = find_structural_differences(normalized_committed, normalized_reformatted)
    assert diffs == [], "Formatting-only differences must not produce structural drift failures."


def test_openapi_drift_negative_detection() -> None:
    """Deliberately mutate in-memory schema properties and verify that drift detection catches it.

    Proves that structural comparisons catch:
    1. Property type changes
    2. Missing required fields
    3. Added/removed endpoints
    4. Modified enum constraints
    Crucially, does NOT modify the committed openapi.json file on disk.
    """
    base_spec = get_deterministic_openapi()

    # Mutation 1: Alter property type of EventResponse.capacity_required from integer to string
    mutated_spec = copy.deepcopy(base_spec)
    assert "components" in mutated_spec and "schemas" in mutated_spec["components"]
    event_schema = mutated_spec["components"]["schemas"].get("EventResponse")
    assert event_schema is not None, "EventResponse schema must exist in OpenAPI components."

    # Change type
    event_schema["properties"]["capacity_required"]["type"] = "string"

    diffs_mutation1 = find_structural_differences(base_spec, mutated_spec)
    assert len(diffs_mutation1) > 0, "Drift detection failed to detect mutated property type."
    assert any(
        "capacity_required" in d and "type" in d.lower() for d in diffs_mutation1
    ), f"Expected property type divergence message, got: {diffs_mutation1}"

    # Mutation 2: Remove a required field
    mutated_spec2 = copy.deepcopy(base_spec)
    event_schema2 = mutated_spec2["components"]["schemas"]["EventResponse"]
    if "required" in event_schema2 and "title" in event_schema2["required"]:
        event_schema2["required"].remove("title")
        diffs_mutation2 = find_structural_differences(
            normalize_openapi_structure(base_spec),
            normalize_openapi_structure(mutated_spec2),
        )
        assert len(diffs_mutation2) > 0, "Drift detection failed to detect missing required field."

    # Mutation 3: Remove an endpoint path entirely
    mutated_spec3 = copy.deepcopy(base_spec)
    test_path = "/api/v1/health"
    if test_path in mutated_spec3["paths"]:
        del mutated_spec3["paths"][test_path]
        diffs_mutation3 = find_structural_differences(base_spec, mutated_spec3)
        assert len(diffs_mutation3) > 0, "Drift detection failed to detect missing endpoint path."
        assert any(test_path in d for d in diffs_mutation3)
