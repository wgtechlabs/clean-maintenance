# Clean Maintenance

![Clean Maintenance banner — Secure dependencies. Ship clean fixes.](<https://ghrb.waren.build/render/banner?header=Clean+Maintenance&subheader=Secure+dependencies.+Ship+clean+fixes.&bg=102b27-187864&color=ffffff&subheadercolor=d6f1e5&headerfont=Inter&subheaderfont=Inter&support=true&stats=false>)
<!-- Created with GitHub Repo Banner by Waren Gonzaga: https://ghrb.waren.build -->

**Clean Maintenance** is a Codex skill that guides maintainers through GitHub Dependabot security alerts, safe dependency updates, and focused fix pull requests.

[Skill instructions](SKILL.md) · [GitHub issues](https://github.com/wgtechlabs/clean-maintenance/issues)

## ✨ Features

- Triage current Dependabot alerts and capture their advisories, affected ranges, manifests, and patched versions.
- Trace direct and transitive dependencies to the active package manager and lockfile.
- Guide minimal, compatibility-aware updates without dismissing alerts or forcing risky overrides.
- Prepare focused Clean Flow pull requests and report validation and alert status accurately.

## 🚀 Getting Started

### Prerequisites

- Codex with skill support.
- Access to the target repository through a connected GitHub integration or an authenticated GitHub CLI session.

### Install

Create your Codex skills directory if needed, then clone this repository into it:

```sh
skill_dir="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$skill_dir"
git clone https://github.com/wgtechlabs/clean-maintenance.git "$skill_dir/clean-maintenance"
```

### First use

In a Codex session with the skill installed, ask it to inspect open Dependabot alerts in a repository. For example:

```text
$clean-maintenance triage open critical Dependabot alerts in OWNER/REPO and propose a safe fix
```

## 📖 Usage

Use the skill to review alert details, identify the dependency path, and prepare the smallest safe remediation. It should report the advisory IDs, package and lockfile changes, checks performed, and whether GitHub still lists the alerts as open. Ask explicitly before publishing a PR or merging when those actions are not part of your request.

## 📚 Documentation

- [SKILL.md](SKILL.md) contains the complete triage, remediation, Clean Flow, and verification guidance.
- [Clean README specification](https://github.com/wgtechlabs/clean-readme/blob/main/SPECIFICATION.md) defines this README's section order and content rules.

## 🛠️ Development

This is a documentation-only repository. There are no build or test scripts. Before submitting a README or skill change, review factual claims and links, confirm the skill name and UI metadata agree, and run:

```sh
git diff --check
```

## 🤝 Contributing

Contributions are welcome. Create a short-lived branch from `dev`, use the [Clean Commit](https://github.com/wgtechlabs/clean-commit) format, and open pull requests targeting `dev`.

## 🐛 Issues & Support

[Open an issue](https://github.com/wgtechlabs/clean-maintenance/issues) to report inaccurate guidance, a broken example, or a feature request. Avoid posting credentials or private security details in public issues.

## 📄 License

No license has been specified for this repository.

## 👥 Authors & Contributors

Created by [Waren Gonzaga](https://github.com/warengonzaga) for [WG Technology Labs](https://github.com/wgtechlabs). See the [contributor graph](https://github.com/wgtechlabs/clean-maintenance/graphs/contributors).
