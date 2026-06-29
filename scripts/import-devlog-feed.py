#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List

ENTRY_PATTERN = re.compile(r"<!-- ENTRY:START -->(.*?)<!-- ENTRY:END -->", re.DOTALL)
FIELD_PATTERN = re.compile(r"^(date|project|repo|agent|session_duration):\s*(.+)$", re.MULTILINE)
SECTION_PATTERN = re.compile(
    r"^### Summary\n(?P<summary>.*?)(?=^### Decisions made\n)"
    r"^### Decisions made\n(?P<decisions>.*?)(?=^### Interesting discoveries\n)"
    r"^### Interesting discoveries\n(?P<discoveries>.*?)(?=^### What's next\n)"
    r"^### What's next\n(?P<next>.*)$",
    re.DOTALL | re.MULTILINE,
)
PROJECT_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}-(.+)$")
TAG_PATTERN = re.compile(r"[A-Za-z0-9]+")
SENSITIVE_PATTERN = re.compile(
    r"(?i)(api[_ -]?key|access[_ -]?token|secret|password|passwd|private key|authorization:|bearer\s+[A-Za-z0-9._-]+)"
)
SOURCE_ENTRY_ID_PATTERN = re.compile(r"^sourceEntryIds:\s*$", re.MULTILINE)
SOURCE_ENTRY_ID_VALUE_PATTERN = re.compile(r'^\s*-\s*"(?P<id>[0-9a-f]{64})"\s*$', re.MULTILINE)


