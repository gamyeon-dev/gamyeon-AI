from app.question.application.port.s3_download_port import S3DownloadPort
from app.question.application.port.pdf_extract_port import PdfExtractPort
from app.question.infrastructure.local_file_adapter import LocalFileAdapter
from app.question.infrastructure.pymupdf_adapter import PyMuPDFAdapter
#local file adapter로 s3 연결전 파일 읽어오는 어댑터로 사용
def get_s3_download_port() -> S3DownloadPort:
    return LocalFileAdapter()

def get_pdf_extract_port() -> PdfExtractPort:
    return PyMuPDFAdapter()


"""   

#원본
from app.question.application.port.s3_download_port import S3DownloadPort
from app.question.infrastructure.s3_download_adapter import S3DownloadAdapter

def get_s3_download_port() -> S3DownloadPort:
    return S3DownloadAdapter()
"""