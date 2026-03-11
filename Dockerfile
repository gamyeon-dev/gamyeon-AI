# 1단계: 빌드 환경 (uv 도구와 파이썬 설치)
FROM python:3.12-slim AS builder

# uv 공식 바이너리 복사
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY uv.lock pyproject.toml /app/
RUN uv sync --frozen --no-dev

# 2단계: 실행 환경 (실제 앱 구동)
FROM python:3.12-slim
WORKDIR /app

# 빌드 환경에서 설치된 가상환경만 가져오기
COPY --from=builder /app/.venv /app/.venv

# 소스 코드 복사 (app 폴더 포함 전체)
COPY . /app

# 가상환경의 파이썬 경로를 시스템 경로에 추가
ENV PATH="/app/.venv/bin:$PATH"

# 실행 (app 폴더 내의 main.py 실행)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]