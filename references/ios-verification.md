# iOS Verification Reference

Use CLI-first verification. Prefer the repo's documented commands when present.

## Discover Commands

Check, in order:

- `README.md`, `AGENTS.md`, `PLANS.md`, `Makefile`, `.github/workflows/`
- Xcode workspace/project and schemes
- Tuist, SwiftPM, or custom scripts

## Baseline Commands

Adapt scheme, workspace, and simulator names to the repo.

```bash
xcodebuild -list
xcodebuild -scheme <Scheme> -destination 'platform=iOS Simulator,name=iPhone 16' build
xcodebuild -scheme <Scheme> -destination 'platform=iOS Simulator,name=iPhone 16' test
xcrun simctl boot "iPhone 16"
xcrun simctl install booted <path-to-app.app>
xcrun simctl launch booted <bundle-id>
```

If the repo uses Tuist or SwiftPM, generate/open the project using the repo's own instructions before running Xcode commands.

## Evidence To Record

In `test-report.md`, record:

- exact commands run
- pass/fail result
- simulator device used
- app scheme and bundle id when known
- test count or reason tests were not applicable
- CI check state and link
- screenshots or logs only when useful for diagnosing failure

## Testing Defaults

Add or update tests when the change affects:

- business logic
- data persistence
- networking and decoding
- state transitions
- bug fixes
- accessibility behavior that can be asserted

Simulator launch is required for UI changes, navigation changes, app lifecycle changes, or app scaffolding.
