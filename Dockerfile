FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.in-project true

ARG ENV=production

ENV ENV=${ENV}
ENV PATH="/app/.venv/bin:$PATH"


RUN if [ "$ENV" = "production" ]; then \
        poetry install --only main --no-root; \
    else \
        poetry install --all-extras --no-root; \
    fi

EXPOSE 8000

CMD if [ "$ENV" = "production" ]; then \
        poetry run uvicorn app.handlers.game_session_logger:app --host 0.0.0.0 --port 8000; \
    else \
        poetry run uvicorn app.handlers.game_session_logger:app --host 0.0.0.0 --port 8000 --reload; \
    fi