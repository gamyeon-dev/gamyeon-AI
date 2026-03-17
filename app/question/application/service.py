from app.question.application.port.s3_download_port import S3DownloadPort
from app.question.application.port.pdf_extract_port import PdfExtractPort
from app.question.application.port.structuring_port import StructuringPort
from app.question.application.port.question_gen_port import QuestionGenPort
from app.question.application.port.callback_port import CallbackPort
from app.question.schema.request import QuestionGenerateRequest
from app.question.schema.response import QuestionCallbackPayload


class QuestionService:

    def __init__(
        self,
        s3_download_port:  S3DownloadPort,
        pdf_extract_port:  PdfExtractPort,
        structuring_port:  StructuringPort,
        question_gen_port: QuestionGenPort,
        callback_port:     CallbackPort,
    ) -> None:
        self._s3       = s3_download_port
        self._pdf      = pdf_extract_port
        self._struct   = structuring_port
        self._qgen     = question_gen_port
        self._callback = callback_port

    async def run(self, request: QuestionGenerateRequest) -> None:
        try:
            # 1. 파일 키 추출
            resume_key = request.get_file_key("RESUME")
            if not resume_key:
                # 이력서는 필수라고 가정
                raise ValueError("RESUME file not found in request.files")

            portfolio_key      = request.get_file_key("PORTFOLIO")
            self_intro_key     = request.get_file_key("SELF_INTRODUCTION")

            # 2. S3 다운로드 (이력서 필수, 나머지는 선택)
            resume_path        = await self._s3.download(resume_key)

            portfolio_path     = (
                await self._s3.download(portfolio_key)
                if portfolio_key
                else None
            )
            self_intro_path    = (
                await self._s3.download(self_intro_key)
                if self_intro_key
                else None
            )

            # 3. PDF 텍스트 추출
            resume_text        = await self._pdf.extract(resume_path)
            portfolio_text     = (
                await self._pdf.extract(portfolio_path)
                if portfolio_path
                else None
            )
            self_intro_text    = (
                await self._pdf.extract(self_intro_path)
                if self_intro_path
                else None
            )

            # 4. LLM 구조화 (포트폴리오/자소서는 선택적으로 전달)
            interview          = await self._struct.structure(
                resume_text=     resume_text,
                job_role=        None,              # 현재 요청에는 job_role 없음
                portfolio_text=  portfolio_text,
                self_intro_text= self_intro_text,
            )

            # 5. 질문 생성
            questions          = await self._qgen.generate(interview)

            # 6. 성공 콜백 페이로드
            payload = QuestionCallbackPayload(
                intvId=       request.intvId,
                status=       "SUCCESS",
                questions=    questions,
                errorMessage= None,
            )

        except Exception as e:
            # 7. 실패 콜백 페이로드
            payload = QuestionCallbackPayload(
                intvId=       request.intvId,
                status=       "FAILED",
                questions=    [],
                errorMessage= str(e),
            )

        # 8. Webhook 전송
        await self._callback.send(
            url=request.callback,
            payload=payload,
        )
