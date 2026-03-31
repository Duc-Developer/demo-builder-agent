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

MAX_CONTEXT_CHARS = 2_000_000
MAX_CONTEXT_FILES = 20
MAX_FILE_CHARS = 200_000


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


def _prompt_role_toggle(label: str, default: bool = True) -> bool:
    default_hint = "Y/n" if default else "y/N"
    while True:
        value = input(f"Enable {label}? ({default_hint}): ").strip().lower()
        if not value:
            return default
        if value in {"y", "yes", "1"}:
            return True
        if value in {"n", "no", "0"}:
            return False
        print("Lựa chọn không hợp lệ. Vui lòng nhập y hoặc n.")


def _prompt_flow_controls() -> dict[str, str]:
    print("\n=== Flow control ===")
    enable_researcher = _prompt_role_toggle("Researcher", default=True)
    enable_designer = _prompt_role_toggle("Designer", default=True)
    enable_developer = _prompt_role_toggle("Developer", default=True)
    enable_manual_tester = _prompt_role_toggle("Manual Tester", default=True)

    if enable_designer and not enable_developer:
        raise ValueError("Designer chỉ có thể bật khi Developer được bật.")

    if enable_designer and not enable_researcher:
        print("Designer cần đầu vào từ Researcher, tự động bật Researcher.")
        enable_researcher = True

    return {
        "enable_researcher": str(enable_researcher).lower(),
        "enable_designer": str(enable_designer).lower(),
        "enable_developer": str(enable_developer).lower(),
        "enable_manual_tester": str(enable_manual_tester).lower(),
    }


def _is_enabled(inputs: dict[str, str], key: str) -> bool:
    return inputs.get(key, "").strip().lower() == "true"


def _build_inputs(topic: str, us: str) -> dict[str, str]:
    return {
        "topic": topic,
        "us": us,
        "current_year": str(datetime.now().year),
        "reference_url": "",
        "enable_researcher": "true",
        "enable_designer": "true",
        "enable_developer": "true",
        "enable_manual_tester": "true",
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


def _truncate_text(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    remaining = len(value) - limit
    return f"{value[:limit]}\n\n...[truncated {remaining} characters]..."


def _collect_existing_app_context() -> str:
    app_dir = _project_root() / "outputs" / "app"
    if not app_dir.exists():
        return ""

    sections: list[str] = []
    total_chars = 0
    file_count = 0
    for path in sorted(app_dir.rglob("*")):
        if not path.is_file() or path.name == "APP_SOURCE.txt":
            continue
        if file_count >= MAX_CONTEXT_FILES or total_chars >= MAX_CONTEXT_CHARS:
            sections.append("...[existing app context truncated due to size limits]...")
            break
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative_path = path.relative_to(app_dir)
        bounded_content = _truncate_text(content, MAX_FILE_CHARS)
        section = f"FILE: {relative_path}\n{bounded_content}"
        remaining_chars = MAX_CONTEXT_CHARS - total_chars
        if remaining_chars <= 0:
            sections.append("...[existing app context truncated due to size limits]...")
            break
        if len(section) > remaining_chars:
            section = f"FILE: {relative_path}\n{_truncate_text(bounded_content, max(0, remaining_chars - len(f'FILE: {relative_path}\\n')))}"
            sections.append(section)
            sections.append("...[existing app context truncated due to size limits]...")
            break
        sections.append(section)
        total_chars += len(section)
        file_count += 1
    return "\n\n".join(sections).strip()


def _prompt_human_action(agent_name: str, result_preview: str) -> tuple[str, str]:
    while True:
        print()
        print(f"=== {agent_name} completed ===")
        print()
        print("=== Preview ===")
        print()
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
        print()
        action, feedback = _prompt_human_action(agent_name, raw_result)

        if action == "continue":
            return result
        if action == "cancel":
            raise RuntimeError(f"Flow cancelled before writing {agent_name} result.")

        feedback_notes.append(feedback)

def _run_design_chain(inputs: dict[str, str], business_context: str):
    demo = Demo()
    research_context = ""
    design_context = ""

    if _is_enabled(inputs, "enable_researcher"):
        researcher_inputs = {
            **inputs,
            "business_analysis": business_context,
        }
        researcher_result = _run_with_feedback(
            "Researcher",
            lambda current_inputs: demo.researcher_crew().kickoff(inputs=current_inputs),
            researcher_inputs,
        )
        research_context = str(getattr(researcher_result, "raw", researcher_result)).strip()
        _update_issue_by_us_label(
            us=inputs["us"],
            role_label="researcher",
            title=f"Researcher - {inputs['topic']}",
            body=research_context,
        )

    if _is_enabled(inputs, "enable_designer"):
        designer_inputs = {
            **inputs,
            "business_analysis": business_context,
            "research_brief": research_context,
        }
        designer_result = _run_with_feedback(
            "Designer",
            lambda current_inputs: demo.designer_crew().kickoff(inputs=current_inputs),
            designer_inputs,
        )
        design_context = str(getattr(designer_result, "raw", designer_result)).strip()
        _update_issue_by_us_label(
            us=inputs["us"],
            role_label="designer",
            title=f"Designer - {inputs['topic']}",
            body=design_context,
        )

    if _is_enabled(inputs, "enable_developer"):
        frontend_inputs = {
            **inputs,
            "business_analysis": business_context,
            "research_brief": research_context,
            "design_blueprint": design_context,
            "existing_app_context": _collect_existing_app_context() or "No existing app context.",
        }
        return _run_with_feedback(
            "Frontend Developer",
            lambda current_inputs: demo.frontend_developer_crew().kickoff(inputs=current_inputs),
            frontend_inputs,
        )

    return None


async def _run_parallel_crews(inputs: dict[str, str], business_context: str) -> tuple[object, object]:
    demo = Demo()
    manual_tester_inputs = {
        **inputs,
        "business_analysis": business_context,
    }
    frontend_result = await asyncio.to_thread(
        _run_design_chain,
        inputs,
        business_context,
    )
    manual_result = None
    if _is_enabled(inputs, "enable_manual_tester"):
        manual_result = await asyncio.to_thread(
            lambda: demo.manual_tester_crew().kickoff(inputs=manual_tester_inputs),
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
    frontend_result, manual_result = asyncio.run(
        _run_parallel_crews(inputs, str(getattr(business_result, "raw", business_result)).strip())
    )
    if frontend_result is not None:
        _extract_frontend_app()
    if manual_result is not None:
        _update_issue_by_us_label(
            us=inputs["us"],
            role_label="manual-tester",
            title=f"Manual Tester - {inputs['topic']}",
            body=str(getattr(manual_result, "raw", manual_result)).strip(),
        )

def run():
    """Run the crew."""
    inputs = _build_inputs(_prompt_topic(), _prompt_us())
    inputs.update(_prompt_flow_controls())

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
