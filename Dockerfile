FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml ./
RUN poetry install --no-root --only main

COPY src/ ./src/

EXPOSE 1337

CMD ["python", "src/server.py"]
