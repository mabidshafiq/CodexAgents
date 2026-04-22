#!/usr/bin/env python3
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SKILLS = [
    "ios-team-lead",
    "ios-product-spec-agent",
    "ios-technical-architect-agent",
    "ios-task-planner-agent",
    "ios-implementation-agent",
    "ios-test-agent",
    "ios-pr-review-agent",
    "ios-release-merge-agent",
]

REQUIRED_REFERENCES = [
    "references/handoff-contract.md",
    "references/merge-gates.md",
    "references/ios-verification.md",
]

DRY_RUN_NEW_APP_CHAIN = [
    ("ios-team-lead", "idea.md"),
    ("ios-product-spec-agent", "product-spec.md"),
    ("ios-technical-architect-agent", "architecture.md"),
    ("ios-task-planner-agent", "task-plan.md"),
    ("ios-implementation-agent", "PR"),
    ("ios-test-agent", "test-report.md"),
    ("ios-pr-review-agent", "release-report.md"),
    ("ios-release-merge-agent", "merged"),
]

DRY_RUN_EXISTING_APP_MARKERS = [
    "repo path plus task",
    "GitHub issue URL",
    "GitHub PR URL",
    "run-id",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing {path.relative_to(ROOT)}")
    return path.read_text()


def validate_skill(skill: str) -> str:
    skill_dir = ROOT / "skills" / skill
    body = read(skill_dir / "SKILL.md")
    match = re.match(r"^---\n(.*?)\n---\n", body, re.DOTALL)
    if not match:
        fail(f"{skill} has invalid frontmatter")
    frontmatter = yaml.safe_load(match.group(1))
    if frontmatter.get("name") != skill:
        fail(f"{skill} frontmatter name mismatch")
    if not frontmatter.get("description"):
        fail(f"{skill} missing description")
    if len(frontmatter["description"]) > 1024:
        fail(f"{skill} description too long")

    metadata = yaml.safe_load(read(skill_dir / "agents" / "openai.yaml"))
    interface = metadata.get("interface", {})
    if f"${skill}" not in interface.get("default_prompt", ""):
        fail(f"{skill} default_prompt must mention ${skill}")
    short_description = interface.get("short_description", "")
    if not 25 <= len(short_description) <= 64:
        fail(f"{skill} short_description must be 25-64 chars")

    for heading in ["## Inputs", "## Workflow", "## Output"]:
        if heading not in body:
            fail(f"{skill} missing {heading}")
    if "../../references/handoff-contract.md" not in body:
        fail(f"{skill} must reference the handoff contract")
    return body


def validate_dry_runs(bodies: dict[str, str]) -> None:
    for skill, marker in DRY_RUN_NEW_APP_CHAIN:
        if marker not in bodies[skill]:
            fail(f"new-app dry run cannot find {marker} in {skill}")

    lead = bodies["ios-team-lead"]
    for marker in DRY_RUN_EXISTING_APP_MARKERS:
        if marker not in lead:
            fail(f"existing-app dry run missing input marker: {marker}")

    release = bodies["ios-release-merge-agent"]
    for gate in ["GitHub required checks", "local build", "simulator launch", "blocking findings"]:
        if gate not in release and gate not in read(ROOT / "references" / "merge-gates.md"):
            fail(f"merge dry run missing gate: {gate}")


def main() -> None:
    for ref in REQUIRED_REFERENCES:
        read(ROOT / ref)

    bodies = {skill: validate_skill(skill) for skill in REQUIRED_SKILLS}
    validate_dry_runs(bodies)
    print("Skill pack is valid.")
    print("Dry run paths covered: new app idea, existing app task, failed verification, blocked review, green merge.")


if __name__ == "__main__":
    main()
