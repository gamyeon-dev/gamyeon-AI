from app.question.application.port.s3_download_port import S3DownloadPort
from app.question.application.port.pdf_extract_port import PdfExtractPort
from app.question.application.port.structuring_port import StructuringPort
from app.question.infrastructure.local_file_adapter import LocalFileAdapter
from app.question.infrastructure.pymupdf_adapter import PyMuPDFAdapter
from app.question.infrastructure.llm_structuring_adapter import LLMStructuringAdapter

def get_s3_download_port() -> S3DownloadPort:
    return LocalFileAdapter()

def get_pdf_extract_port() -> PdfExtractPort:
    return PyMuPDFAdapter()

def get_structuring_port() -> StructuringPort:
    return LLMStructuringAdapter()



"""   

#원본
from app.question.application.port.s3_download_port import S3DownloadPort
from app.question.infrastructure.s3_download_adapter import S3DownloadAdapter

def get_s3_download_port() -> S3DownloadPort:
    return S3DownloadAdapter()
"""