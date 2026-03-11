SYSTEM_PROMPT = """
당신은 이력서/포트폴리오/자기소개서 텍스트를 분석하여
지정된 JSON 구조로 변환하는 전문가입니다.

규칙:
- 텍스트에 없는 내용은 null 또는 빈 리스트로 채우세요.
- name과 job_role은 반드시 추출하세요.
- career_summary는 지원자의 경력/역량을 공백포함 3문장이하로 요약하세요.
- work_experiences는 각 경력을 한 줄씩 요약하세요.
- projects는 각 프로젝트를 한 줄씩 요약하세요.
- core_competencies는 직군 무관하게 핵심 역량/기술을 추출하세요.
"""

def build_human_prompt(
    resume_text: str,
    job_role: str,
    portfolio_text: str | None = None,
    self_intro_text: str | None = None,
) -> str:
    prompt = f"[이력서]\n{resume_text}\n\n"
    prompt += f"[지원 직군]\n{job_role}\n\n"

    if portfolio_text:
        prompt += f"[포트폴리오]\n{portfolio_text}\n\n"
    if self_intro_text:
        prompt += f"[자기소개서]\n{self_intro_text}\n\n"

    return prompt
