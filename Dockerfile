# ---- 1. Build the Vue frontend ------------------------------------------------
FROM node:22-alpine AS web
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
COPY shared/ ../shared/
RUN npm run build

# ---- 2. Flask API + built frontend on one origin ------------------------------
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 FLASK_APP=wsgi.py FLASK_ENV=production
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY shared/ ../shared/
COPY --from=web /app/frontend/dist ../frontend/dist
RUN useradd --create-home appuser && mkdir -p instance/uploads && chown -R appuser /app
USER appuser
EXPOSE 10000
CMD ["sh", "start.sh"]
