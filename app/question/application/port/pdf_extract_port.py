from abc import ABC, abstractmethod

class PdfExtractPort(ABC):

    @abstractmethod
    async def extract(self, file_bytes: bytes) -> str:
        """PDF bytes에서 텍스트를 추출하여 반환"""
        pass
