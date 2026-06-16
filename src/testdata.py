"""Testing database"""

from __future__ import annotations #be able to annote data type, easier to check bugs

knowledge_base: dict[str, list[str]] = {
    "Python": [],
    "Machine Learning": ["Python", "线性代数", "概率论"],
    "深度学习": ["Machine Learning", "微积分", "Python"],
    "MySQL数据库": ["SQL语法"],
}

__all__ = ["knowledge_base"]
