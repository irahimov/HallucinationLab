import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from retrieval_eval import metrics


def test_metrics_perfect():
    m = metrics([1, 1, 1])
    assert m["hit@1"] == 1.0 and m["mrr"] == 1.0


def test_metrics_mixed():
    m = metrics([1, 2, 4])
    assert m["hit@1"] == round(1 / 3, 3)
    assert m["hit@3"] == round(2 / 3, 3)
    assert m["mrr"] == round((1 + 0.5 + 0.25) / 3, 3)
