from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger

from app.evaluation.agent_eval import evaluate_agent
from app.evaluation.datasets import (
    load_agent_cases,
    load_rag_cases,
    load_retrieval_cases,
    smoke_slice,
)
from app.evaluation.rag_eval import evaluate_rag
from app.evaluation.retrieval_eval import evaluate_retrieval

REPORTS_DIR = Path("logs/evaluation")

DEFAULT_THRESHOLDS = {
    "retrieval.hit_rate": 0.40,
    "rag.answer_relevancy": 0.55,
    "agent.routing_accuracy": 0.60,
    "agent.task_completion_accuracy": 0.50,
}


def _get_nested(data: dict, dotted_key: str) -> float:
    cur = data
    for part in dotted_key.split("."):
        cur = cur[part]
    return float(cur)


def _read_threshold_env(overrides: dict[str, float]) -> dict[str, float]:
    out = dict(overrides)
    mapping = {
        "EVAL_THRESHOLD_RETRIEVAL_HIT_RATE": "retrieval.hit_rate",
        "EVAL_THRESHOLD_RAG_ANSWER_RELEVANCY": "rag.answer_relevancy",
        "EVAL_THRESHOLD_AGENT_ROUTING_ACCURACY": "agent.routing_accuracy",
        "EVAL_THRESHOLD_AGENT_TASK_COMPLETION": "agent.task_completion_accuracy",
    }
    for env_name, metric in mapping.items():
        value = os.getenv(env_name)
        if value is None:
            continue
        try:
            out[metric] = float(value)
        except ValueError:
            logger.warning(f"Invalid {env_name}='{value}', keeping default.")
    return out


def _save_report(report: dict) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = REPORTS_DIR / f"report_{ts}.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (REPORTS_DIR / "latest.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return path


def run(
    *,
    smoke: bool,
    offline: bool,
    strict: bool,
    smoke_limit_per_set: int,
) -> int:
    live = not offline
    retrieval_cases = load_retrieval_cases()
    rag_cases = load_rag_cases()
    agent_cases = load_agent_cases()

    if smoke:
        retrieval_cases = smoke_slice(retrieval_cases, smoke_limit_per_set)
        rag_cases = smoke_slice(rag_cases, smoke_limit_per_set)
        agent_cases = smoke_slice(agent_cases, smoke_limit_per_set)

    logger.info(
        "Running eval (smoke={} live={}) with cases: retrieval={}, rag={}, agent={}",
        smoke,
        live,
        len(retrieval_cases),
        len(rag_cases),
        len(agent_cases),
    )

    retrieval = evaluate_retrieval(retrieval_cases, live=live)
    rag = evaluate_rag(rag_cases, live=live)
    agent = evaluate_agent(agent_cases, live=live)

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": {
            "smoke": smoke,
            "offline": offline,
            "live": live,
            "strict": strict,
        },
        "retrieval": retrieval,
        "rag": rag,
        "agent": agent,
    }

    thresholds = _read_threshold_env(DEFAULT_THRESHOLDS)
    checks = []
    for metric, threshold in thresholds.items():
        value = _get_nested(report, metric)
        passed = value >= threshold
        checks.append(
            {
                "metric": metric,
                "value": value,
                "threshold": threshold,
                "passed": passed,
            }
        )
    report["checks"] = checks
    report["passed"] = all(x["passed"] for x in checks)
    path = _save_report(report)

    logger.info(
        "Eval summary -> retrieval.hit_rate={:.3f}, rag.answer_relevancy={:.3f}, "
        "agent.routing_accuracy={:.3f}, agent.task_completion_accuracy={:.3f}",
        retrieval["hit_rate"],
        rag["answer_relevancy"],
        agent["routing_accuracy"],
        agent["task_completion_accuracy"],
    )
    logger.info(f"Evaluation report: {path}")

    if strict and not report["passed"]:
        logger.error("Threshold checks failed in strict mode.")
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 9 evaluation suite.")
    parser.add_argument("--smoke", action="store_true", help="Run small smoke subset.")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Do not call LLM APIs; use deterministic offline evaluators.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail (non-zero exit) if threshold checks fail.",
    )
    parser.add_argument(
        "--smoke-limit-per-set",
        type=int,
        default=7,
        help="Max cases per dataset for smoke mode.",
    )
    args = parser.parse_args()

    # Auto-fallback to offline mode if no API key is set.
    if not args.offline and not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY missing; forcing offline evaluation mode.")
        args.offline = True

    return run(
        smoke=args.smoke,
        offline=args.offline,
        strict=args.strict,
        smoke_limit_per_set=args.smoke_limit_per_set,
    )


if __name__ == "__main__":
    sys.exit(main())

