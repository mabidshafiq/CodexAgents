# iOS Agent Skill Pack

Portable Codex skills for an autonomous iOS app delivery team.

## Skills

- `ios-team-lead`: intake, run state, routing, and handoffs
- `ios-product-spec-agent`: product requirements and acceptance criteria
- `ios-technical-architect-agent`: Swift/iOS architecture planning
- `ios-task-planner-agent`: executable GitHub issue planning
- `ios-implementation-agent`: one task, one branch, one PR
- `ios-test-agent`: local iOS verification and CI status
- `ios-pr-review-agent`: release-blocking PR review
- `ios-release-merge-agent`: autonomous merge gate checks and merge

## Shared State

Agents coordinate through `docs/agent-runs/<run-id>/` in the target iOS repo and GitHub issues/PRs. Shared contracts live in `references/`.

## Validation

Run:

```bash
python3 scripts/validate_skill_pack.py
```

This checks skill frontmatter, `agents/openai.yaml`, required shared references, and the two dry-run paths: new app idea and existing app task.
