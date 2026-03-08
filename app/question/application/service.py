import asyncio
from app.question.application.port.s3_download_port import S3DownloadPort
from app.question.application.port.pdf_extract_port import PdfExtractPort
from app.question.application.port.structuring_port import StructuringPort
from app.question.domain.interview_input import InterviewInput
from app.question.infrastructure.pymupdf_adapter import MAX_CHARS_RESUME, MAX_CHARS_OTHER

class QuestionService:

    def __init__(
        self,
        s3_download_port: S3DownloadPort,
        pdf_extract_port: PdfExtractPort,
        structuring_port: StructuringPort,
    ):
        self.s3_download_port = s3_download_port
        self.pdf_extract_port = pdf_extract_port
        self.structuring_port = structuring_port

    async def parse_and_generate(
        self,
        resume_url: str,
        job_role: str,
        portfolio_url: str | None = None,
        self_introduction_url: str | None = None,
    ) -> list[str]:

        # [1단계] S3 병렬 다운로드
        resume_bytes, portfolio_bytes, self_intro_bytes = await asyncio.gather(
            self.s3_download_port.download(resume_url),
            self.s3_download_port.download(portfolio_url) if portfolio_url else asyncio.sleep(0, result=None),
            self.s3_download_port.download(self_introduction_url) if self_introduction_url else asyncio.sleep(0, result=None),
        )

        # [2단계] 이력서 텍스트 추출 (필수, 우선)
        resume_text = await self.pdf_extract_port.extract(resume_bytes, max_chars=MAX_CHARS_RESUME)

        # [3단계] 선택 파일 병렬 텍스트 추출
        portfolio_text, self_intro_text = await asyncio.gather(
            self.pdf_extract_port.extract(portfolio_bytes, max_chars=MAX_CHARS_OTHER) if portfolio_bytes else asyncio.sleep(0, result=None),
            self.pdf_extract_port.extract(self_intro_bytes, max_chars=MAX_CHARS_OTHER) if self_intro_bytes else asyncio.sleep(0, result=None),
        )

        # [4단계] LLM 구조화
        interview_input: InterviewInput = await self.structuring_port.structure(
            resume_text=resume_text,
            job_role=job_role,
            portfolio_text=portfolio_text,
            self_intro_text=self_intro_text,
        )

        # 임시 반환 (질문 생성 로직은 다음 단계)
        return [
            f"name: {interview_input.name}",
            f"job_role: {interview_input.job_role}",
            f"core_competencies: {interview_input.core_competencies}",
            f"career_summary: {interview_input.career_summary}",
            f"work_experiences: {interview_input.work_experiences}",
            f"projects: {interview_input.projects}",
        ]
