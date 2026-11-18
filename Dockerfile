# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# COPY ./backend/app ./main
COPY . .
ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "app/main:app", "--host", "0.0.0.0", "--port", "8080"]

# I need to cd into backend, then run docker build -t rag-backend . to build the image, then run docker run -p 8080:8080 rag-backend to start the container.