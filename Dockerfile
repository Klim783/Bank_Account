
FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

# сначала только файлы зависимостей — чтобы Docker кэшировал этот слой
# и не переустанавливал всё заново при каждом изменении кода
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# теперь весь остальной код
COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]