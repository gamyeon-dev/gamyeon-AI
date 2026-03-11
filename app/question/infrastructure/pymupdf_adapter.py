import fitz
from app.question.application.port.pdf_extract_port import PdfExtractPort

MAX_CHARS_RESUME = 3000
MAX_CHARS_OTHER = 2000

class PyMuPDFAdapter(PdfExtractPort):

    async def extract(self, file_bytes: bytes, max_chars: int = MAX_CHARS_RESUME) -> str:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "\n".join([page.get_text() for page in doc])
        doc.close()

        if not text.strip():
            raise ValueError("텍스트 추출 실패: 스캔본 PDF이거나 텍스트가 없습니다.")

        return text[:max_chars]
