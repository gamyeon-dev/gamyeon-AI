# 1단계: 빌드 환경 (uv 사용)
FROM python:3.12-slim AS builder

WORKDIR /app
COPY uv.lock pyproject.toml /app/
# 가상환경을 /app/.venv에 생성
RUN uv sync --frozen --no-dev

# 2단계: 실행 환경 (실제 앱 구동)
FROM python:3.12-slim
WORKDIR /app
# 빌드 환경에서 만든 가상환경만 복사
COPY --from=builder /app/.venv /app/.venv
COPY . /app

# 가상환경의 파이썬과 라이브러리를 사용하도록 경로 추가
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]