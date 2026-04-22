# Autonomous Merge Gates

The release agent may merge a PR without human approval only when every gate passes.

## Required Gates

- GitHub required checks are green.
- Local `xcodebuild build` passes for the app scheme.
- Local `xcodebuild test` passes for the app scheme when tests exist or were added.
- UI-touching changes launch successfully in an iOS simulator.
- The PR review agent reports no blocking findings.
- The PR branch is up to date with the target branch or cleanly mergeable.
- No secrets, signing credentials, destructive migrations, or unrelated large rewrites are present.

## Blocking Conditions

Do not merge when:

- Any required GitHub check is failing, pending too long, or unavailable without explanation.
- Local build, test, or simulator launch fails.
- Review findings remain unresolved.
- The PR includes broad unrelated changes.
- The diff touches signing, certificates, provisioning profiles, secrets, analytics collection, privacy manifests, payments, authentication, data deletion, or migrations without explicit spec coverage.
- The target branch changed after verification and the PR was not rechecked.

## Failure Handoff

When a gate fails:

1. Update `docs/agent-runs/<run-id>/release-report.md` with status `blocked`.
2. Add the failing gate, evidence, and command output summary.
3. Route the work back to the responsible agent:
   - CI failure: implementation agent or test agent
   - local build/test failure: implementation agent
   - simulator failure: implementation agent and test agent
   - review finding: implementation agent
   - unclear product decision: team lead or product spec agent

## Merge Output

After merge:

- Update `release-report.md` with status `merged`.
- Record PR URL, merge commit, target branch, verification summary, and any follow-up issues.
- Close or update related GitHub issues.
