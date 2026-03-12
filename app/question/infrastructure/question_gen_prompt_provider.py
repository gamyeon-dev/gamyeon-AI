from pathlib import Path
from app.core.prompt_loader import load_yaml_prompt

PROMPT_DIR = Path(__file__).parent / "prompts"


class QuestionGenPromptProvider:

    def __init__(self, version: str = "v1") -> None:
        data = load_yaml_prompt(PROMPT_DIR / f"question_gen_{version}.yaml")
        self._system_prompt: str = data["system_prompt"]
        self._human_prompt: str = data["human_prompt"]

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @property
    def human_prompt(self) -> str:
        return self._human_prompt
