# Використовуємо базовий образ Python 3.10 slim
FROM python:3.10-slim

# Встановлюємо робочий каталог у контейнері
WORKDIR /app

# Копіюємо всі файли проекту в контейнер
COPY . /app

# Оновлюємо пакетний менеджер і встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean

# Оновлюємо pip
RUN pip install --no-cache-dir --upgrade pip

# Встановлюємо залежності з requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Відкриваємо порт для API
EXPOSE 8000

# Запускаємо додаток за допомогою Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
