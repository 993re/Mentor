"""Search engine powered by grafeo — a graph-native database.

Two search backends:
  ``"dict"``    — case-insensitive substring match on topic names.
  ``"grafeo"``  — BM25 full-text search via grafeo's built-in text index.
"""

from __future__ import annotations

import grafeo
from testdata import seed_grafeo

# ── database singleton ────────────────────────────────────────

_db: grafeo.GrafeoDB | None = None
_db_path: str | None = None
_text_index_ready: bool = False


def _get_db(base: str | None) -> grafeo.GrafeoDB:
    """Return (and cache) a GrafeoDB for *base*.

    * ``None``          → in-memory DB seeded with built-in data.
    * ``"path/to.db"``  → persistent file opened via grafeo.
    """
    global _db, _db_path, _text_index_ready

    # same database — reuse
    if _db is not None and base == _db_path:
        return _db

    # different database — close old, open new
    if _db is not None:
        _db.close()
        _db = None
        _db_path = None
        _text_index_ready = False

    if base is None:
        _db = grafeo.GrafeoDB()
        seed_grafeo(_db)
    else:
        _db = grafeo.GrafeoDB(base)

    _db_path = base
    return _db


def _ensure_text_index(db: grafeo.GrafeoDB) -> None:
    """Create the BM25 text index on :Knowledge.name if not already done."""
    global _text_index_ready
    if not _text_index_ready:
        db.create_text_index("Knowledge", "name")
        _text_index_ready = True


# ── search ────────────────────────────────────────────────────

def search(
    query: str,
    base: str | None = None,
    engine: str = "dict",
) -> list[str]:
    """Return knowledge topics matching *query*.

    ``engine="dict"``    — case-insensitive substring match (default).
    ``engine="grafeo"``  — BM25-ranked full-text search.
    """
    db = _get_db(base)

    if engine == "grafeo":
        _ensure_text_index(db)
        scored: list[tuple[int, float]] = db.text_search(
            "Knowledge", "name", query, k=20,
        )
        names: list[str] = []
        for node_id, _score in scored:
            node = db.get_node(node_id)
            if node is not None:
                props = node.properties()
                if props:
                    names.append(props.get("name", ""))
        return names

    # engine="dict" — substring match
    result = db.execute("MATCH (n:Knowledge) RETURN n.name")
    query_lower = query.lower()
    return [row["n.name"] for row in result if query_lower in row["n.name"].lower()]


# ── prerequisite expansion ────────────────────────────────────

def append_match(
    match: str,
    base: str | None = None,
    max_depth: int = 3,
) -> list[tuple[int, str]]:
    """DFS traversal of the prerequisite graph starting from *match*.

    Returns ``[(depth, prerequisite_name), ...]`` where *depth* starts
    at 2 for direct prerequisites.
    """
    db = _get_db(base)
    results: list[tuple[int, str]] = []
    visited: set[str] = set()

    def _append(name: str, depth: int) -> None:
        if depth > max_depth or name in visited:
            return
        visited.add(name)
        rows = db.execute(
            f'MATCH (n:Knowledge {{name: "{name}"}})-[:REQUIRES]->(p:Knowledge) '
            f"RETURN p.name"
        )
        for row in rows:
            prereq = row["p.name"]
            results.append((depth, prereq))
            _append(prereq, depth + 1)

    _append(match, 2)
    return results


# ── CLI demo ──────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("===== 多层级前置知识查询系统 (grafeo) =====")
    user_input = input("请输入知识名称：")

    while True:
        depth_input = input("请输入最大展开深度（数字，如1/2/3）：")
        if depth_input.isdigit():
            max_depth = int(depth_input)
            break
        print("请输入有效数字！")

    matches = search(user_input)
    if not matches:
        print("未找到匹配的知识！")
        sys.exit(0)

    for topic in matches:
        print(f"\n=== {topic} ===")
        chain = append_match(topic, max_depth=max_depth)
        if not chain:
            print("  (无已知前置知识)")
        for depth, prereq in chain:
            prefix = "#" * depth
            print(f"  {prefix} {prereq}")
