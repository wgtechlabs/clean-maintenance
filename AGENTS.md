# AI Agent Instructions

These instructions apply to work in this repository. Follow stricter repository,
organization, and user instructions when they apply.

## Clean Commit

Use this format for commit messages and pull request titles:

```text
<emoji> <type>: <description>
<emoji> <type> (<scope>): <description>
<emoji> <type>!: <description>
<emoji> <type>! (<scope>): <description>
```

Use the exact emoji and lowercase type: 📦 `new`, 🔧 `update`, 🗑️ `remove`,
🔒 `security`, ⚙️ `setup`, ☕ `chore`, 🧪 `test`, 📖 `docs`, or 🚀 `release`.
Use present tense, start the description in lowercase, omit a final period,
and keep messages under 72 characters when practical. Scopes are optional and
lowercase. Use `!` only for breaking changes to `new`, `update`, `remove`, or
`security` work. Keep each commit to one logical change.

## Clean Flow

Ship through `dev` and keep `main` stable:

```text
feature/* -> squash merge -> dev -> merge commit -> main
```

- Create short-lived `feature/`, `fix/`, `docs/`, `chore/`, `test/`, or
  `refactor/` branches from `dev`.
- Target feature pull requests at `dev`; do not send feature branches directly
  to `main`.
- Avoid direct commits to `main` or `dev`.
- Update or rebase feature branches against `dev` before submitting when needed.
- Delete feature branches after merge when repository policy allows it.
- Promote stable `dev` to `main` with a regular merge commit and use a
  meaningful `🚀 release:` pull request title.

## Security

- Scan new first-party code with available security tooling and fix issues
  introduced by the change, then rescan.
- Never expose or log secrets, keys, or credentials. Never commit credential
  files such as `.env` or `credentials.json`.

## Code Quality

- Follow existing repository conventions and prefer existing libraries and
  utilities. Do not add dependencies without justification.
- Keep changes focused, runnable, and production-ready. Use consistent naming
  and present tense.
- Run relevant lint, typecheck, test, build, and security checks when available;
  report checks that were not run or could not be verified.

## Pull Requests and Labels

- Use Clean Commit format for pull request titles.
- Before requesting review or merge, assign relevant labels that already exist
  in the repository. Do not create labels unless explicitly requested.
- Use existing repository label vocabulary; do not rename labels to fit a
  preferred convention.

## Code Review

- Apply requested code review changes and reply directly to each addressed
  review thread. Verify the remote fix and reply before resolving the thread.

## Release Pull Requests

Pull requests from `dev` to `main` must use a meaningful Clean Commit title,
such as `🚀 release: ship v1.4.0 with bot version command and bug fixes`.
