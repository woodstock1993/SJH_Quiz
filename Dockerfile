FROM python:3.12-slim

RUN apt update && apt install -y curl

RUN curl -sSL https://install.python-poetry.org | python3 - 

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock .env alembic.ini /app/

RUN poetry install --no-interaction --no-ansi

RUN poetry add --group dev pytest

COPY . /app

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" "--reload "]

