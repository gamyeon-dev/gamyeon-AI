import asyncio
from app.question.application.port.s3_download_port import S3DownloadPort
from app.question.application.port.pdf_extract_port import PdfExtractPort
from app.question.infrastructure.pymupdf_adapter import MAX_CHARS_RESUME, MAX_CHARS_OTHER
# local file version
class QuestionService:

    def __init__(
        self,
        s3_download_port: S3DownloadPort,
        pdf_extract_port: PdfExtractPort,
    ):
        self.s3_download_port = s3_download_port
        self.pdf_extract_port = pdf_extract_port

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

        # 추출 결과 확인 (임시 반환)
        return [
            f"resume_text: {resume_text[:100]}",
            f"portfolio_text: {portfolio_text[:100] if portfolio_text else 'None'}",
            f"self_intro_text: {self_intro_text[:100] if self_intro_text else 'None'}",
        ]
