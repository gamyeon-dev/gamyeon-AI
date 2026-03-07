
"""
    s3 연결전 로컬로 파일을 읽어오는 어댑터
    

 """
from random import sample

from app.question.application.port.s3_download_port import S3DownloadPort

class LocalFileAdapter(S3DownloadPort):

    async def download(self, url: str ) -> bytes:
        with open(url, "rb") as f:
            return f.read()
