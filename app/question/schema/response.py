from pydantic import BaseModel

class QuestionGenerateResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True, # 💡 핵심: 출력할 때 무조건 alias(camelCase)로 변환해라!
    )
    
    questions: list[str]
