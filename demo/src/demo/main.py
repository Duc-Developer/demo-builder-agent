#!/usr/bin/env python
import sys
import warnings
import os
import json
import subprocess
import asyncio

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


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"{name} is missing from environment.")
    return value


def _publish_issue(title: str, body: str, labels: list[str]) -> None:
    repo = _require_env("GIT_HUB_REPO")
    token = _require_env("GIT_HUB_TOKEN")
    payload = json.dumps(
        {
            "title": title,
            "body": body,
            "labels": labels,
        }
    )
    subprocess.run(
        [
            "curl",
            "-sS",
            "-X",
            "POST",
            f"https://api.github.com/repos/{repo}/issues",
            "-H",
            "Accept: application/vnd.github+json",
            "-H",
            f"Authorization: Bearer {token}",
            "-H",
            "X-GitHub-Api-Version: 2022-11-28",
            "-d",
            payload,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _publish_agent_outputs(result: object, topic: str) -> None:
    task_output = getattr(result, "tasks_output", None)
    if not task_output:
        return

    raw_output = getattr(task_output[0], "raw", str(task_output[0])).strip() if len(task_output) > 0 else ""
    if raw_output and "Business Analytics" in getattr(task_output[0], "agent", ""):
        _publish_issue(
            title=f"Business Analytics - {topic}",
            body=raw_output,
            labels=["business-analytics", "ai-output"],
        )
    elif raw_output:
        _publish_issue(
            title=f"Manual Tester - {topic}",
            body=raw_output,
            labels=["manual-tester", "ai-output"],
        )


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


async def _run_parallel_crews(inputs: dict[str, str], business_context: str) -> tuple[object, object]:
    demo = Demo()
    parallel_inputs = {
        **inputs,
        "business_analysis": business_context,
    }
    frontend_result, manual_result = await asyncio.gather(
        demo.frontend_developer_crew().kickoff_async(inputs=parallel_inputs),
        demo.manual_tester_crew().kickoff_async(inputs=parallel_inputs),
    )
    return frontend_result, manual_result


def _run_and_materialize(inputs: dict[str, str]) -> None:
    demo = Demo()
    business_result = demo.business_analytics_crew().kickoff(inputs=inputs)
    _publish_issue(
        title=f"Business Analytics - {inputs['topic']}",
        body=str(getattr(business_result, "raw", business_result)).strip(),
        labels=["business-analytics", "ai-output"],
    )
    frontend_result, manual_result = asyncio.run(
        _run_parallel_crews(inputs, str(getattr(business_result, "raw", business_result)).strip())
    )
    _extract_frontend_app()
    _publish_issue(
        title=f"Manual Tester - {inputs['topic']}",
        body=str(getattr(manual_result, "raw", manual_result)).strip(),
        labels=["manual-tester", "ai-output"],
    )

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
