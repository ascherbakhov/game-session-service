FROM python:3.12

WORKDIR /app

COPY . /app

COPY requirements.txt requirements-dev.txt /app/

ARG ENV=production

RUN pip install --no-cache-dir -r requirements.txt && \
    if [ "$ENV" = "test" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]