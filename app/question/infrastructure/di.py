from langchain_openai import ChatOpenAI

from app.question.application.port.s3_download_port import S3DownloadPort
from app.question.application.port.pdf_extract_port import PdfExtractPort
from app.question.application.port.structuring_port import StructuringPort
from app.question.application.port.question_gen_port import QuestionGenPort

from app.question.infrastructure.local_file_adapter import LocalFileAdapter
from app.question.infrastructure.pymupdf_adapter import PyMuPDFAdapter
from app.question.infrastructure.llm_structuring_adapter import LLMStructuringAdapter
from app.question.infrastructure.llm_question_gen_adapter import LLMQuestionGenAdapter
from app.question.infrastructure.structuring_prompt_provider import StructuringPromptProvider
from app.question.infrastructure.question_gen_prompt_provider import QuestionGenPromptProvider


def get_s3_download_port() -> S3DownloadPort:
    return LocalFileAdapter()

    # ↓ AWS 키 수령 후 교체
    # from app.question.infrastructure.s3_download_adapter import S3DownloadAdapter
    # return S3DownloadAdapter()


def get_pdf_extract_port() -> PdfExtractPort:
    return PyMuPDFAdapter()


def get_structuring_port() -> StructuringPort:
    llm             = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    prompt_provider = StructuringPromptProvider(version="v1")
    return LLMStructuringAdapter(llm=llm, prompt_provider=prompt_provider)


def get_question_gen_port() -> QuestionGenPort:
    llm             = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)
    prompt_provider = QuestionGenPromptProvider(version="v1")
    return LLMQuestionGenAdapter(llm=llm, prompt_provider=prompt_provider)
