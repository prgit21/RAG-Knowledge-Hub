FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app
ENV PYTHONUNBUFFERED=1

# Do not hardcode secrets in Dockerfile. Use build args or environment variables at runtime

# You can pass the JWT_SECRET when running the container:
# docker run -e JWT_SECRET=your_jwt_secret_here ...

# Or use a .env file with docker-compose:
# environment:
#   - JWT_SECRET=${JWT_SECRET}
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
