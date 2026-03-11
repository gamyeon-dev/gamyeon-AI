SYSTEM_PROMPT = """
당신은 채용 면접관입니다.
지원자의 정보를 바탕으로 맞춤형 면접 질문을 생성하세요.

규칙:
- 반드시 총 4개의 질문을 생성하세요.
- 제공된 정보가 풍부한 영역에 질문을 더 배분하세요.
- 제공되지 않은 항목(없음으로 표시된 항목)은 질문에서 제외하세요.
- 질문은 지원자의 실제 경험에 기반한 구체적인 질문이어야 합니다.
- 질문 번호나 prefix 없이 질문만 한 줄씩 반환하세요.
"""

def build_question_prompt(interview_input) -> str:
    lines = [f"지원 직군: {interview_input.job_role}"]

    if interview_input.core_competencies:
        lines.append(f"핵심 역량: {', '.join(interview_input.core_competencies)}")

    if interview_input.career_summary:
        lines.append(f"경력 요약: {interview_input.career_summary}")

    if interview_input.work_experiences:
        lines.append(f"주요 경력:\n" + "\n".join(interview_input.work_experiences))

    if interview_input.projects:
        lines.append(f"프로젝트:\n" + "\n".join(interview_input.projects))

    if interview_input.portfolio_summary:
        lines.append(f"포트폴리오 요약: {interview_input.portfolio_summary}")

    if interview_input.self_introduction_summary:
        lines.append(f"자기소개서 요약: {interview_input.self_introduction_summary}")

    lines.append("\n위 정보를 바탕으로 맞춤형 면접 질문 4개를 생성하세요.")
    return "\n\n".join(lines)
