from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.question.application.port.structuring_port import StructuringPort
from app.question.domain.interview_input import InterviewInput
from app.question.infrastructure.prompts.structuring_prompt import SYSTEM_PROMPT, build_human_prompt

class LLMStructuringAdapter(StructuringPort):

    def __init__(self):
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        self.chain = llm.with_structured_output(InterviewInput)

    async def structure(
        self,
        resume_text: str,
        job_role: str,
        portfolio_text: str | None = None,
        self_intro_text: str | None = None,
    ) -> InterviewInput:
        human_prompt = build_human_prompt(resume_text, job_role, portfolio_text, self_intro_text)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
        ])
        chain = prompt | self.chain
        return await chain.ainvoke({"input": human_prompt})
