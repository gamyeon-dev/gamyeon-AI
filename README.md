```
# 가면 (Gamyeon) — AI 모의 면접 시뮬레이터

AI와 함께하는 실전형 면접 연습 플랫폼입니다.
이력서 기반 맞춤형 질문 생성부터 답변 피드백까지, 면접의 전 과정을 시뮬레이션합니다.

---

## 서비스 소개

취업 준비생이 실제 면접과 유사한 환경에서 연습할 수 있도록
AI가 면접관 역할을 수행합니다.

- 업로드한 이력서와 직군을 분석하여 맞춤형 면접 질문을 생성합니다.
- 음성으로 답변하면 STT가 텍스트로 변환하고, LLM이 피드백을 제공합니다.
- 면접 이력을 대시보드로 관리하고 성장 과정을 확인할 수 있습니다.

---

## 주요 기능

  AI 면접 질문 생성
  - 이력서(필수) / 포트폴리오(선택) 기반 맞춤형 질문 생성
  - 공용 질문 + AI 생성 질문 혼합 출제 (최대 7문항)

  음성 답변 처리
  - 음성 답변을 Whisper STT△ 로 텍스트 변환
  - 한국어 / 영어 혼용 답변 지원

  답변 피드백
  - 면접 종료 후 전체 답변 일괄 평가
  - 특징 / 잘한 점 / 개선점 항목별 제공

  시선 처리 해석
  - 면접 중 시선 데이터 수집 및 집중도 분석

  면접 이력 관리
  - 대시보드에서 과거 면접 기록 조회
  - 회차별 피드백 열람

---

## 기술 스택

  Backend (Spring)
  - Java / Spring Boot
  - Spring Security + JWT
  - Spring Cloud Gateway
  - JPA / PostgreSQL
  - Gradle Multi Module
  - DDD + Half Hexagonal Architecture

  AI Server (Python)
  - Python / FastAPI
  - LangChain
  - OpenAI GPT-4o / Whisper
  - UV (패키지 관리)
  - Half Hexagonal Architecture

  Storage
  - PostgreSQL (사용자 / 세션 / 질문 데이터)
  - NoSQL (면접 피드백 보고서)
  - AWS S3 (파일 저장)

  Infra
  - GitHub Actions (CI/CD)
  - Docker

---

## 시스템 아키텍처

  [클라이언트]
       |
  [API Gateway]          인증 / 라우팅 / Rate Limit
       |
  ┌────┴────────────────────────┐
  |                             |
  [Spring 서버]             [Backoffice 서버]
  Gradle Multi Module        관리자 기능
  ├── user
  ├── interview
  ├── evaluation
  └── notification
       |
       | REST
       |
  [Python AI 서버]         FastAPI + LangChain
  ├── question/            면접 질문 생성
  ├── evaluation/          답변 평가
  ├── feedback/            종합 피드백
  ├── stt/                 음성 → 텍스트
  ├── resume/              이력서 파싱
  └── agent/               2차 MVP 예정

---

## 프로젝트 구조

---

## 개발 로드맵

  1차 MVP (진행 중)
  - 이력서 기반 AI 질문 생성
  - 음성 답변 STT 변환
  - 답변 피드백 생성
  - 면접 이력 대시보드
  - 시선 처리 해석


---

## 로컬 실행 방법

  Spring 서버

    git clone https://github.com/your-org/gamyeon.git
    cd gamyeon
    ./gradlew bootRun

  Python AI 서버
  PS C:\Users\user\Documents\GitHub\gamyeon-AI> uv run uvicorn app.main:app --reload


  환경변수 (.env)

    OPENAI_API_KEY=your-openai-api-key
    ENVIRONMENT=development

---

```