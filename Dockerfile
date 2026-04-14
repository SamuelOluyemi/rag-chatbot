# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# COPY ./backend/app ./main
COPY . .
ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
