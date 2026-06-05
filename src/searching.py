"""Search engine: fuzzy topic lookup and prerequisite chain traversal."""

from __future__ import annotations

from database import knowledge_base
from pathlib import Path
import json

def fuzzy_search(query: str, base: dict[str, list[str]] | None = None) -> list[str]:
    """Return knowledge topics whose names contain *query* (case-insensitive)."""
    if not base:
        base = knowledge_base
    else:
        base = json.loads(Path(base).read_text(encoding='utf-8'))
    query_lower = query.lower()
    return [name for name in base if query_lower in name.lower()]


def prerequisite_chain(
    knowledge: str,
    base: dict[str, list[str]] | None = None,
    max_depth: int = 3,
) -> list[tuple[int, str]]:
    """Return a flat list of *(depth, topic)* for the prerequisite tree.

    Depth 1 = direct prerequisites, depth 2 = prerequisites of those, etc.
    Handles cycles and missing entries gracefully.
    """
    if not base:
        base = knowledge_base
    else:
        base = json.loads(Path(base).read_text(encoding='utf-8'))
    results: list[tuple[int, str]] = []
    visited: set[str] = set()

    def _dfs(name: str, depth: int) -> None:
        if depth > max_depth or name in visited:
            return
        visited.add(name)
        for prerequisite in base.get(name, []):
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
