"""Built-in knowledge base and grafeo seeding utility."""

from __future__ import annotations

import grafeo

knowledge_base: dict[str, list[str]] = {
    "Python": [],
    "Machine Learning": ["Python", "线性代数", "概率论"],
    "深度学习": ["Machine Learning", "微积分", "Python"],
    "MySQL数据库": ["SQL语法"],
}


def seed_grafeo(db: grafeo.GrafeoDB) -> None:
    """Load the built-in knowledge base into a GrafeoDB instance.

    Creates ``:Knowledge`` nodes with a ``name`` property and
    ``[:REQUIRES]`` edges for prerequisite relationships.
    """
    # ── collect all unique topic names (keys + prerequisite values) ──
    all_topics: set[str] = set(knowledge_base)
    for prereqs in knowledge_base.values():
        all_topics.update(prereqs)

    # ── create nodes ──────────────────────────────────────
    for topic in all_topics:
        db.execute(f'INSERT (:Knowledge {{name: "{topic}"}})')

    # ── create prerequisite edges ─────────────────────────
    for topic, prerequisites in knowledge_base.items():
        for prereq in prerequisites:
            db.execute(
                f'MATCH (a:Knowledge {{name: "{topic}"}}), '
                f'(b:Knowledge {{name: "{prereq}"}}) '
                f'INSERT (a)-[:REQUIRES]->(b)'
            )


__all__ = ["knowledge_base", "seed_grafeo"]
