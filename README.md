# Clean Maintenance

A Codex skill for triaging GitHub Dependabot security alerts and preparing focused dependency-fix pull requests that follow Clean Flow.

## Contents

- `SKILL.md` — alert triage, safe remediation, pull request preparation, and verification
- `agents/openai.yaml` — Codex interface metadata

## Install

Clone this repository into your Codex skills directory:

- `$CODEX_HOME/skills/clean-maintenance`, or
- `~/.codex/skills/clean-maintenance` when `CODEX_HOME` is unset.

## Use

Ask Codex to triage the repository's open Dependabot alerts and prepare a focused fix PR. The skill checks the active package manager and lockfile, follows repository branch rules, and reports checks and alert status without claiming a fix is complete before the alert clears.
