#!/usr/bin/env python3
"""Validate every content/ instance against its JSON schema (PR 1A content layer).

Dependency-free on purpose: scripts/qa/requirements.txt stays untouched, so this
runs in CI and locally with the stdlib only. The supported schema subset is
exactly what content/schemas/*.json uses: type (including type unions),
required, properties, additionalProperties (false or a subschema), items,
enum, pattern, minLength, minProperties, minItems and minimum.

Every *.json file under content/ (except content/schemas/) must match exactly
one mapping below, and every schema must be used by a mapping: content can
never land without a gate, and a schema can never go stale-unwired.

Usage: python3 scripts/qa/check_content_schemas.py   (exit 1 on any violation)
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHEMA_DIR = os.path.join(ROOT, "content", "schemas")

# (glob relative to repo root, schema name, items key or None)
# items key: the file is {"schema": N, "<key>": [ ... ]} and each element of
# that array is validated against the schema.
MAPPINGS = [
    ("content/rosary/episodes.json", "daily-video", "episodes"),
    ("content/prayers/*.json", "prayer-page", None),
    ("content/products/*.json", "product", None),
    ("content/language-pages/*.json", "language-page", None),
]

TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "boolean": lambda v: isinstance(v, bool),
    # bool is an int subclass in Python; JSON Schema says a boolean is never an integer.
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "null": lambda v: v is None,
}


def validate(value, schema, path, errors):
    """Append human-readable violations for value against schema to errors."""
    expected = schema.get("type")
    if expected is not None:
        types = expected if isinstance(expected, list) else [expected]
        unknown = [t for t in types if t not in TYPE_CHECKS]
        if unknown:
            errors.append(f"{path}: schema uses unsupported type(s) {unknown}")
            return
        if not any(TYPE_CHECKS[t](value) for t in types):
            errors.append(f"{path}: expected type {' or '.join(types)}, got {json.dumps(value)[:80]}")
            return

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {json.dumps(value)[:80]} not in enum {schema['enum']}")
        return

    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match pattern {schema['pattern']!r}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: longer than maxLength {schema['maxLength']}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} below minimum {schema['minimum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for i, item in enumerate(value):
                validate(item, item_schema, f"{path}[{i}]", errors)

    if isinstance(value, dict):
        if "minProperties" in schema and len(value) < schema["minProperties"]:
            errors.append(f"{path}: fewer than minProperties {schema['minProperties']}")
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required key {key!r}")
        props = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            child = f"{path}.{key}" if path else key
            if key in props:
                validate(item, props[key], child, errors)
            elif additional is False:
                errors.append(f"{path}: unexpected key {key!r}")
            elif isinstance(additional, dict):
                validate(item, additional, child, errors)


def load_schema(name):
    with open(os.path.join(SCHEMA_DIR, f"{name}.schema.json"), encoding="utf-8") as fh:
        return json.load(fh)


def check_file(path, schema, items_key):
    """Validate one instance file; return a list of violation strings."""
    rel = os.path.relpath(path, ROOT)
    errors = []
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{rel}: unreadable JSON ({exc})"]
    if items_key is None:
        validate(data, schema, rel, errors)
        return errors
    if not isinstance(data, dict) or not isinstance(data.get(items_key), list):
        return [f"{rel}: expected an object with a {items_key!r} array"]
    for i, item in enumerate(data[items_key]):
        validate(item, schema, f"{rel}: {items_key}[{i}]", errors)
    return errors


def run():
    errors = []
    used_schemas = set()
    covered = []
    for pattern, name, items_key in MAPPINGS:
        schema = load_schema(name)
        used_schemas.add(name)
        files = sorted(glob.glob(os.path.join(ROOT, pattern)))
        if not files:
            errors.append(f"{pattern}: mapping matches no files")
        for path in files:
            covered.append(os.path.normpath(path))
            errors.extend(check_file(path, schema, items_key))

    # Coverage is enforced inside the directories this layer owns. content/books,
    # content/ui and the books-level JSON files already have their own contracts
    # (scripts/books/*, books:check) and migrate in later PRs.
    owned_dirs = sorted({os.path.dirname(os.path.join(ROOT, pat)) for pat, _, _ in MAPPINGS})
    on_disk = set()
    for directory in owned_dirs:
        on_disk.update(
            os.path.normpath(p)
            for p in glob.glob(os.path.join(directory, "**", "*.json"), recursive=True)
        )
    for path in sorted(on_disk - set(covered)):
        errors.append(f"{os.path.relpath(path, ROOT)}: no schema mapping covers this content file")

    for schema_file in sorted(os.listdir(SCHEMA_DIR)):
        name = schema_file[: -len(".schema.json")] if schema_file.endswith(".schema.json") else None
        if name is None:
            errors.append(f"content/schemas/{schema_file}: schema files must be named <type>.schema.json")
        elif name not in used_schemas:
            errors.append(f"content/schemas/{schema_file}: schema is not wired into any mapping")
    return errors


def main():
    errors = run()
    if errors:
        print("content schema validation FAILED:")
        for line in errors:
            print(f"  - {line}")
        return 1
    print("content schema validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
