FROM python:3.12

WORKDIR /app

COPY . /app

COPY requirements.txt requirements-dev.txt /app/

ARG ENV=production

RUN pip install --no-cache-dir -r requirements.txt && \
    if [ "$ENV" = "test" ] || [ "$ENV" = "dev" ]; then \
        pip install --no-cache-dir -r requirements-dev.txt; \
    fi
EXPOSE 8000

CMD ["uvicorn", "app.handlers.game_session_logger:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]