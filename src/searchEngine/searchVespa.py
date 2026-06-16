"""Pure Python Vespa-like search engine for knowledge prerequisite lookup.

Implements classical Vespa architecture in pure Python:
- Inverted index with term frequencies
- BM25 ranking (k1=1.2, b=0.75)
- Document store with typed fields
- YQL-like query interface
- Convenience methods for Mentor integration
"""

from __future__ import annotations

import math
import re
from pathlib import Path
import json

from testdata import knowledge_base


def _load_base(base: str | None) -> dict[str, list[str]]:
    if base is None:
        return knowledge_base
    return json.loads(Path(base).read_text(encoding="utf-8"))


class SearchVespa:
    """Classical Vespa search engine — pure Python.

    Usage::

        engine = SearchVespa()          # uses built-in knowledge_base
        engine = SearchVespa("data.json")  # loads from JSON file

        # Raw Vespa API
        engine.feed("Python", {"topic": "Python", "prerequisites": []})
        results = engine.query(query="deep learning", hits=5)

        # Prerequisite expansion
        chain = engine.prerequisite_chain("深度学习", max_depth=2)
    """

    # BM25 constants
    _K1: float = 1.2
    _B: float = 0.75

    def __init__(self, base: str | None = None) -> None:
        self._inverted_index: dict[str, dict[str, int]] = {}
        self._doc_store: dict[str, dict] = {}
        self._doc_count: int = 0
        self._total_topic_len: int = 0

        data = _load_base(base)
        self.feed_iterable(data.items())

    # ── indexing ──────────────────────────────────────────

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Classical whitespace + lowercase tokenizer."""
        return text.lower().split()

    def feed(self, doc_id: str, fields: dict) -> None:
        """Index a single document."""
        self._doc_store[doc_id] = fields
        self._doc_count += 1

        topic = fields.get("topic", doc_id)
        tokens = self._tokenize(topic)
        self._total_topic_len += len(tokens)

        seen: set[str] = set()
        for term in tokens:
            if term in seen:
                continue
            seen.add(term)
            tf = tokens.count(term)
            self._inverted_index.setdefault(term, {})[doc_id] = tf

    def feed_iterable(self, items) -> None:
        """Batch-index (topic, prerequisites) pairs."""
        for topic, prereqs in items:
            self.feed(topic, {"topic": topic, "prerequisites": list(prereqs)})

    # ── BM25 ranking ──────────────────────────────────────

    @property
    def _avg_topic_len(self) -> float:
        return self._total_topic_len / max(self._doc_count, 1)

    def _bm25_score(self, query_terms: list[str], doc_id: str) -> float:
        """Compute BM25 between query terms and a document's topic field."""
        doc = self._doc_store[doc_id]
        topic = doc.get("topic", doc_id)
        doc_tokens = self._tokenize(topic)
        doc_len = len(doc_tokens)
        avg_len = self._avg_topic_len

        score = 0.0
        for term in query_terms:
            postings = self._inverted_index.get(term)
            if postings is None or doc_id not in postings:
                continue
            tf = postings[doc_id]
            df = len(postings)

            idf = math.log(1.0 + (self._doc_count - df + 0.5) / (df + 0.5))
            numerator = tf * (self._K1 + 1.0)
            denominator = tf + self._K1 * (1.0 - self._B + self._B * doc_len / avg_len)
            score += idf * numerator / denominator

        return score

    # ── querying ──────────────────────────────────────────

    def query(
        self,
        yql: str | None = None,
        query: str | None = None,
        hits: int = 10,
        ranking: str = "bm25",
    ) -> list[dict]:
        """Execute a Vespa query.

        ``query``   — free-text search on the *topic* field.
        ``yql``     — YQL-like: ``select * from doc where topic contains "..."``
        """
        if query is not None:
            return self._text_query(query, hits)
        if yql is not None:
            return self._yql_query(yql, hits)
        return []

    def _text_query(self, query_text: str, hits: int) -> list[dict]:
        """BM25-ranked full-text search on topic field."""
        query_terms = self._tokenize(query_text)
        if not query_terms:
            return []

        scored: list[tuple[str, float]] = []
        for doc_id in self._doc_store:
            score = self._bm25_score(query_terms, doc_id)
            if score > 0.0:
                scored.append((doc_id, score))

        scored.sort(key=lambda x: (-x[1], x[0]))

        return [
            {
                "id": doc_id,
                "relevance": round(score, 4),
                "fields": self._doc_store[doc_id],
            }
            for doc_id, score in scored[:hits]
        ]

    def _yql_query(self, yql: str, hits: int) -> list[dict]:
        """Lightweight YQL parser: extracts contains-clause query string."""
        match = re.search(r"""contains\s+["']([^"']*)["']""", yql, re.IGNORECASE)
        if match:
            return self._text_query(match.group(1), hits)
        return []

    def get_data(self, doc_id: str) -> dict | None:
        """Retrieve a full document by ID."""
        return self._doc_store.get(doc_id)

    # ── Mentor convenience API ────────────────────────────

    def prerequisite_chain(
        self, knowledge: str, max_depth: int = 3
    ) -> list[tuple[int, str]]:
        """DFS traversal of the prerequisite graph.

        Engine-agnostic: reads edges from the document store directly.
        """
        results: list[tuple[int, str]] = []
        visited: set[str] = set()

        def _append(name: str, depth: int) -> None:
            if depth > max_depth or name in visited:
                return
            visited.add(name)
            doc = self.get_data(name)
            if doc:
                for prerequisite in doc.get("prerequisites", []):
                    results.append((depth, prerequisite))
                    _append(prerequisite, depth + 1)

        _append(knowledge, 1)
        return results
