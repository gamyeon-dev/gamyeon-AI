"""
Python 서버 내부 도메인 이벤트 Signal 정의

blinker Signal 기반 Pub/Sub
도메인 간 직접 import 없이 이벤트로 통신

현재 정의된 Signal:
    media_completed   : media 파이프라인 완료 → feedback 도메인 구독
"""

from blinker import Signal

# media 파이프라인 완료 이벤트
# sender:  "media"
# payload: MediaProcessingResult.to_feedback_event_payload() 반환값
media_completed: Signal = Signal("media.completed")