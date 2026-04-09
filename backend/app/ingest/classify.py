"""Heuristic category / severity from headline text (no LLM)."""

import re

_HIGH_ALERT = re.compile(
    r"hurac[aá]n|hurricane|sismo|terremoto|earthquake|tsunami|"
    r"evacua|emergencia|amenaza|tornado|inundaci[oó]n|flooding",
    re.I,
)
_SAFETY = re.compile(
    r"accidente|choque|crash|muerto|herido|balacera|robo|"
    r"seguridad|polic[ií]a|bomberos|protecci[oó]n civil|"
    r"cocodrilo|bandera roja|oleaje",
    re.I,
)
_INFRA = re.compile(
    r"agua|seapal|apag[oó]n|sin luz|cfe|bache|carretera|"
    r"t[uú]nel|puente ameca|tr[aá]fico|obras",
    re.I,
)
_EVENT = re.compile(
    r"evento|festival|concierto|gala|expo|feria|tour|charity|"
    r"calendario|this weekend|este fin",
    re.I,
)


def classify_headline(title: str) -> tuple[str, str]:
    """Return (category, severity)."""
    t = title or ""
    if _HIGH_ALERT.search(t):
        return "safety", "high"
    if _SAFETY.search(t):
        return "safety", "elevated"
    if _INFRA.search(t):
        return "infrastructure", "normal"
    if _EVENT.search(t):
        return "event", "normal"
    return "general", "normal"


def detect_language_hint(title: str, summary: str | None) -> str | None:
    """Very rough BCP-47 hint for UI (es vs en)."""
    blob = f"{title} {summary or ''}"
    if re.search(r"[áéíóúñü¿¡]", blob, re.I):
        return "es"
    return "en"
