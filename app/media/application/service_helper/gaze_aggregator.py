from __future__ import annotations

from media.domain import (
    GazeSegment, GazeResult, GazeSummary,
)
from media.domain._shared.normalizer import r2, r3


class GazeAggregator:
    """
    GazeSegment 목록 → GazeResult 집계 도메인 서비스
    세그먼트 0개: gaze_score=None, segment_coverage=0.0
    """

    def aggregate(
        self,
        segments: list[GazeSegment],
        answer_duration_ms: int,
    ) -> GazeResult:
        """
        Args:
            segments:           pop_all() 반환값 (정렬 완료)
            answer_duration_ms: time_score 산출과 동일 기준값

        Returns:
            GazeResult (세그먼트 없으면 is_empty=True)
        """
        if not segments:
            return self._empty_result()

        # 세그먼트 커버리지
        expected = max(1, answer_duration_ms // 10_000)
        coverage = r3(len(segments) / expected)

        # 가중 평균 집중도 (세그먼트 길이 동일 → 단순 평균)
        avg_concentration = r3(
            sum(s.metrics_summary.average_concentration for s in segments)
            / len(segments)
        )

        # 이탈 집계
        away_count     = sum(s.away_count for s in segments)
        away_total_ms  = sum(s.away_duration_ms for s in segments)

        # 전체 프레임 confidence 평균
        all_frames     = [f for s in segments for f in s.raw_data]
        avg_confidence = r2(
            sum(f.confidence for f in all_frames) / len(all_frames)
            if all_frames else 0.0
        )

        summary = GazeSummary(
            avg_concentration=avg_concentration,
            away_count=away_count,
            away_total_ms=away_total_ms,
            segment_coverage=coverage,
            avg_confidence=avg_confidence,
        )

        gaze_score = self._calculate_gaze_score(summary)

        return GazeResult(
            gaze_score=gaze_score,
            summary=summary,
            segments=tuple(segments),
        )

    def _calculate_gaze_score(self, summary: GazeSummary) -> int:
        """
        gaze_score 0~100 산출
        집중도 70% + 커버리지 30% 가중합
        """
        score = int(
            summary.avg_concentration * 70
            + summary.segment_coverage  * 30
        )
        return max(0, min(100, score))

    def _empty_result(self) -> GazeResult:
        """세그먼트 미수신 → Degraded GazeResult"""
        return GazeResult(
            gaze_score=None,
            summary=GazeSummary(
                avg_concentration=0.0,
                away_count=0,
                away_total_ms=0,
                segment_coverage=0.0,
                avg_confidence=0.0,
            ),
            segments=(),
        )