import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import pytest
from faithfulness import split_claims, parse_verdict, ParseError

CONTEXT = ("Gecikmə üzrə qayda: 30 gündən çox gecikən kredit Stage 2-yə keçirilir. "
           "Kredit məbləği 10 000 AZN-dən çox olduqda təminat tələb olunur. "
           "Müraciət onlayn və ya filialda edilə bilər.")
ANSWER = ("30 gündən çox gecikən kredit Stage 2-yə keçirilir. "
          "10 000 AZN-dən çox məbləğdə təminat tələb olunur. "
          "Müraciət yalnız onlayn edilə bilər. "
          "Kredit 90 gündən sonra default sayılır.")


def test_split_claims_gives_four_claims():
    assert len(split_claims(ANSWER)) == 4


def test_split_claims_keeps_decimals_together():
    assert split_claims("Faiz 3.5 faizdir.") == ["Faiz 3.5 faizdir."]


@pytest.mark.parametrize("raw,expected", [
    ("SUPPORTED", "SUPPORTED"),
    ("  contradicted. ", "CONTRADICTED"),
    ("UNSUPPORTED", "UNSUPPORTED"),
])
def test_parse_verdict_accepts_labels(raw, expected):
    assert parse_verdict(raw) == expected


def test_parse_verdict_rejects_free_text():
    with pytest.raises(ParseError):
        parse_verdict("Mən düşünürəm ki, SUPPORTED ola bilər")


def test_parse_verdict_strips_thinking_block():
    raw = "Claim is stated in the context directly.\n</think>\n\nSUPPORTED"
    assert parse_verdict(raw) == "SUPPORTED"


def test_parse_verdict_rejects_thinking_without_answer():
    with pytest.raises(ParseError):
        parse_verdict("some reasoning only</think>")


from judge_eval import cohen_kappa


def test_kappa_perfect_agreement_is_one():
    assert cohen_kappa(["SUPPORTED", "CONTRADICTED"], ["SUPPORTED", "CONTRADICTED"]) == 1.0


def test_kappa_chance_level_is_zero():
    a = ["SUPPORTED", "SUPPORTED", "CONTRADICTED", "CONTRADICTED"]
    b = ["SUPPORTED", "CONTRADICTED", "SUPPORTED", "CONTRADICTED"]
    assert abs(cohen_kappa(a, b)) < 1e-9
