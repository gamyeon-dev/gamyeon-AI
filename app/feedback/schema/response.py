from pydantic import BaseModel
from typing import Optional


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True, # 💡 핵심: 출력할 때 무조건 alias(camelCase)로 변환해라!
    )
    
    intv_question_id:          int
    status:                    str
    logic_score:               Optional[int] = None
    answer_composition_score:  Optional[int] = None
    characteristic:            Optional[str] = None
    answer_summary:            Optional[str] = None
    strength:                  Optional[str] = None
    improvement:               Optional[str] = None
    feedback_badges:           list[str]     = []
    gaze_score:                int           = 0
    time_score:                int           = 0
    answer_duration_ms:        int           = 0
    keyword_count:             int           = 0

    model_config = {"use_enum_values": True}
