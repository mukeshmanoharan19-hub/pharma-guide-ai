from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

DATA_DIR = Path("data/evaluation")


@dataclass
class RetrievalCase:
    id: str
    query: str
    relevant_ids: list[str]
    category: str


@dataclass
class RagCase:
    id: str
    query: str
    expected_themes: list[str]
    required_citations: list[str]


@dataclass
class AgentCase:
    id: str
    query: str
    expected_intent: str
    expected_tools: list[str]


def _read_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_retrieval_cases(path: Path | None = None) -> List[RetrievalCase]:
    path = path or DATA_DIR / "gold_retrieval.jsonl"
    return [RetrievalCase(**row) for row in _read_jsonl(path)]


def load_rag_cases(path: Path | None = None) -> List[RagCase]:
    path = path or DATA_DIR / "gold_rag.jsonl"
    return [RagCase(**row) for row in _read_jsonl(path)]


def load_agent_cases(path: Path | None = None) -> List[AgentCase]:
    path = path or DATA_DIR / "gold_agent.jsonl"
    return [AgentCase(**row) for row in _read_jsonl(path)]


def smoke_slice[T](rows: list[T], limit: int) -> list[T]:
    """Deterministic subset for CI smoke runs."""
    if limit <= 0 or len(rows) <= limit:
        return rows
    return rows[:limit]

