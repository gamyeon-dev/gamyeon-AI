from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.question.application.port.question_gen_port import QuestionGenPort
from app.question.domain.interview_input import InterviewInput
from app.question.infrastructure.prompts.question_gen_prompt import SYSTEM_PROMPT, build_question_prompt

class LLMQuestionGenAdapter(QuestionGenPort):

    def __init__(self):
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
        ])
        self.chain = prompt | llm | StrOutputParser()

    async def generate(self, interview_input: InterviewInput) -> list[str]:
        result = await self.chain.ainvoke({"input": build_question_prompt(interview_input)})
        questions = [q.strip() for q in result.split("\n") if q.strip()]
        return questions[:4]  # 혹시 4개 초과 시 안전장치
