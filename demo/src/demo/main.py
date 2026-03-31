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
from demo.langfuse_utils import flush_langfuse, get_current_trace_url, healthcheck_langfuse, observe, set_current_trace_io, update_observation

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")


def _langfuse_run_metadata(inputs: dict[str, str], flow_name: str) -> dict[str, str]:
    return {
        "flow_name": flow_name,
        "topic": inputs.get("topic", ""),
        "us": inputs.get("us", ""),
    }


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

def _run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _github_pages_url() -> str:
    repo = _require_env("GIT_HUB_REPO")
    owner, name = repo.split("/", 1)
    return f"https://{owner.lower()}.github.io/{name}/"


def _detect_build_output_dir(app_dir: Path) -> Path:
    for candidate in ("dist", "build"):
        candidate_path = app_dir / candidate
        if candidate_path.exists() and candidate_path.is_dir():
            return candidate_path
    raise ValueError("Build output directory not found. Expected dist/ or build/.")


def _github_pages_base_path() -> str:
    raw_base = _require_env("GIT_HUB_PAGE_URL_BASE")
    base = raw_base.strip().strip("\"'")
    if not base:
        raise ValueError("GIT_HUB_PAGE_URL_BASE is empty.")
    if not base.startswith("/"):
        base = f"/{base}"
    if not base.endswith("/"):
        base = f"{base}/"
    return base


def _ensure_vite_base_config(app_dir: Path) -> None:
    vite_config_path: Path | None = None
    for candidate in ("vite.config.ts", "vite.config.js", "vite.config.mjs"):
        candidate_path = app_dir / candidate
        if candidate_path.exists():
            vite_config_path = candidate_path
            break

    if vite_config_path is None:
        return

    content = vite_config_path.read_text(encoding="utf-8")
    if "base:" in content or "base :" in content:
        return

    marker = "export default defineConfig({"
    if marker not in content:
        return

    updated_content = content.replace(
        marker,
        f'{marker}\n  base: "{_github_pages_base_path()}",',
        1,
    )
    vite_config_path.write_text(updated_content, encoding="utf-8")


def build_and_deploy_github_pages(topic: str, us: str) -> str:
    output_dir = _project_root() / "outputs"
    app_dir = output_dir / "app"
    if not app_dir.exists():
        raise ValueError("No app output found to deploy.")

    package_json_path = app_dir / "package.json"
    if not package_json_path.exists():
        raise ValueError("package.json not found in outputs/app.")

    package_json = json.loads(package_json_path.read_text(encoding="utf-8"))
    scripts = package_json.get("scripts", {})
    if "build" not in scripts:
        raise ValueError("Build script not found in generated app package.json.")

    with observe(
        "build_and_deploy_github_pages",
        input={"topic": topic, "us": us, "app_dir": str(app_dir)},
        metadata={
            "github_pages_url": _github_pages_url(),
            "github_pages_base": _github_pages_base_path(),
        },
        as_type="tool",
    ) as observation:
        print("Build & Deploy: Typing...")
        _ensure_vite_base_config(app_dir)
        if (app_dir / "package-lock.json").exists():
            install_command = ["npm", "ci"]
        else:
            install_command = ["npm", "install"]

        install_result = _run_command(install_command, app_dir)
        build_result = _run_command(["npm", "run", "build"], app_dir)

        build_output_dir = _detect_build_output_dir(app_dir)
        deploy_dir = output_dir / "github-pages-deploy"
        if deploy_dir.exists():
            shutil.rmtree(deploy_dir)
        shutil.copytree(build_output_dir, deploy_dir)

        repo = _require_env("GIT_HUB_REPO")
        token = _require_env("GIT_HUB_TOKEN")
        pages_url = _github_pages_url()
        remote_url = f"https://x-access-token:{token}@github.com/{repo}.git"

        _run_command(["git", "init", "-b", "gh-pages"], deploy_dir)
        _run_command(["git", "remote", "add", "origin", remote_url], deploy_dir)
        _run_command(["git", "add", "."], deploy_dir)
        _run_command(["git", "commit", "-m", f"Deploy app for {us}"], deploy_dir)
        _run_command(["git", "push", "--force", "origin", "gh-pages"], deploy_dir)

        update_observation(
            observation,
            output={
                "github_pages_url": pages_url,
                "github_pages_base": _github_pages_base_path(),
                "install_stdout": install_result.stdout[-4000:],
                "build_stdout": build_result.stdout[-4000:],
                "deploy_branch": "gh-pages",
            },
            metadata={"topic": topic, "us": us, "deploy_status": "success"},
        )
        print(f"App deployed to GitHub Pages: {pages_url}")
        return pages_url

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

    with observe(
        f"{agent_name.lower().replace(' ', '_')}_crew",
        input=base_inputs,
        metadata={"agent_name": agent_name},
        as_type="chain",
    ) as observation:
        while True:
            run_inputs = dict(base_inputs)
            if feedback_notes:
                run_inputs["human_feedback"] = "\n\n".join(feedback_notes)
            print(f"{agent_name}: Typing...")
            result = runner(run_inputs)
            raw_result = str(getattr(result, "raw", result)).strip()
            update_observation(
                observation,
                input=run_inputs,
                output=raw_result,
                metadata={
                    "agent_name": agent_name,
                    "feedback_count": len(feedback_notes),
                },
            )
            action, feedback = _prompt_human_action(agent_name, raw_result)

            if action == "continue":
                return result
            if action == "cancel":
                update_observation(
                    observation,
                    level="WARNING",
                    status_message="Flow cancelled by user before persisting result.",
                )
                raise RuntimeError(f"Flow cancelled before writing {agent_name} result.")

            feedback_notes.append(feedback)

