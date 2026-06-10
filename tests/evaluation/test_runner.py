from pathlib import Path

from app.evaluation.runner import run


def test_offline_smoke_runner():
    exit_code = run(smoke=True, offline=True, strict=True, smoke_limit_per_set=3)
    assert exit_code == 0
    assert Path("logs/evaluation/latest.json").exists()


if __name__ == "__main__":
    test_offline_smoke_runner()
    print("evaluation runner smoke test OK")

