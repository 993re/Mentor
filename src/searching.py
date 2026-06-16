"""Search engine: two-part architecture — search + append.
"""

from __future__ import annotations

from testdata import knowledge_base
from pathlib import Path
import json


_vespa_engine = None  # type: ignore[var-annotated]


def _get_vespa(base: str | None = None):
    """Lazy-init the Vespa singleton."""
    global _vespa_engine
    if _vespa_engine is None:
        from searchEngine.searchVespa import SearchVespa

        _vespa_engine = SearchVespa(base)
    return _vespa_engine


def _load_base(base: str | None) -> dict[str, list[str]]:
    if base is None:
        return knowledge_base
    return json.loads(Path(base).read_text(encoding="utf-8"))


def search(
    query: str,
    base: str | None = None,
    engine: str = "dict",
) -> list[str]:
    """Find knowledge topics matching *query*.

    ``engine="dict"``  — case-insensitive substring match on topic names.
    ``engine="vespa"`` — BM25-ranked full-text search via Vespa engine.
    """
    if engine == "vespa":
        results = _get_vespa(base).query(query=query, hits=20)
        return [r["fields"]["topic"] for r in results]

    # engine="dict" (default)
    loaded = _load_base(base)
    query_lower = query.lower()
    return [name for name in loaded if query_lower in name.lower()]
 

def append_match(
    match: str,
    base: str | None = None,
    max_depth: int = 3,
) -> list[tuple[int, str]]:
    loaded = _load_base(base)
    results: list[tuple[int, str]] = []
    visited: set[str] = set()

    def _append(match: str, depth: int) -> None:
        if depth > max_depth or match in visited:
            return
        visited.add(match)
        for prerequisite in loaded.get(match, []):
            results.append((depth, prerequisite)) #finally: match's results == [(2, a), (3, aa), (1, b)]
            _append(prerequisite, depth + 1)

    _append(match, 2)
    return results


if __name__ == "__main__":
    import sys

    print("===== 多层级前置知识查询系统 =====")
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
