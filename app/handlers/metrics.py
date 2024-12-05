from prometheus_client import Counter, Gauge

SESSIONS_CREATED = Counter("sessions_created_total", "Total number of created sessions")
