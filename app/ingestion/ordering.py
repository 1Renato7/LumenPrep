"""TASK-ING-004. Watermark (tolerância de late 2m) + terminal-state guard."""

from datetime import datetime, timedelta

TERMINAL_STATUSES = {"SUCCEEDED", "DECLINED", "ERROR", "TIMEOUT", "CANCELLED"}
LATE_TOLERANCE = timedelta(minutes=2)


def is_terminal(status: str) -> bool:
    return status in TERMINAL_STATUSES


def should_apply(con, attempt_id: str, new_event_time: datetime) -> tuple[bool, bool]:
    """Retorna (aplicar_como_estado_atual, is_late).

    Terminal-state guard: não sobrescreve attempt já em status terminal (nunca late, é bloqueio).
    Forward progress (new_event_time >= atual): aplica, não é late.
    Late dentro de 2m: nunca vira estado atual (evitaria regressão pra dado mais velho),
      mas marca is_late — AGG conta como revisão de janela.
    Late fora de 2m: não aplica e não conta revisão — só fica no log.
    """
    row = con.execute(
        "SELECT status, event_time FROM canonical_attempts WHERE attempt_id = ?", [attempt_id]
    ).fetchone()
    if row is None:
        return True, False

    current_status, current_event_time = row
    if is_terminal(current_status):
        return False, False

    if new_event_time >= current_event_time:
        return True, False

    within_tolerance = (current_event_time - new_event_time) <= LATE_TOLERANCE
    return False, within_tolerance
