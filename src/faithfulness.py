"""Faithfulness kernel: cavabdakı hər iddianın parçaya görə dəstəklənib-dəstəklənmədiyini yoxlayır."""
import re
import requests
from dataclasses import dataclass

OLLAMA_URL = "http://localhost:11434/api/chat"
JUDGE_MODEL = "qwen3:4b"
LABELS = ("SUPPORTED", "CONTRADICTED", "UNSUPPORTED")

JUDGE_PROMPT = """You are checking one claim against a context.
Context:
{context}

Claim: {claim}

Is the claim SUPPORTED by the context, CONTRADICTED by it, or UNSUPPORTED (not stated and not implied)?
Answer with exactly one word: SUPPORTED, CONTRADICTED, or UNSUPPORTED."""


class ParseError(ValueError):
    """Hakimin cavabı üç etiketdən biri deyilsə atılır. Sükutla UNSUPPORTED sayılmır."""


@dataclass
class ClaimResult:
    claim: str
    verdict: str  # SUPPORTED | CONTRADICTED | UNSUPPORTED


def split_claims(answer: str) -> list[str]:
    # Cümlə sonu (. ! ?) ilə bölür. Nöqtədən sonra boşluq olmalıdır ki, "10.5" kimi rəqəmlər bölünməsin.
    parts = re.split(r"(?<=[.!?])\s+", answer.strip())
    return [p.strip() for p in parts if p.strip()]


def parse_verdict(raw: str) -> str:
    text = raw.strip().upper().strip(".!* ")
    if text in LABELS:
        return text
    raise ParseError(f"Hakim üç etiketdən birini qaytarmadı: {raw!r}")


def judge(claim: str, context: str, timeout: int = 120) -> str:
    payload = {
        "model": JUDGE_MODEL,
        "stream": False,
        "think": False,
        "options": {"temperature": 0},
        "messages": [{
            "role": "user",
            "content": JUDGE_PROMPT.format(context=context, claim=claim),
        }],
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    r.raise_for_status()
    return parse_verdict(r.json()["message"]["content"])


def faithfulness(answer: str, context: str) -> tuple[float, list[ClaimResult]]:
    claims = split_claims(answer)
    if not claims:
        raise ValueError("Cavabda iddia tapılmadı")
    results = [ClaimResult(c, judge(c, context)) for c in claims]
    supported = sum(r.verdict == "SUPPORTED" for r in results)
    return supported / len(results), results
