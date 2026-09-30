FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias primero (aprovecha capa de cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Streamlit config: escuchar en 0.0.0.0 y puerto que Cloud Run inyecta via $PORT
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD streamlit run 09_web_app_chat/app.py \
    --server.port=${PORT:-8080} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
