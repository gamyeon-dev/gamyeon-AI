from abc import ABC, abstractmethod

from media.domain import STTResult

class STTPort(ABC) :
    """
    STT 아웃바운드 포트.

    책임:
      WAV 파일 → STTResult 변환.
      OOM fallback 정책은 어댑터 내부에서 처리.
        large-v3 실패 → medium 1회 재시도.
        medium도 실패 → STTTranscriptionError 발생.

    구현체: infrastructure/whisper_stt_adapter.py
    """

    @abstractmethod
    async def transcribe(
        self,
        audio_path: str,
        tech_stack: list[str],
    ) -> STTResult :
        """
        WAV 파일을 텍스트로 변환.

        Args:
            audio_path: 로컬 WAV 파일 경로 (/tmp/{jobId}/audio.wav)
            tech_stack: initial_prompt 구성용 기술 스택

        Returns:
            STTResult (raw_transcript, word_timestamps,
            language_probability, stt_model_used)

        Raises:
            STTTranscriptionError: large-v3 + medium fallback 모두 실패 시.
            service.py에서 FAILED 처리.
        """
        ...