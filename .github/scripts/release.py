#!/usr/bin/env python3
"""Create Clean Commit based tags, changelog entries, and GitHub releases."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


INITIAL_VERSION = "0.1.0"
VERSION_PREFIX = "v"
CHANGELOG_PATH = "CHANGELOG.md"
MAJOR_TAGS_ENABLED = True
GIT_USER_NAME = "WG Tech Labs"
GIT_USER_EMAIL = "262751631+wgtechlabs-automation@users.noreply.github.com"

VERSION_TAG = re.compile(r"^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
COMMIT_PATTERN = re.compile(r"^\W*([a-z]+)(?:\s*(\(([^)]+)\)))?(!)?:\s+(.+)$")


@dataclass(frozen=True)
class Commit:
    subject: str
    body: str
    commit_type: str
    description: str
    breaking: bool


CHANGELOG_SECTIONS = (
    "Added",
    "Changed",
    "Deprecated",
    "Removed",
    "Fixed",
    "Security",
)
EXCLUDED_TYPES = {"style", "ci", "build"}
SECTION_BY_TYPE = {
    "feat": "Added",
    "new": "Added",
    "add": "Added",
    "fix": "Fixed",
    "bugfix": "Fixed",
    "revert": "Fixed",
    "security": "Security",
    "perf": "Changed",
    "refactor": "Changed",
    "update": "Changed",
    "change": "Changed",
    "chore": "Changed",
    "setup": "Changed",
    "docs": "Changed",
    "test": "Changed",
    "release": "Changed",
    "deprecate": "Deprecated",
    "remove": "Removed",
    "delete": "Removed",
}
MINOR_TYPES = {"feat", "new", "add"}
PATCH_TYPES = {"fix", "bugfix", "security", "perf", "update", "remove"}


def run(*args: str, capture: bool = False) -> str:
    result = subprocess.run(
        args,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return result.stdout.strip() if capture else ""


def commits_since(tag: str | None) -> list[Commit]:
    revision = f"{tag}..HEAD" if tag else "HEAD"
    raw = run(
        "git",
        "log",
        revision,
        "--no-merges",
        "--format=%s%x00%b%x00",
        capture=True,
    )
    fields = raw.split("\x00")
    commits: list[Commit] = []
    for index in range(0, len(fields) - 1, 2):
        subject = fields[index].strip()
        body = fields[index + 1].strip()
        if not subject:
            continue
        match = COMMIT_PATTERN.match(subject)
        if match:
            commit_type = match.group(1)
            breaking = bool(match.group(4)) or bool(
                re.search(r"BREAKING[- ]CHANGE", body)
            )
            description = match.group(5)
        else:
            commit_type = "other"
            breaking = bool(re.search(r"BREAKING[- ]CHANGE", body))
            description = subject
        commits.append(
            Commit(subject, body, commit_type, description, breaking)
        )
    return commits


def changelog_section(commit: Commit) -> str | None:
    if commit.commit_type in EXCLUDED_TYPES:
        return None
    if commit.breaking:
        return "Changed"
    return SECTION_BY_TYPE.get(commit.commit_type)


def section_lines(commits: list[Commit]) -> list[str]:
    groups: dict[str, list[str]] = {section: [] for section in CHANGELOG_SECTIONS}
    for commit in commits:
        section = changelog_section(commit)
        if section:
            description = (
                f"**BREAKING:** {commit.description}"
                if commit.breaking
                else commit.description
            )
            groups[section].append(f"- {description}")

    lines: list[str] = []
    for section in CHANGELOG_SECTIONS:
        entries = groups[section]
        if entries:
            if lines:
                lines.append("")
            lines.extend((f"### {section}", "", *entries))
    return lines


def changelog_template() -> str:
    return (
        "# Changelog\n\n"
        "All notable changes to this project will be documented in this file.\n\n"
        "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),\n"
        "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\n\n"
        "## [Unreleased]\n"
    )


def replace_unreleased(content: str, replacement: list[str]) -> str:
    lines = content.splitlines()
    try:
        start = next(
            index
            for index, line in enumerate(lines)
            if line.strip() == "## [Unreleased]"
        )
    except StopIteration as error:
        raise RuntimeError("CHANGELOG.md must contain a ## [Unreleased] section") from error

    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("## [")
        ),
        len(lines),
    )
    return "\n".join(lines[: start + 1] + [""] + replacement + [""] + lines[end:]).rstrip() + "\n"


def latest_version_tag() -> tuple[str, tuple[int, int, int]] | None:
    tags: list[tuple[str, tuple[int, int, int]]] = []
    for tag in run("git", "tag", "--list", "v*", capture=True).splitlines():
        match = VERSION_TAG.fullmatch(tag)
        if match:
            tags.append((tag, tuple(int(part) for part in match.groups())))
    return max(tags, key=lambda item: item[1]) if tags else None


def github_release_for_tag(tag: str) -> dict[str, object] | None:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise RuntimeError("GITHUB_REPOSITORY is missing or invalid")
    if not token:
        raise RuntimeError("GH_TOKEN is required to check GitHub Releases")

    url = (
        f"https://api.github.com/repos/{repository}/releases/tags/"
        f"{quote(tag, safe='')}"
    )
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            release = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 404:
            return None
        raise RuntimeError(
            f"GitHub returned HTTP {error.code} while checking release {tag}"
        ) from error
    except URLError as error:
        raise RuntimeError(f"Could not check GitHub Release {tag}") from error

    if release.get("tag_name") != tag:
        raise RuntimeError(f"GitHub returned an unexpected release for {tag}")
    return release


def release_notes_from_changelog(tag: str) -> str:
    version = tag.removeprefix(VERSION_PREFIX)
    with open(CHANGELOG_PATH, encoding="utf-8") as changelog:
        content = changelog.read()

    heading = re.compile(
        rf"^## \[{re.escape(version)}\](?: - .*)?$",
        re.MULTILINE,
    )
    match = heading.search(content)
    if not match:
        raise RuntimeError(f"CHANGELOG.md has no release entry for {tag}")

    end = re.search(r"^## \[", content[match.end():], re.MULTILINE)
    entry_end = match.end() + end.start() if end else len(content)
    return content[match.start():entry_end].strip()


def update_major_tag(tag: str) -> None:
    version = tag.removeprefix(VERSION_PREFIX)
    major_tag = f"{VERSION_PREFIX}{version.split('.')[0]}"
    run(
        "git",
        "tag",
        "--force",
        "--annotate",
        "--message",
        f"🚀 release: {major_tag}",
        major_tag,
        tag,
    )
    run("git", "push", "--force", "origin", f"refs/tags/{major_tag}")


def recover_missing_release(
    latest: tuple[str, tuple[int, int, int]] | None,
) -> None:
    if latest is None:
        return

    tag, _ = latest
    if github_release_for_tag(tag) is not None:
        return

    notes = release_notes_from_changelog(tag)
    if MAJOR_TAGS_ENABLED:
        update_major_tag(tag)
    publish_release(tag, notes)
    print(f"Recovered missing GitHub release {tag}.")


def next_version(
    commits: list[Commit], previous: tuple[int, int, int] | None
) -> tuple[str, str]:
    if previous is None:
        return INITIAL_VERSION, "patch"
    bump = "none"
    for commit in commits:
        message = f"{commit.subject}\n{commit.body}"
        if re.search(r"BREAKING CHANGE|BREAKING-CHANGE|breaking", message) or commit.breaking:
            return f"{previous[0] + 1}.0.0", "major"
        if commit.commit_type in MINOR_TYPES:
            bump = "minor"
        elif commit.commit_type in PATCH_TYPES and bump != "minor":
            bump = "patch"

    if bump == "major":
        return f"{previous[0] + 1}.0.0", bump
    if bump == "minor":
        return f"{previous[0]}.{previous[1] + 1}.0", bump
    if bump == "patch":
        return f"{previous[0]}.{previous[1]}.{previous[2] + 1}", bump
    return ".".join(map(str, previous)), "none"


def write_changelog(commits: list[Commit], version: str | None) -> tuple[bool, str]:
    path = CHANGELOG_PATH
    content = open(path, encoding="utf-8").read() if os.path.exists(path) else changelog_template()
    sections = section_lines(commits)
    if version is None:
        updated = replace_unreleased(content, sections)
        release_entry = ""
    else:
        updated = replace_unreleased(content, [])
        date = dt.datetime.now(dt.timezone.utc).date().isoformat()
        entry_lines = [f"## [{version}] - {date}"]
        if sections:
            entry_lines.extend(("", *sections))
        lines = updated.splitlines()
        unreleased = next(i for i, line in enumerate(lines) if line.strip() == "## [Unreleased]")
        insert_at = next(
            (i for i in range(unreleased + 1, len(lines)) if lines[i].startswith("## [")),
            len(lines),
        )
        lines[insert_at:insert_at] = ["", *entry_lines, ""]
        updated = "\n".join(lines).rstrip() + "\n"
        release_entry = "\n".join(entry_lines)
    changed = not os.path.exists(path) or open(path, encoding="utf-8").read() != updated
    if changed:
        with open(path, "w", encoding="utf-8", newline="\n") as changelog:
            changelog.write(updated)
    return changed, release_entry


def commit_changelog(version_tag: str | None) -> bool:
    if not run("git", "status", "--porcelain", "--", CHANGELOG_PATH, capture=True):
        return False
    run("git", "config", "user.name", GIT_USER_NAME)
    run("git", "config", "user.email", GIT_USER_EMAIL)
    description = (
        f"update CHANGELOG.md for {version_tag}"
        if version_tag
        else "update CHANGELOG.md [Unreleased]"
    )
    run("git", "add", CHANGELOG_PATH)
    run("git", "commit", "-m", f"☕ chore: {description}")
    run("git", "push", "origin", "HEAD:main")
    return True


def publish_release(tag: str, notes: str) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="\n", suffix=".md"
    ) as notes_file:
        notes_file.write(notes)
        notes_file.flush()
        run(
            "gh",
            "release",
            "create",
            tag,
            "--target",
            "main",
            "--title",
            tag,
            "--notes-file",
            notes_file.name,
        )


def main() -> None:
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise RuntimeError("The release workflow must run on main")

    run("git", "fetch", "--tags", "--force", "origin")
    run("git", "fetch", "origin", "main")
    run("git", "checkout", "--detach", "FETCH_HEAD")

    latest = latest_version_tag()
    recover_missing_release(latest)
    previous_tag, previous = latest if latest else (None, None)
    commits = commits_since(previous_tag)

    if previous is None and not run("git", "rev-list", "--count", "HEAD", capture=True):
        print("No commits found; skipping release.")
        return

    version, bump = next_version(commits, previous)
    if bump == "none":
        changed, _ = write_changelog(commits, None)
        if changed and commit_changelog(None):
            print("Updated the [Unreleased] changelog; no release bump was detected.")
        else:
            print("No release bump or changelog update was detected.")
        return

    tag = f"{VERSION_PREFIX}{version}"
    changed, notes = write_changelog(commits, version)
    if not changed:
        raise RuntimeError(f"CHANGELOG.md did not change for {tag}; refusing duplicate release processing")
    if not commit_changelog(tag):
        raise RuntimeError(f"Could not commit CHANGELOG.md for {tag}")

    run("git", "tag", "--annotate", tag, "--message", f"🚀 release: {tag}")
    run("git", "push", "origin", f"refs/tags/{tag}")

    if MAJOR_TAGS_ENABLED:
        update_major_tag(tag)

    publish_release(tag, notes)
    print(f"Created GitHub release {tag}.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"::error::{error}", file=sys.stderr)
        sys.exit(1)
