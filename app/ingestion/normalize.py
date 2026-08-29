"""TASK-ING-002. Normaliza status/method/decline; garante defaults dos campos opcionais do CTR-EVT-001."""

_OPTIONAL_DEFAULTS = {
    "card": None,
    "decline": None,
    "provider_connection_id": None,
    "payment_method_type": None,
    "raw_event_id": None,
    "normalization_version": "1.0",
}

_UPPER_FIELDS = ("status", "event_type", "payment_method_category", "country", "currency")


def normalize(payload: dict) -> dict:
    normalized = dict(payload)
    for key, default in _OPTIONAL_DEFAULTS.items():
        normalized.setdefault(key, default)
    for field in _UPPER_FIELDS:
        value = normalized.get(field)
        if isinstance(value, str):
            normalized[field] = value.upper()
    decline = normalized.get("decline")
    if isinstance(decline, dict):
        for field in ("category", "retryability"):
            if isinstance(decline.get(field), str):
                decline[field] = decline[field].upper()
    return normalized
