from langchain_openai import ChatOpenAI
from enum import Enum

class ModelType(Enum):
    QUESTION_GEN = "question_gen"
    EVALUATION = "evaluation"
    FAST = "fast"

def get_llm(model_type: ModelType):
    match model_type:
        case ModelType.QUESTION_GEN:
            return ChatOpenAI(model="gpt-4o", temperature=0.8)
        case ModelType.EVALUATION:
            return ChatOpenAI(model="gpt-4o", temperature=0.0)
        case ModelType.FAST:
            return ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
