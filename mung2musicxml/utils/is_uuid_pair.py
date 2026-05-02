import re


def is_uuid_pair(s: str) -> bool:
    uuid_pattern = r"[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}"
    full_pattern = f"^{uuid_pattern}_{uuid_pattern}$"
    return re.fullmatch(full_pattern, s) is not None
