"""Knowledge base mapping topic names to their prerequisite knowledge."""

from __future__ import annotations

knowledge_base: dict[str, list[str]] = {
    "Python编程": ["计算机基础", "英语基础"],
    "机器学习": ["Python编程", "线性代数", "概率论"],
    "深度学习": ["机器学习", "微积分", "Python编程"],
    "Java开发": ["计算机基础", "面向对象思想"],
    "数据结构": ["Python编程/Java开发", "离散数学"],
    "算法": ["数据结构", "数学逻辑"],
    "MySQL数据库": ["计算机基础", "SQL语法"],
    "网络原理": ["计算机基础"],
    "线性代数": ["高中数学"],
    "微积分": ["高中数学"],
    "概率论": ["高中数学"],
    "离散数学": ["高中数学"],
}

__all__ = ["knowledge_base"]
