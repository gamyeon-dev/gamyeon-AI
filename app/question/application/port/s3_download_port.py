from abc import ABC, abstractmethod

class S3DownloadPort(ABC):

    @abstractmethod
    async def download(self, url: str) -> bytes:
        """S3 Presigned URL로부터 파일을 다운로드하여 bytes로 반환"""
        pass
