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


def _prompt_us() -> str:
    us = input("Enter US: ").strip()
    if not us:
        raise ValueError("US is required.")
    return us


def _build_inputs(topic: str, us: str) -> dict[str, str]:
    return {
        "topic": topic,
        "us": us,
        "current_year": str(datetime.now().year),
    }


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"{name} is missing from environment.")
    return value


def _github_api(path: str, method: str = "GET", payload: dict | None = None) -> dict | list:
    repo = _require_env("GIT_HUB_REPO")
    token = _require_env("GIT_HUB_TOKEN")
    command = [
        "curl",
        "-sS",
        "-X",
        method,
        f"https://api.github.com/repos/{repo}{path}",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        f"Authorization: Bearer {token}",
        "-H",
        "X-GitHub-Api-Version: 2022-11-28",
    ]
    if payload is not None:
        command.extend(["-d", json.dumps(payload)])
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def _find_issue_by_us_label(us: str, role_label: str) -> dict:
    us_label = f"US:{us}"
    issues = _github_api(f"/issues?state=open&labels={us_label}")
    for issue in issues:
        labels = {label["name"] for label in issue.get("labels", [])}
        if role_label in labels and us_label in labels:
            return issue
    return {}


def _update_issue_by_us_label(us: str, role_label: str, title: str, body: str) -> None:
    issue = _find_issue_by_us_label(us, role_label)
    us_label = f"US:{us}"

    if issue:
        labels = [label["name"] for label in issue.get("labels", [])]
        _github_api(
            f"/issues/{issue['number']}",
            method="PATCH",
            payload={
                "title": title,
                "body": body,
                "labels": labels,
            },
        )
        return

    _github_api(
        "/issues",
        method="POST",
        payload={
            "title": title,
            "body": body,
            "labels": [role_label, "ai-output", us_label],
        },
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


def _collect_existing_app_context() -> str:
    app_dir = _project_root() / "outputs" / "app"
    if not app_dir.exists():
        return ""

    sections: list[str] = []
    for path in sorted(app_dir.rglob("*")):
        if not path.is_file() or path.name == "APP_SOURCE.txt":
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        sections.append(f"FILE: {path.relative_to(app_dir)}\n{content}")
    return "\n\n".join(sections).strip()


def _prompt_human_action(agent_name: str, result_preview: str) -> tuple[str, str]:
    while True:
        print(f"\n=== {agent_name} preview ===\n")
        print(result_preview[:2000])
        print("\nChoose action:")
        print("1. Làm lại với feedback")
        print("2. Tiếp tục")
        print("3. Cancel")
        choice = input("Your choice (1/2/3, Enter=2): ").strip()

        if choice in {"", "2", "continue", "c"}:
            return "continue", ""
        if choice in {"3", "cancel", "x"}:
            return "cancel", ""
        if choice in {"1", "redo", "r"}:
            while True:
                feedback = input("Nhập feedback: ").strip()
                if feedback:
                    return "redo", feedback
                print("Feedback không được để trống.")
        print("Lựa chọn không hợp lệ. Vui lòng nhập 1, 2, 3 hoặc Enter.")


def _run_with_feedback(agent_name: str, runner, base_inputs: dict[str, str]):
    feedback_notes: list[str] = []

    while True:
        run_inputs = dict(base_inputs)
        if feedback_notes:
            run_inputs["human_feedback"] = "\n\n".join(feedback_notes)
        result = runner(run_inputs)
        raw_result = str(getattr(result, "raw", result)).strip()
        action, feedback = _prompt_human_action(agent_name, raw_result)

        if action == "continue":
            return result
        if action == "cancel":
            raise RuntimeError(f"Flow cancelled before writing {agent_name} result.")

        feedback_notes.append(feedback)

async def _run_parallel_crews(inputs: dict[str, str], business_context: str) -> tuple[object, object]:
    demo = Demo()
    parallel_inputs = {
        **inputs,
        "business_analysis": business_context,
        "existing_app_context": _collect_existing_app_context() or "No existing app context.",
    }
    frontend_result = await asyncio.to_thread(
        _run_with_feedback,
        "Frontend Developer",
        lambda current_inputs: demo.frontend_developer_crew().kickoff(inputs=current_inputs),
        parallel_inputs,
    )
    manual_result = await asyncio.to_thread(
        _run_with_feedback,
        "Manual Tester",
        lambda current_inputs: demo.manual_tester_crew().kickoff(inputs=current_inputs),
        parallel_inputs,
    )
    return frontend_result, manual_result


def _run_and_materialize(inputs: dict[str, str]) -> None:
    demo = Demo()
    business_result = _run_with_feedback(
        "Business Analytics",
        lambda current_inputs: demo.business_analytics_crew().kickoff(inputs=current_inputs),
        inputs,
    )
    _update_issue_by_us_label(
        us=inputs["us"],
        role_label="business-analytics",
        title=f"Business Analytics - {inputs['topic']}",
        body=str(getattr(business_result, "raw", business_result)).strip(),
    )
    _, manual_result = asyncio.run(
        _run_parallel_crews(inputs, str(getattr(business_result, "raw", business_result)).strip())
    )
    _extract_frontend_app()
    _update_issue_by_us_label(
        us=inputs["us"],
        role_label="manual-tester",
        title=f"Manual Tester - {inputs['topic']}",
        body=str(getattr(manual_result, "raw", manual_result)).strip(),
    )

def run():
    """Run the crew."""
    inputs = _build_inputs(_prompt_topic(), _prompt_us())

    try:
        _run_and_materialize(inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """Train the crew for a given number of iterations."""
    inputs = _build_inputs(_prompt_topic(), _prompt_us())
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
    inputs = _build_inputs(_prompt_topic(), _prompt_us())

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
        **_build_inputs(
            trigger_payload.get("topic", "").strip() or _prompt_topic(),
            trigger_payload.get("us", "").strip() or _prompt_us(),
        ),
    }

    try:
        _run_and_materialize(inputs)
        return None
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