async def _run_parallel_crews(inputs: dict[str, str], business_context: str) -> tuple[object, object]:
    demo = Demo()
    parallel_inputs = {
        **inputs,
        "business_analysis": business_context,
        "existing_app_context": _collect_existing_app_context() or "No existing app context.",
    }
    with observe(
        "parallel_crews",
        input={"inputs": inputs, "business_context": business_context},
        metadata=_langfuse_run_metadata(inputs, "parallel_crews"),
        as_type="chain",
    ) as observation:
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
        update_observation(
            observation,
            output={
                "frontend_result": str(getattr(frontend_result, "raw", frontend_result)).strip(),
                "manual_result": str(getattr(manual_result, "raw", manual_result)).strip(),
            },
        )
        return frontend_result, manual_result


def _run_and_materialize(inputs: dict[str, str]) -> None:
    demo = Demo()
    with observe(
        "run_and_materialize",
        input=inputs,
        metadata=_langfuse_run_metadata(inputs, "run_and_materialize"),
        as_type="chain",
    ) as observation:
        business_result = _run_with_feedback(
            "Business Analytics",
            lambda current_inputs: demo.business_analytics_crew().kickoff(inputs=current_inputs),
            inputs,
        )
        business_output = str(getattr(business_result, "raw", business_result)).strip()
        _update_issue_by_us_label(
            us=inputs["us"],
            role_label="business-analytics",
            title=f"Business Analytics - {inputs['topic']}",
            body=business_output,
        )
        frontend_result, manual_result = asyncio.run(
            _run_parallel_crews(inputs, business_output)
        )
        _extract_frontend_app()
        pages_url = build_and_deploy_github_pages(inputs["topic"], inputs["us"])
        manual_output = str(getattr(manual_result, "raw", manual_result)).strip()
        _update_issue_by_us_label(
            us=inputs["us"],
            role_label="manual-tester",
            title=f"Manual Tester - {inputs['topic']}",
            body=manual_output,
        )
        update_observation(
            observation,
            output={
                "business_analytics": business_output,
                "frontend_developer": str(getattr(frontend_result, "raw", frontend_result)).strip(),
                "manual_tester": manual_output,
                "github_pages_url": pages_url,
                "trace_url": get_current_trace_url(),
            },
        )

def cleanup_outputs():
    """Clean up outputs directory."""
    outputs_dir = _project_root() / "outputs"
    if outputs_dir.exists():
        shutil.rmtree(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)

def run():
    """Run the crew."""
    inputs = _build_inputs(_prompt_topic(), _prompt_us())
    # Clean up outputs directory before running
    cleanup_outputs()

    with observe(
        "run",
        input=inputs,
        metadata=_langfuse_run_metadata(inputs, "run"),
        as_type="chain",
    ) as observation:
        try:
            set_current_trace_io(input=inputs)
            _run_and_materialize(inputs)
            update_observation(
                observation,
                output={"status": "success", "trace_url": get_current_trace_url()},
            )
        except Exception as e:
            update_observation(
                observation,
                output={"status": "error", "error": str(e)},
                level="ERROR",
                status_message=str(e),
            )
            raise Exception(f"An error occurred while running the crew: {e}")
        finally:
            flush_langfuse()


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

    with observe(
        "run_with_trigger",
        input=inputs,
        metadata=_langfuse_run_metadata(inputs, "run_with_trigger"),
        as_type="chain",
    ) as observation:
        try:
            set_current_trace_io(input=inputs)
            _run_and_materialize(inputs)
            update_observation(
                observation,
                output={"status": "success", "trace_url": get_current_trace_url()},
            )
            return None
        except Exception as e:
            update_observation(
                observation,
                output={"status": "error", "error": str(e)},
                level="ERROR",
                status_message=str(e),
            )
            raise Exception(f"An error occurred while running the crew with trigger: {e}")
        finally:
            flush_langfuse()


def healthcheck_langfuse_command():
    """Verify Langfuse connection."""
    if healthcheck_langfuse():
        print("Langfuse client is authenticated and ready!")
    else:
        print("Authentication failed. Please check your credentials and host.")
