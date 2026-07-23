"""
Resident/house code generation.

Per PROJECT_ROADMAP.md Section 6.3:
- Owner code:  "{house_code}-O"
- Tenant code: "{house_code}-T{n}", n auto-incrementing per house

These are only ever called from the registration-approval service, never
from the registration (self-signup) path — codes are server-generated
after Housing Office approval, never client-supplied or pre-verification.
"""


def build_house_code(raw_house_number: str) -> tuple[str, str]:
    """
    Given a raw house number like "B-026", returns (house_code, block).
    house_code = "EHS-B-026", block = "B".

    Raises ValueError if the input doesn't contain a block segment.
    """
    parts = raw_house_number.split("-", maxsplit=1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(
            f'house_number must be in the form "<BLOCK>-<NUMBER>", e.g. "B-026" (got "{raw_house_number}")'
        )
    block, number = parts
    return f"EHS-{block}-{number}", block


def owner_resident_code(house_code: str) -> str:
    return f"{house_code}-O"


def tenant_resident_code(house_code: str, sequence: int) -> str:
    return f"{house_code}-T{sequence}"
