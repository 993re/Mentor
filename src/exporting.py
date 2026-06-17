"""Export search results in various formats."""

from __future__ import annotations

from pathlib import Path

import grafeo

EXPORT_MODES = ["None", "Markdown", "Mermaid", "Grafeo"]


def next_mode(current: str) -> str:
    """Return the next export mode in the cycle."""
    idx = EXPORT_MODES.index(current)
    return EXPORT_MODES[(idx + 1) % len(EXPORT_MODES)]


# ── shared helpers ──────────────────────────────────────────────

def _reconstruct_edges(
    chain: list[tuple[int, str]],
    match: str,
) -> list[tuple[str, str]]:
    """Reconstruct parent→child edges from a flat depth chain.

    The DFS-order chain is emitted by ``append_match()``.  Because DFS
    visits children immediately after their parent, the closest preceding
    item at *depth − 1* is the parent.
    """
    edges: list[tuple[str, str]] = []
    last_at_depth: dict[int, str] = {1: match}

    for depth, name in chain:
        parent = last_at_depth.get(depth - 1, match)
        edges.append((parent, name))
        last_at_depth[depth] = name

    return edges


# ── Markdown ────────────────────────────────────────────────────

def to_markdown(
    query: str,
    matches: list[str],
    chains_db: dict[str, list[tuple[int, str]]],
) -> str:
    """Format prerequisite chains as nested Markdown headings."""
    lines: list[str] = [f"# {query}\n"]
    for topic in matches:
        lines.append(f"## {topic}\n")
        for depth, prereq in chains_db.get(topic, []):
            marker = "#" * (depth + 1)
            lines.append(f"{marker} {prereq}\n")
    return "".join(lines)


# ── Mermaid ─────────────────────────────────────────────────────

def to_mermaid(
    query: str,
    matches: list[str],
    chains_db: dict[str, list[tuple[int, str]]],
) -> str:
    """Render the full prerequisite graph as a Mermaid flowchart.

    Nodes are deduplicated by name so that a topic appearing as a
    prerequisite for multiple parents is shown as a single node with
    multiple incoming edges.
    """
    lines: list[str] = ["flowchart TD"]

    # unique node-id generator
    node_ids: dict[str, str] = {}
    _emitted: set[str] = set()
    _counter: int = 0

    def _node_id(name: str) -> str:
        nonlocal _counter
        if name not in node_ids:
            node_ids[name] = f"n{_counter}"
            _counter += 1
        return node_ids[name]

    def _emit_node(name: str) -> None:
        if name in _emitted:
            return
        _emitted.add(name)
        nid = _node_id(name)
        # escape double-quotes inside the label
        safe = name.replace('"', "'")
        lines.append(f'    {nid}["{safe}"]')

    def _emit_edge(src: str, dst: str) -> None:
        lines.append(f"    {_node_id(src)} --> {_node_id(dst)}")

    # ── query node ──────────────────────────────────────────
    _emit_node(query)

    for match in matches:
        _emit_node(match)
        if match != query:  # skip self-loop when query text equals match name
            _emit_edge(query, match)

        chain = chains_db.get(match, [])
        for parent, child in _reconstruct_edges(chain, match):
            _emit_node(child)
            _emit_edge(parent, child)

    return "\n".join(lines) + "\n"


# ── Grafeo ──────────────────────────────────────────────────────

def to_grafeo(
    query: str,
    matches: list[str],
    chains_db: dict[str, list[tuple[int, str]]],
    path: str | Path,
) -> None:
    """Export the search results as a native grafeo database file.

    Creates ``:Knowledge`` nodes with a ``name`` property and
    ``[:REQUIRES]`` edges for the prerequisite graph, plus
    ``[:SEARCHED]`` edges from the query to each match.
    """
    p = Path(path)

    # remove existing file for a clean export
    if p.exists():
        p.unlink()

    db = grafeo.GrafeoDB(str(p))
    created: set[str] = set()

    def _ensure_node(name: str) -> None:
        if name not in created:
            safe = name.replace('"', "'")
            db.execute(f'INSERT (:Knowledge {{name: "{safe}"}})')
            created.add(name)

    def _ensure_edge(src: str, dst: str, etype: str) -> None:
        safe_src = src.replace('"', "'")
        safe_dst = dst.replace('"', "'")
        db.execute(
            f'MATCH (a:Knowledge {{name: "{safe_src}"}}), '
            f'(b:Knowledge {{name: "{safe_dst}"}}) '
            f"INSERT (a)-[:{etype}]->(b)"
        )

    _ensure_node(query)

    for match in matches:
        _ensure_node(match)
        if match != query:
            _ensure_edge(query, match, "SEARCHED")

        chain = chains_db.get(match, [])
        for parent, child in _reconstruct_edges(chain, match):
            _ensure_node(child)
            _ensure_edge(parent, child, "REQUIRES")

    db.close()


# ── file I/O ────────────────────────────────────────────────────

def write_file(path: str | Path, content: str) -> None:
    """Write *content* to *path*, creating parent directories if needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
