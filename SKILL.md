---
name: clean-maintenance
description: Triage and remediate GitHub Dependabot security alerts, update the correct dependency and lockfile, and prepare a focused Clean Flow fix PR. Use for dependency vulnerability maintenance, not routine version bumps.
---

# Clean Maintenance

Use this skill to turn Dependabot alerts into a small, verifiable dependency-security fix. Follow repository instructions first, including `AGENTS.md`, `CONTRIBUTING.md`, and the declared package manager and branch flow.

## Triage the alerts

- Read the current open alerts from the repository's Dependabot page or an available GitHub integration. If needed, use the authenticated GitHub CLI. For example:

  ```powershell
  gh api 'repos/OWNER/REPO/dependabot/alerts?state=open' --jq '[.[] | {number, state, package: .dependency.package.name, ecosystem: .dependency.package.ecosystem, manifest: .dependency.manifest_path, scope: .dependency.scope, vulnerable: .security_vulnerability.vulnerable_version_range, fixed: .security_vulnerability.first_patched_version.identifier, advisory: .security_advisory.ghsa_id, cve: .security_advisory.cve_id}]'
  ```

- Capture the alert number, package ecosystem, manifest or lockfile, vulnerable range, fixed version, severity, and advisory ID. Prioritize the severity the user requested; do not assume an alert is current from an old PR or scan.
- If the alert endpoint is unavailable, distinguish missing authorization from network/tool limitations. Never ask the user to paste a token or print credentials. Ask them to refresh the authenticated CLI or provide the alert details if access cannot be restored.
- Check the advisory and package-manager metadata for current fix guidance. Do not guess a safe version from the package name alone.

## Choose a safe, focused remediation

- Trace whether the dependency is direct or transitive and which active manifest and lockfile introduce it. Confirm the package manager used by CI and contributor instructions.
- Prefer updating the direct dependency or its parent to a release that brings in a patched transitive version. Update lockfiles with the repository's package manager; do not hand-edit generated lockfile data.
- Avoid forced resolutions, overrides, or major-version jumps unless the advisory requires them and compatibility is understood. Explain any compatibility tradeoff in the PR.
- Remove an obsolete manifest or lockfile only after confirming it is not used by current workflows or documented development paths. Do not remove a file merely to silence an alert if it is still an active dependency source.
- Do not dismiss alerts or add ignore rules as a substitute for a fix. If there is no patched version or no safe upgrade, report the blocker and viable options instead of claiming resolution.
- Keep the change limited to the affected dependency graph. Batch alerts only when one coherent update fixes the same dependency path without unrelated upgrades.

## Prepare the fix PR

- Follow repository branching rules. For Clean Flow, create a short-lived `fix/...` branch from `dev` and target the PR to `dev`; do not commit directly to `dev` or `main`.
- Use Clean Commit format for the commit and PR title. Security fixes use `🔒 security: ...` or a scoped equivalent, with a lowercase present-tense description.
- Apply only labels that already exist in the repository; use `security` when available. Do not create labels unless asked.
- Run the checks required by repository instructions and any available dependency or security audit. Report skipped checks and validation limits accurately.
- Include the alert IDs and advisory identifiers, the dependency path changed, why the chosen upgrade/removal is safe, and validation results in the PR description.
- Do not merge unless the user explicitly asks. Before reporting merge readiness, recheck the PR head SHA, mergeability, and every required check conclusion.

## Verify alert status

- After opening the PR, verify its base branch, head branch, diff, labels, and check state.
- An alert may remain open while a fix is only on a feature branch or `dev`. Do not say it is resolved until the fix reaches the repository's default branch and a fresh Dependabot query confirms the alert is closed or fixed.
- If addressing review feedback, apply the requested change and reply to each addressed review thread; resolve threads only after verifying the change.

## Report back

Summarize the alerts handled, the package/lockfile change, branch and PR link, checks that passed or remain pending, and whether GitHub currently reports the alerts as open or fixed. Never include secrets or credential values.
