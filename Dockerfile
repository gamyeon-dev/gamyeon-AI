FROM python:3.12-slim
WORKDIR /app
# 의존성 캐시 활용으로 빠른 빌드 UX 구현
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]