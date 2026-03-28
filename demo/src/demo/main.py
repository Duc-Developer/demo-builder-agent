#!/usr/bin/env python
import sys
import warnings

from datetime import datetime
from pathlib import Path
import shutil

from dotenv import load_dotenv

from demo.crew import Demo

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")


def _prompt_topic() -> str:
    topic = input("Enter topic: ").strip()
    if not topic:
        raise ValueError("Topic is required.")
    return topic


def _build_inputs(topic: str) -> dict[str, str]:
    return {
        "topic": topic,
        "current_year": str(datetime.now().year),
    }


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _extract_frontend_app() -> None:
    output_dir = _project_root() / "outputs"
    source_manifest = output_dir / "app" / "APP_SOURCE.txt"

    if not source_manifest.exists():
        return

    app_dir = output_dir / "app"
    if app_dir.exists():
        for child in app_dir.iterdir():
            if child.name == source_manifest.name:
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    current_file: Path | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal current_file, buffer
        if current_file is None:
            return
        current_file.parent.mkdir(parents=True, exist_ok=True)
        current_file.write_text("".join(buffer).lstrip("\n"), encoding="utf-8")
        current_file = None
        buffer = []

    for line in source_manifest.read_text(encoding="utf-8").splitlines(keepends=True):
        if line.startswith("FILE: "):
            flush()
            relative_path = line.removeprefix("FILE: ").strip()
            if not relative_path:
                continue
            current_file = app_dir / relative_path
            continue
        if current_file is not None:
            buffer.append(line)

    flush()


def _run_and_materialize(inputs: dict[str, str]) -> None:
    Demo().crew().kickoff(inputs=inputs)
    _extract_frontend_app()

def run():
    """Run the crew."""
    inputs = _build_inputs(_prompt_topic())

    try:
        _run_and_materialize(inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """Train the crew for a given number of iterations."""
    inputs = _build_inputs(_prompt_topic())
    try:
        Demo().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
        _extract_frontend_app()

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """Replay the crew execution from a specific task."""
    try:
        Demo().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """Test the crew execution and returns the results."""
    inputs = _build_inputs(_prompt_topic())

    try:
        Demo().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)
        _extract_frontend_app()

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger():
    """Run the crew with trigger payload."""
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        **_build_inputs(trigger_payload.get("topic", "").strip() or _prompt_topic()),
    }

    try:
        _run_and_materialize(inputs)
        return None
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