@dataclass
class FeedEntry:
    entry_id: str
    raw: str
    entry_date: date
    project: str
    repo: str
    agent: str
    session_duration: str
    summary: str
    decisions: List[str]
    discoveries: List[str]
    next_steps: List[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import new devlog feed entries into content/devlog.")
    parser.add_argument(
        "--feed",
        default="~/dev-journal/DEVLOG_FEED.md",
        help="Path to the shared devlog feed file.",
    )
    parser.add_argument(
        "--output-dir",
        default="content/devlog",
        help="Directory where new devlog posts should be created.",
    )
    return parser.parse_args()


def parse_bullets(block: str) -> List[str]:
    return [line[2:].strip() for line in block.strip().splitlines() if line.strip().startswith("- ")]


def parse_entry(raw_entry: str) -> FeedEntry:
    fields = dict(FIELD_PATTERN.findall(raw_entry))
    sections = SECTION_PATTERN.search(raw_entry)
    if not sections:
        raise ValueError("Feed entry is missing one or more required sections.")

    raw_date = fields.get("date")
    project = fields.get("project")
    repo = fields.get("repo")
    agent = fields.get("agent")
    session_duration = fields.get("session_duration")
    if not all([raw_date, project, repo, agent, session_duration]):
        raise ValueError("Feed entry is missing one or more required fields.")

    normalized_raw = raw_entry.strip()
    return FeedEntry(
        entry_id=hashlib.sha256(normalized_raw.encode("utf-8")).hexdigest(),
        raw=normalized_raw,
        entry_date=date.fromisoformat(raw_date),
        project=project.strip(),
        repo=repo.strip(),
        agent=agent.strip(),
        session_duration=session_duration.strip(),
        summary=sections.group("summary").strip(),
        decisions=parse_bullets(sections.group("decisions")),
        discoveries=parse_bullets(sections.group("discoveries")),
        next_steps=parse_bullets(sections.group("next")),
    )


def latest_devlog_date(output_dir: Path) -> date | None:
    latest: date | None = None
    for path in output_dir.iterdir():
        if not path.is_dir():
            continue
        match = PROJECT_PATTERN.match(path.name)
        if not match:
            continue
        entry_date = date.fromisoformat(path.name[:10])
        if latest is None or entry_date > latest:
            latest = entry_date
    return latest


def sanitize_slug(value: str) -> str:
    slug = "-".join(TAG_PATTERN.findall(value.lower()))
    return slug or "devlog"


def next_post_dir(output_dir: Path, base_name: str) -> Path:
    candidate = output_dir / base_name
    if not candidate.exists():
        return candidate

    suffix = 2
    while True:
        candidate = output_dir / f"{base_name}-{suffix}"
        if not candidate.exists():
            return candidate
        suffix += 1


def summarize_tags(entries: List[FeedEntry]) -> List[str]:
    tags: List[str] = []
    for entry in entries:
        project_tag = sanitize_slug(entry.project)
        if project_tag not in tags:
            tags.append(project_tag)
        agent_tag = sanitize_slug(entry.agent)
        if agent_tag not in tags:
            tags.append(agent_tag)
    return tags[:6]


def ensure_safe(entries: List[FeedEntry]) -> None:
    for entry in entries:
        if SENSITIVE_PATTERN.search(entry.raw):
            raise ValueError(f"Sensitive-looking content detected in feed entry for {entry.project} on {entry.entry_date}.")


def imported_entry_ids(output_dir: Path) -> set[str]:
    imported_ids: set[str] = set()
    for path in output_dir.rglob("index.md"):
        content = path.read_text()
        if not SOURCE_ENTRY_ID_PATTERN.search(content):
            continue
        imported_ids.update(match.group("id") for match in SOURCE_ENTRY_ID_VALUE_PATTERN.finditer(content))
    return imported_ids


def build_post(entries: List[FeedEntry]) -> str:
    post_date = max(entry.entry_date for entry in entries)
    title = f"{entries[0].project}: AI dev log"
    description = entries[0].summary.splitlines()[0]
    tags = ", ".join(f'"{tag}"' for tag in summarize_tags(entries))
    source_entry_ids = "\n".join(f'  - "{entry.entry_id}"' for entry in entries)
    projects = "\n".join(
        f"  - name: \"{entry.project}\"\n    url: \"{entry.repo}\""
        for entry in {entry.project: entry for entry in entries}.values()
    )
    body_parts = [f"*This entry was drafted from the shared devlog feed by an AI agent and should be reviewed before publishing.*\n"]
    for entry in entries:
        body_parts.append(f"## {entry.entry_date.isoformat()} — {entry.project}\n")
        body_parts.append(f"**Agent:** {entry.agent}  ")
        body_parts.append(f"**Session length:** {entry.session_duration}\n")
        body_parts.append(f"{entry.summary}\n")
        if entry.decisions:
            body_parts.append("### Decisions made\n")
            body_parts.extend(f"- {item}\n" for item in entry.decisions)
        if entry.discoveries:
            body_parts.append("### Interesting discoveries\n")
            body_parts.extend(f"- {item}\n" for item in entry.discoveries)
        if entry.next_steps:
            body_parts.append("### What's next\n")
            body_parts.extend(f"- {item}\n" for item in entry.next_steps)
        body_parts.append("\n")

    return (
        f"---\n"
        f"title: \"{title}\"\n"
        f"date: {post_date.isoformat()}\n"
        f"description: \"{description}\"\n"
        f"tags: [{tags}]\n"
        f"sourceEntryIds:\n{source_entry_ids}\n"
        f"projects:\n{projects}\n"
        f"draft: true\n"
        f"---\n\n"
        + "".join(body_parts)
    )


def main() -> int:
    args = parse_args()
    feed_path = Path(args.feed).expanduser()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not feed_path.exists():
        raise SystemExit(f"Feed file not found: {feed_path}")

    raw_feed = feed_path.read_text()
    entries = [parse_entry(match.group(1)) for match in ENTRY_PATTERN.finditer(raw_feed)]
    ensure_safe(entries)

    already_imported = imported_entry_ids(output_dir)
    if already_imported:
        pending = [entry for entry in entries if entry.entry_id not in already_imported]
    else:
        latest_published = latest_devlog_date(output_dir)
        pending = [entry for entry in entries if latest_published is None or entry.entry_date > latest_published]
    if not pending:
        print("No new devlog entries to import.")
        return 0

    slug = sanitize_slug(pending[0].project)
    post_dir = next_post_dir(output_dir, f"{max(entry.entry_date for entry in pending).isoformat()}-{slug}")
    post_dir.mkdir(parents=True, exist_ok=False)
    post_path = post_dir / "index.md"
    post_path.write_text(build_post(pending))
    print(post_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
