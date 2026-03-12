from pathlib import Path
import yaml


def load_yaml_prompt(file_path: str | Path) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
