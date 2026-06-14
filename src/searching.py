"""Search engine: fuzzy topic lookup and prerequisite chain traversal."""

from __future__ import annotations

from database import knowledge_base
from pathlib import Path
import json


def _load_base(base: str | None) -> dict[str, list[str]]:
    if base is None:
        return knowledge_base
    return json.loads(Path(base).read_text(encoding='utf-8'))


def fuzzy_search(query: str, base: str | None = None) -> list[str]:
    """Return knowledge topics whose names contain *query* (case-insensitive)."""
    loaded = _load_base(base)
    query_lower = query.lower()
    return [name for name in loaded if query_lower in name.lower()]


def depth0(
    topic: str,
    base: str | None = None,
) -> list[str]:
    """Return immediate prerequisites of *topic* (depth 0 neighbours)."""
    loaded = _load_base(base)
    return list(loaded.get(topic, []))


def prerequisite_chain(
    knowledge: str,
    base: str | None = None,
    max_depth: int = 3,
) -> list[tuple[int, str]]:
    """Return a flat list of *(depth, topic)* for the prerequisite tree.

    Depth 1 = depth0 prerequisites, depth 2 = prerequisites of those, etc.
    Handles cycles and missing entries gracefully.
    Composes *depth0* internally for neighbour lookup.
    """
    results: list[tuple[int, str]] = []
    visited: set[str] = set()

    def _dfs(name: str, depth: int) -> None:
        if depth > max_depth or name in visited:
            return
        visited.add(name)
        for prerequisite in depth0(name, base):
            results.append((depth, prerequisite))
            _dfs(prerequisite, depth + 1)

    _dfs(knowledge, 1)
    return results


def main() -> None:
    """CLI interface for quick testing."""
    print("===== 多层级前置知识查询系统 =====")
    user_input = input("请输入知识名称：")

    while True:
        depth_input = input("请输入最大展开深度（数字，如1/2/3）：")
        if depth_input.isdigit():
            max_depth = int(depth_input)
            break
        print("请输入有效数字！")

    matches = fuzzy_search(user_input)
    if not matches:
        print("未找到匹配的知识！")
        return

    for topic in matches:
        print(f"\n=== {topic} ===")
        chain = prerequisite_chain(topic, max_depth=max_depth)
        if not chain:
            print("  (无已知前置知识)")
        for depth, prereq in chain:
            prefix = "#" * depth
            print(f"  {prefix} {prereq}")


if __name__ == "__main__":
    main()
