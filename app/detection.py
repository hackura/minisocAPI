from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

FAILED_LOGIN_THRESHOLD = 5
WINDOW_MINUTES = 10
_attempts: dict[str, deque[datetime]] = defaultdict(deque)

def analyze_event(event_type: str, source_ip: str | None) -> tuple[int, str, str | None]:
    if event_type.lower() not in {"failed_login", "login_failed", "authentication_failure"} or not source_ip:
        return 10, "low", None

    now = datetime.now(timezone.utc)
    attempts = _attempts[source_ip]
    attempts.append(now)
    cutoff = now - timedelta(minutes=WINDOW_MINUTES)
    while attempts and attempts[0] < cutoff:
        attempts.popleft()

    if len(attempts) >= FAILED_LOGIN_THRESHOLD:
        return 90, "critical", "T1110"
    if len(attempts) >= 3:
        return 55, "medium", "T1110"
    return 25, "low", None
