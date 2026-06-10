from app.evaluation.metrics import (
    citation_coverage,
    hit_rate,
    jaccard,
    precision_at_k,
    recall_at_k,
    theme_coverage,
)


def test_retrieval_metrics():
    expected = {"a", "b"}
    predicted = ["a", "x", "b"]
    assert recall_at_k(expected, predicted, 1) == 0.5
    assert recall_at_k(expected, predicted, 3) == 1.0
    assert precision_at_k(expected, predicted, 2) == 0.5
    assert hit_rate(expected, predicted, 1) == 1.0


def test_text_metrics():
    answer = "Refund timeline is 5 business days. Source: refund_policy"
    assert theme_coverage(answer, ["refund", "business days"]) == 1.0
    assert citation_coverage(answer, ["refund_policy", "shipping_policy"]) == 0.5
    assert jaccard({"a", "b"}, {"b", "c"}) == 1 / 3


if __name__ == "__main__":
    test_retrieval_metrics()
    test_text_metrics()
    print("evaluation metric tests OK")

