FROM python:3.12-slim
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd --system app && \
    useradd --system --gid app --no-create-home app

WORKDIR /app

COPY services/product-service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app services/product-service/app/ ./app/
COPY --chown=app:app shared/ ./shared/

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
