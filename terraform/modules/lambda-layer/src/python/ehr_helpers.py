import hashlib
import re

# FHIR's id format: letters, digits, "-" and ".", up to 64 characters
FHIR_ID = r"[A-Za-z0-9\-.]{1,64}"


def parse_groups(event):
    auth = event.get("requestContext", {}).get("authorizer", {})
    claims = auth.get("jwt", {}).get("claims") or auth.get("claims", {})
    raw_groups = claims.get("cognito:groups", "")
    if isinstance(raw_groups, str):
        cognito_groups = raw_groups.strip("[]").split()
    else:
        cognito_groups = raw_groups
    return cognito_groups


def salted_hash(value, salt):
    return hashlib.sha256((value + salt).encode()).hexdigest()


def follow(value, path):
    # Follows path through dicts and lists, e.g. ("type", 0, "text"); None if a step is missing
    for key in path:
        try:
            value = value[key]
        except (KeyError, IndexError, TypeError):
            return None
    return value


def get_field(value, *path, kind=str):
    # The value at path, e.g. get_field(event, "type", 0, "text").
    # None if a step is missing, the wrong shape, or the end isn't a non-empty `kind`.
    value = follow(value, path)
    return value if isinstance(value, kind) and value else None


def supplied(value, *path):
    # Whether the request sent anything other than null at path, in any shape
    return follow(value, path) is not None


def fhir_id(value):
    return value if isinstance(value, str) and re.fullmatch(FHIR_ID, value) else None


def sort_key(value, prefix):
    # As the write handlers build it, e.g. "ENCOUNTER#2026-07-14T09:30:00Z#enc-uk-0001"
    if isinstance(value, str) and re.fullmatch(rf"{prefix}#.+#{FHIR_ID}", value):
        return value
    return None


def coding(value):
    # A Coding such as an Encounter's class, with all three parts as strings
    parts = {part: get_field(value, part) for part in ("system", "code", "display")}
    return parts if None not in parts.values() else None


def reference_id(reference, resource_type):
    # Only the relative form, e.g. {"reference": "Patient/pat-uk-200"} -> "pat-uk-200"
    match = re.fullmatch(
        rf"{resource_type}/({FHIR_ID})", get_field(reference, "reference") or ""
    )
    return match[1] if match else None
