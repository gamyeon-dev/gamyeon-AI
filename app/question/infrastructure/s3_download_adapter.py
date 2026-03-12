import httpx
import logging
from app.question.application.port.s3_download_port import S3DownloadPort
from app.core.config import settings

logger = logging.getLogger(__name__)

class S3DownloadAdapter(S3DownloadPort):
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    async def download(self, url: str) -> bytes:
        """
        Spring으로부터 받은 Presigned URL을 통해 파일을 다운로드합니다.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"S3 파일 다운로드 시작: {url[:50]}...")
                
                response = await client.get(url)
                
                # HTTP 에러(403 Forbidden, 404 Not Found 등) 발생 시 예외 발생
                response.raise_for_status()
                
                file_data = response.content
                logger.info(f"다운로드 완료: {len(file_data)} bytes 수신")
                
                return file_data

        except httpx.HTTPStatusError as e:
            # 403(만료/권한), 404(파일없음) 등 서버 응답 에러 처리
            logger.error(f"S3 다운로드 실패 (상태 코드: {e.response.status_code}): {e}")
            if e.response.status_code == 403:
                raise ValueError("S3 URL이 만료되었거나 접근 권한이 없습니다.") from e
            raise Exception(f"S3 서버 에러 발생: {e.response.status_code}") from e

        except httpx.RequestError as e:
            # 네트워크 단절, 타임아웃 등 요청 자체 실패 처리
            logger.error(f"S3 연결 중 네트워크 에러 발생: {e}")
            raise Exception("S3 서버에 연결할 수 없습니다. 네트워크 상태를 확인하세요.") from e

        except Exception as e:
            logger.error(f"알 수 없는 오류 발생: {e}")
            raise e

    # def _parse_url(self, url: str) -> tuple[str, str]:
    #     # s3://bucket-name/path/to/file.pdf
    #     path = url.replace("s3://", "")
    #     bucket, key = path.split("/", 1)
    #     return bucket, key
