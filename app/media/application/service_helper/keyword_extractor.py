from __future__ import annotations

from media.domain import KeywordResult, KeywordCandidate

class KeywordExtractor:
    """
    IT 기술 용어 키워드 추출 도메인 서비스.

    처리 순서:
    1. corrected_transcript 형태소 분석
    2. IT 기술 용어 화이트리스트 매칭
        (BE / FE / AI / DevOps 카테고리)
    3. 출현 횟수 집계 → 상위 10개 반환
    """

    async def extract(self, text: str) -> KeywordResult:
        """
        Args:
            text: corrected_transcript (S5 교정 완료 텍스트)

        Returns:
            KeywordResult: 상위 10개 후보.
                        추출 실패 시 빈 tuple (호출자에서 처리).
        """
        raise NotImplementedError("이후 구현")
