# How To Use These Agents

## 1. Start With The Team Lead

Use the team lead agent first to turn your idea into a run.

Example:

```text
Use $ios-team-lead to coordinate this iOS app idea from intake through autonomous delivery: Build a habit tracker iPhone app.
```

For an existing app:

```text
Use $ios-team-lead for this repo: /path/to/MyApp. Task: Add onboarding screens.
```

## 2. Let The Lead Create The Run

The team lead should create or update:

```text
docs/agent-runs/<run-id>/idea.md
```

It will decide which specialist agent should act next.

## 3. Run The Product Spec Agent

```text
Use $ios-product-spec-agent with run-id <run-id>.
```

This creates:

```text
docs/agent-runs/<run-id>/product-spec.md
```

## 4. Run The Technical Architect

```text
Use $ios-technical-architect-agent with run-id <run-id>.
```

This creates:

```text
docs/agent-runs/<run-id>/architecture.md
```

## 5. Run The Task Planner

```text
Use $ios-task-planner-agent with run-id <run-id>.
```

This creates:

```text
docs/agent-runs/<run-id>/task-plan.md
```

If GitHub is available, it should also create GitHub issues.

## 6. Run Implementation Per Task

For each issue or task:

```text
Use $ios-implementation-agent for issue <GitHub issue URL>.
```

The agent should create a branch, implement one task, and open or update a PR.

## 7. Run Testing

```text
Use $ios-test-agent for PR <GitHub PR URL>.
```

This writes:

```text
docs/agent-runs/<run-id>/test-report.md
```

## 8. Run PR Review

```text
Use $ios-pr-review-agent for PR <GitHub PR URL>.
```

This updates:

```text
docs/agent-runs/<run-id>/release-report.md
```

## 9. Run Release And Merge

```text
Use $ios-release-merge-agent for PR <GitHub PR URL>.
```

It only merges if all gates pass:

- GitHub checks are green
- local build passes
- local tests pass
- simulator launch passes when needed
- review has no blocking findings

## 10. Validate The Skill Pack

From the skill-pack repo:

```bash
cd /Volumes/External_SSD/DevProjects/CodexAgents
python3 scripts/validate_skill_pack.py
```

## Simple Flow

```text
$ios-team-lead
→ $ios-product-spec-agent
→ $ios-technical-architect-agent
→ $ios-task-planner-agent
→ $ios-implementation-agent
→ $ios-test-agent
→ $ios-pr-review-agent
→ $ios-release-merge-agent
```
