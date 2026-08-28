import hashlib


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
