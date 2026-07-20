FROM python:3.11-slim

# Evitar buffering
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências de sistema (Postgres, compilers)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar o restante do código
COPY . /app/

# Porta padrão que o gunicorn vai escutar
EXPOSE 8000

# Comando de inicialização:
# - aplica migrações
# - coleta estáticos
# - sobe o gunicorn
CMD ["bash", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn setup.wsgi:application --bind 0.0.0.0:8000"]
