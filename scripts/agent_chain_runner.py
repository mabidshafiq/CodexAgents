#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
STAGE_FILES = [
    "release-report.md",
    "test-report.md",
    "task-plan.md",
    "architecture.md",
    "product-spec.md",
    "idea.md",
]

DEFAULT_SKILL_SEQUENCE = {
    "idea.md": "ios-product-spec-agent",
    "product-spec.md": "ios-technical-architect-agent",
    "architecture.md": "ios-task-planner-agent",
    "task-plan.md": "ios-implementation-agent",
    "test-report.md": "ios-pr-review-agent",
    "release-report.md": "ios-release-merge-agent",
}


def today() -> str:
    return dt.date.today().isoformat()


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:48] or "run"


def fail(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def read_text(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def parse_header(text: str) -> dict[str, str]:
    header: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("- "):
            continue
        if ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        header[key.strip().lower()] = value.strip()
    return header


def load_skill_prompt(skill_name: str) -> str:
    skill_path = ROOT / "skills" / skill_name / "SKILL.md"
    if not skill_path.exists():
        fail(f"missing skill: {skill_name}")
    body = skill_path.read_text()
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", body, re.DOTALL)
    if not match:
        fail(f"invalid SKILL.md for {skill_name}")
    meta = yaml.safe_load(match.group(1))
    return meta.get("description", "").strip()


def repo_root(path: Path) -> Path:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        fail(f"{path} is not inside a git repository")
    return Path(output.strip())


def git_remote_slug(repo: Path) -> str:
    try:
        url = subprocess.check_output(
            ["git", "-C", str(repo), "remote", "get-url", "origin"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        return ""
    match = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    return match.group(1) if match else ""


def ensure_run_dir(repo: Path, run_id: str) -> Path:
    run_dir = repo / "docs" / "agent-runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_idea_file(run_dir: Path, run_id: str, source: str, repo: Path) -> Path:
    idea_path = run_dir / "idea.md"
    if idea_path.exists():
        return idea_path

    idea_path.write_text(
        "\n".join(
            [
                "# Idea",
                "",
                f"- Run ID: {run_id}",
                "- Status: draft",
                "- Owner Agent: ios-team-lead",
                "- Next Agent: ios-team-lead",
                f"- Last Updated: {today()}",
                f"- Source: {source}",
                "",
                f"Repository: {repo}",
                "",
            ]
        )
    )
    return idea_path


def infer_run_id(args: argparse.Namespace) -> str:
    if args.run_id:
        return args.run_id
    if args.issue:
        issue_id = re.search(r"/issues?/(\d+)", args.issue)
        if issue_id:
            return f"{today()}-issue-{issue_id.group(1)}"
    if args.pr:
        pr_id = re.search(r"/pull/(\d+)", args.pr)
        if pr_id:
            return f"{today()}-pr-{pr_id.group(1)}"
    source = args.idea or args.task or args.issue or args.pr or "run"
    return f"{today()}-{slugify(source)}"


def infer_source(args: argparse.Namespace) -> str:
    parts = []
    if args.idea:
        parts.append(f"idea: {args.idea}")
    if args.task:
        parts.append(f"task: {args.task}")
    if args.issue:
        parts.append(f"issue: {args.issue}")
    if args.pr:
        parts.append(f"pr: {args.pr}")
    if args.repo:
        parts.append(f"repo: {args.repo}")
    return " | ".join(parts) if parts else "unknown source"


def extract_metadata(path: Path) -> dict[str, str]:
    text = read_text(path)
    if not text:
        return {}
    return parse_header(text)


def detect_task_plan_next_agent(text: str, header: dict[str, str]) -> Optional[str]:
    if header.get("next agent"):
        return header["next agent"]
    if re.search(r"(?im)^-\s*(PR URL|Pull Request|PR)\s*:\s*https?://", text):
        return "ios-test-agent"
    if re.search(r"(?im)^-\s*(Branch|Task)\s*:", text):
        return "ios-implementation-agent"
    return None


def choose_next_agent(run_dir: Path) -> tuple[str, Path, dict[str, str]]:
    for filename in STAGE_FILES:
        path = run_dir / filename
        if not path.exists():
            continue
        header = extract_metadata(path)
        status = header.get("status", "").lower()
        next_agent = header.get("next agent", "").strip()

        if filename == "task-plan.md":
            candidate = detect_task_plan_next_agent(path.read_text(), header)
            if candidate:
                return candidate, path, header
            return "ios-implementation-agent", path, header
        if filename == "test-report.md":
            if next_agent:
                return next_agent, path, header
            return ("ios-pr-review-agent" if status == "verified" else "ios-implementation-agent"), path, header
        if filename == "release-report.md":
            if next_agent:
                return next_agent, path, header
            return ("terminal" if status == "merged" else "ios-implementation-agent"), path, header

        if next_agent:
            return next_agent, path, header
        if filename == "idea.md":
            return "ios-product-spec-agent", path, header
        if filename == "product-spec.md":
            return "ios-technical-architect-agent", path, header
        if filename == "architecture.md":
            return "ios-task-planner-agent", path, header

    return "ios-team-lead", run_dir / "idea.md", {}


def build_prompt(skill: str, repo: Path, run_dir: Path, trigger_file: Path, source: str) -> str:
    stage_note = {
        "ios-team-lead": "Resolve the intake, write or update idea.md, and set Next Agent.",
        "ios-product-spec-agent": "Write or update product-spec.md from the current run files.",
        "ios-technical-architect-agent": "Write or update architecture.md from the current run files.",
        "ios-task-planner-agent": "Write or update task-plan.md and GitHub issues from the current run files.",
        "ios-implementation-agent": "Implement exactly one task, update task-plan.md, and open or update a PR.",
        "ios-test-agent": "Verify the PR locally and update test-report.md.",
        "ios-pr-review-agent": "Review the PR and update release-report.md.",
        "ios-release-merge-agent": "Check merge gates and merge only if safe.",
    }.get(skill, "Complete the assigned work.")

    files = []
    for name in ["idea.md", "product-spec.md", "architecture.md", "task-plan.md", "test-report.md", "release-report.md"]:
        path = run_dir / name
        if path.exists():
            files.append(f"- {name}")

    prompt_lines = [
        f"You are running as ${skill}.",
        f"Repository: {repo}",
        f"Run directory: {run_dir}",
        f"Trigger file: {trigger_file.name}",
        f"Source: {source}",
        "",
        "Available run files:",
        *(files if files else ["- none yet"]),
        "",
        f"Task: {stage_note}",
        "Follow the handoff contract in references/handoff-contract.md.",
        "Set the run file header fields, especially Status and Next Agent.",
        "Stop after completing this one responsibility.",
    ]
    return "\n".join(prompt_lines)


def load_executor(args: argparse.Namespace) -> Optional[str]:
    if args.executor:
        return args.executor
    env = os.environ.get("CODEX_AGENT_EXECUTOR", "").strip()
    if env:
        return env
    config_path = args.config or ROOT / ".agent-runner.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
        except json.JSONDecodeError as exc:
            fail(f"invalid config file {config_path}: {exc}")
        executor = config.get("executor", "").strip()
        if executor:
            return executor
    return None


def run_executor(template: str, *, skill: str, prompt_file: Path, repo: Path, run_id: str, run_dir: Path) -> None:
    values = {
        "skill": shlex.quote(skill),
        "prompt_file": shlex.quote(str(prompt_file)),
        "repo": shlex.quote(str(repo)),
        "run_id": shlex.quote(run_id),
        "run_dir": shlex.quote(str(run_dir)),
    }
    command = template.format(**values)
    print(f"dispatch: {command}")
    completed = subprocess.run(command, shell=True, check=False)
    if completed.returncode != 0:
        fail(f"executor failed for {skill} with exit code {completed.returncode}")


def write_prompt_file(run_dir: Path, skill: str, prompt: str) -> Path:
    prompt_dir = run_dir / ".runner"
    prompt_dir.mkdir(exist_ok=True)
    handle = tempfile.NamedTemporaryFile("w", delete=False, dir=prompt_dir, prefix=f"{skill}-", suffix=".md")
    with handle:
        handle.write(prompt)
    return Path(handle.name)


def run_chain(args: argparse.Namespace) -> None:
    repo = repo_root(Path(args.repo).resolve())
    run_id = infer_run_id(args)
    run_dir = ensure_run_dir(repo, run_id)
    source = infer_source(args)
    if args.idea or args.task or args.issue or args.pr:
        write_idea_file(run_dir, run_id, source, repo)

    executor = load_executor(args)
    if not executor and not args.dry_run:
        fail(
            "no executor configured. Set CODEX_AGENT_EXECUTOR, pass --executor, or add .agent-runner.json."
        )

    steps = 0
    while True:
        skill, trigger_file, header = choose_next_agent(run_dir)
        status = header.get("status", "").lower()
        if skill == "terminal" or status == "merged":
            print(f"run {run_id} is complete")
            return

        prompt = build_prompt(skill, repo, run_dir, trigger_file, source)
        prompt_file = write_prompt_file(run_dir, skill, prompt)
        print(f"next: {skill} from {trigger_file.name}")

        if args.dry_run or not executor:
            print(prompt)
            return

        run_executor(executor, skill=skill, prompt_file=prompt_file, repo=repo, run_id=run_id, run_dir=run_dir)
        steps += 1
        if args.max_steps and steps >= args.max_steps:
            print(f"stopped after {steps} steps")
            return


def print_status(args: argparse.Namespace) -> None:
    repo = repo_root(Path(args.repo).resolve())
    run_dir = ensure_run_dir(repo, args.run_id)
    skill, trigger_file, header = choose_next_agent(run_dir)
    print(json.dumps({
        "run_id": args.run_id,
        "repo": str(repo),
        "run_dir": str(run_dir),
        "next_agent": skill,
        "trigger_file": trigger_file.name,
        "status": header.get("status", "unknown"),
    }, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Automatically dispatch the iOS agent chain.")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo", required=True, help="Target app repository path.")
    common.add_argument("--run-id", help="Existing or desired run id.")
    common.add_argument("--executor", help="Shell template used to launch an agent.")
    common.add_argument("--config", type=Path, help="Path to JSON runner config.")

    start = sub.add_parser("start", parents=[common], help="Create a run and dispatch the chain.")
    start.add_argument("--idea", help="App idea or feature request.")
    start.add_argument("--task", help="Existing app task description.")
    start.add_argument("--issue", help="GitHub issue URL.")
    start.add_argument("--pr", help="GitHub PR URL.")
    start.add_argument("--dry-run", action="store_true", help="Print the next step instead of executing it.")
    start.add_argument("--max-steps", type=int, default=0, help="Stop after N dispatched agents.")
    start.set_defaults(func=run_chain)

    resume = sub.add_parser("resume", parents=[common], help="Resume an existing run.")
    resume.add_argument("--dry-run", action="store_true", help="Print the next step instead of executing it.")
    resume.add_argument("--max-steps", type=int, default=0, help="Stop after N dispatched agents.")
    resume.set_defaults(func=run_chain)

    status = sub.add_parser("status", parents=[common], help="Show the next agent for a run.")
    status.set_defaults(func=print_status)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
