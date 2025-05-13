# Dockerfile
FROM python:3.12

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Указываем переменные окружения (если нужно)
ENV PYTHONUNBUFFERED 1