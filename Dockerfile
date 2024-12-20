FROM python:3.12-slim

COPY pyproject.toml poetry.lock alembic.ini /
COPY /app /app
COPY /tests /tests

RUN pip install poetry

ARG ENV=production

ENV ENV=${ENV}
ENV PATH="/app/.venv/bin:$PATH"


RUN if [ "$ENV" = "production" ]; then \
        poetry config virtualenvs.in-project true && poetry install --only main --no-root; \
    else \
        poetry config virtualenvs.in-project true && poetry install --all-extras --no-root; \
    fi

EXPOSE 8000

CMD if [ "$ENV" = "production" ]; then \
        poetry run uvicorn app.main_app:app --host 0.0.0.0 --port 8000; \
    else \
        poetry run uvicorn app.main_app:app --host 0.0.0.0 --port 8000 --reload; \
    fi