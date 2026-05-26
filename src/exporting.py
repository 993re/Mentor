"""Export search results in various formats."""

from __future__ import annotations

from pathlib import Path


EXPORT_MODES = ["None", "Markdown"]


def next_mode(current: str) -> str:
    """Return the next export mode in the cycle."""
    idx = EXPORT_MODES.index(current)
    return EXPORT_MODES[(idx + 1) % len(EXPORT_MODES)]


def to_markdown(
    query: str,
    matches: list[str],
    chains: dict[str, list[tuple[int, str]]],
) -> str:
    """Format prerequisite chains as raw Markdown lines."""
    lines: list[str] = []
    for topic in matches:
        lines.append(f"#{topic}\n")
        for depth, prereq in chains.get(topic, []):
            marker = "#" * (depth + 1)
            lines.append(f"{marker}{prereq}\n")
    return "".join(lines)


def write_file(path: str | Path, content: str) -> None:
    """Write *content* to *path*, creating parent directories if needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
