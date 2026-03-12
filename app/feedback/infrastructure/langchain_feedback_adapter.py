from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from app.feedback.application.port.feedback_port import FeedbackPort
from app.feedback.domain.feedback_model import QuestionFeedback, FeedbackStatus
from app.feedback.schema.request import FeedbackRequest


# ── Structured Output 스키마 ─────────────────────────────────────
class FeedbackOutput(BaseModel):
    logic_score:               int       = Field(description="논리성 점수 (0~100)")
    answer_composition_score:  int       = Field(description="답변구성력 점수 (0~100)")
    characteristic:            str       = Field(description="답변 전반적 특징 (공백 포함 80자 이내)")
    answer_summary:            str       = Field(description="답변 내용 요약 (1~2문장)")
    strength:                  str       = Field(description="잘한 점 (한 문장, 구체적 근거 포함)")
    improvement:               str       = Field(description="개선점 (한 문장, 구체적 방향 포함)")
    feedback_badges:           list[str] = Field(description="답변 특징 키워드 뱃지 (1~2개)")


# ── 프롬프트 ────────────────────────────────────────────────────
SYSTEM_PROMPT = """당신은 IT 직군 면접 답변 평가 전문가입니다.
주어진 질문과 답변을 분석하여 아래 기준에 따라 항목별로 평가하세요.

[평가 기준]

1. logic_score (0~100)
   - 주장과 이유가 명확하게 연결되어 있는가
   - 무엇을 어떻게 처리했는지 구체적으로 서술했는가
   - 수치(숫자, 퍼센트, 기간 등)가 포함되면 가점

2. answer_composition_score (0~100)
   - PREP 구조(Point → Reason → Example → Point) 포함 여부
   - 구조가 완전할수록 높은 점수

3. characteristic
   - 답변의 전반적 특징을 한~두 문장으로 요약
   - 공백 포함 반드시 80자 이내

4. answer_summary
   - 답변 핵심 내용을 1~2문장으로 요약

5. strength
   - 가장 잘한 점을 구체적 근거와 함께 한 문장으로 서술

6. improvement
   - 가장 중요한 개선점을 구체적 방향과 함께 한 문장으로 서술

7. feedback_badges
   - 답변을 대표하는 짧은 키워드 뱃지 1~2개
   - 예시: "수치 근거 활용", "PREP 구조 미흡", "경험 기반 답변"

{format_instructions}"""

HUMAN_PROMPT = """[직군]: {job_role}
[질문]: {question_text}
[답변]: {corrected_transcript}"""


# ── Adapter ─────────────────────────────────────────────────────
class LangchainFeedbackAdapter(FeedbackPort):

    # 사전 차단 기준값
    MIN_TRANSCRIPT_LENGTH = 10
    MIN_RELIABILITY_SCORE = 50

    def __init__(self, llm: ChatOpenAI) -> None:
        self._parser = PydanticOutputParser(pydantic_object=FeedbackOutput)
        self._prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human",  HUMAN_PROMPT),
        ]).partial(format_instructions=self._parser.get_format_instructions())
        self._chain = self._prompt | llm | self._parser

    # ── 외부 진입점 ──────────────────────────────────────────────
    async def generate_feedback(self, request: FeedbackRequest) -> QuestionFeedback:
        media_scores = self._extract_media_scores(request)

        if self._should_skip(request):
            return QuestionFeedback.skipped(request.intv_question_id)

        try:
            output: FeedbackOutput = await self._invoke_with_retry(request)
            return self._to_domain(output, request, media_scores)

        except Exception:
            return QuestionFeedback.failed(
                intv_question_id = request.intv_question_id,
                **media_scores,
            )

    # ── 사전 차단 ────────────────────────────────────────────────
    def _should_skip(self, request: FeedbackRequest) -> bool:
        return (
            request.degraded
            or len(request.corrected_transcript.strip()) < self.MIN_TRANSCRIPT_LENGTH
            or request.reliability_score < self.MIN_RELIABILITY_SCORE
        )

    # ── LLM 호출 (재시도 1회) ────────────────────────────────────
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def _invoke_with_retry(self, request: FeedbackRequest) -> FeedbackOutput:
        return await self._chain.ainvoke({
            "job_role":             request.job_role,
            "question_text":        request.question_text,
            "corrected_transcript": request.corrected_transcript,
        })

    # ── media 수치 추출 ──────────────────────────────────────────
    @staticmethod
    def _extract_media_scores(request: FeedbackRequest) -> dict:
        return {
            "gaze_score":         request.gaze_score,
            "time_score":         request.time_score,
            "answer_duration_ms": request.answer_duration_ms,
            "keyword_count":      len(request.keyword_candidates),
        }

    # ── 도메인 변환 ──────────────────────────────────────────────
    @staticmethod
    def _to_domain(
        output:       FeedbackOutput,
        request:      FeedbackRequest,
        media_scores: dict,
    ) -> QuestionFeedback:
        return QuestionFeedback(
            intv_question_id         = request.intv_question_id,
            status                   = FeedbackStatus.COMPLETED,
            logic_score              = output.logic_score,
            answer_composition_score = output.answer_composition_score,
            characteristic           = output.characteristic,
            answer_summary           = output.answer_summary,
            strength                 = output.strength,
            improvement              = output.improvement,
            feedback_badges          = output.feedback_badges,
            **media_scores,
        )
