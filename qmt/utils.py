from datetime import date, datetime
from typing import Any, Iterable, List, Optional, Sequence, Union


def normalize_code(code: str) -> str:
    code = (code or "").strip()
    if not code:
        raise ValueError("code is empty")
    if "." in code:
        return code
    if code.startswith("6"):
        return code + ".SH"
    if code.startswith("0") or code.startswith("3"):
        return code + ".SZ"
    if code.startswith("4") or code.startswith("8"):
        return code + ".BJ"
    return code + ".SZ"


def normalize_codes(codes: Union[str, Sequence[str]]) -> List[str]:
    if isinstance(codes, str):
        return [normalize_code(codes)]
    return [normalize_code(c) for c in list(codes)]


def to_timestr(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.strftime("%Y%m%d%H%M%S")
    if isinstance(value, date):
        return value.strftime("%Y%m%d")
    return value


def ensure_list(value: Optional[Union[str, Iterable[str]]]) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)

