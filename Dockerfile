FROM python:3.12-slim
# 컨테이너에 uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv /bin/uv/
WORKDIR /app
# uv.lock과 pyproject.toml만 먼저 복사하여 의존성 캐시 활용
COPY uv.lock pyproject.toml /app/
# uv sync로 의존성 설치
RUN uv sync --frozen
# 소스 코드 복사
COPY . /app
# 애플리케이션 실행
CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]