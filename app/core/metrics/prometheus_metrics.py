from prometheus_client import Counter

SESSIONS_CREATED = Counter("sessions_created_total", "Total number of created sessions")
