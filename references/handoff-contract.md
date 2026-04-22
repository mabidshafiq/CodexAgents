# iOS Agent Handoff Contract

Use this contract for every autonomous iOS agent run.

## Run Folder

Create or reuse `docs/agent-runs/<run-id>/` in the target app repo. Use a short, stable run id:

- New app: `YYYY-MM-DD-<app-name>`
- Existing app task: `YYYY-MM-DD-issue-<number>` or `YYYY-MM-DD-<short-task>`

Required files:

- `idea.md`: original request, target repo, constraints, links, and current status
- `product-spec.md`: product requirements, acceptance criteria, user stories, scope
- `architecture.md`: technical approach, app structure, dependencies, risks
- `task-plan.md`: ordered tasks, GitHub issue links, branch and PR links
- `test-report.md`: local build, test, simulator, and CI status
- `release-report.md`: review result, merge gate result, release/merge summary

## Status Values

Use exactly one status in each run file header:

- `draft`
- `ready-for-next-agent`
- `blocked`
- `in-progress`
- `verified`
- `merged`

## Agent Output Header

Every file an agent writes or updates must start with:

```markdown
# <Title>

- Run ID: <run-id>
- Status: <status>
- Owner Agent: <agent-skill-name>
- Last Updated: <YYYY-MM-DD>
- Source: <idea, issue URL, PR URL, or repo path>
```

## Handoff Rules

- Each agent owns one responsibility and one output category.
- Read upstream files before acting. Do not infer missing product or technical decisions if they are already documented.
- If required input is missing, set the current file status to `blocked`, name the missing input, and stop.
- If a GitHub issue or PR is created, add the URL to `task-plan.md`.
- If local verification or CI fails, add exact commands and failure summaries to `test-report.md`.
- If a review blocks merge, add the blocking finding and owning agent to `release-report.md`.
- Keep handoffs durable: a different agent must be able to continue from files and GitHub links alone.

## Independent Invocation

An agent must be able to start from any one of:

- `run-id`
- GitHub issue URL
- GitHub PR URL
- target repo path plus task description

Resolve the missing context by reading the target repo, GitHub metadata, and the run folder. Ask the user only when product intent cannot be derived.
