FROM python:3.12-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

## 1) Кладём requirements внутрь
COPY requirements.txt .

## 2) Отладка: убедиться, что requirements именно тот
RUN echo "===== requirements inside container =====" \
    && pwd \
    && ls -la \
    && cat requirements.txt

## 3) Обновляем pip и ставим зависимости с официального PyPI
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir \
       --index-url https://pypi.org/simple \
       --trusted-host pypi.org \
       --trusted-host files.pythonhosted.org \
       -r requirements.txt

## дальше как было
COPY src ./src
COPY data ./data
COPY docs ./docs

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
