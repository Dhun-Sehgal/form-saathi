"""LLM adapter for Saathi AI (Anthropic Claude).

The API key lives only on the server (LLM_API_KEY). When it is missing, is_configured() is
False and every AI endpoint answers 503 "ai_not_configured" — nothing pretends to work.
"""
from __future__ import annotations

import json
import logging

from flask import current_app

log = logging.getLogger("formsaathi.llm")

LANGUAGE_NAMES = {"en": "English", "hi": "Hindi (Devanagari script)", "mr": "Marathi (Devanagari script)"}

SAATHI_SYSTEM = """You are Saathi AI, the application assistant inside FormSaathi, an app that helps Indian \
students and citizens find opportunities (scholarships, internships, schemes, exams, jobs) and complete applications.

How to help:
- Explain forms, instructions and difficult English or bureaucratic terms in simple, friendly language.
- Help users make document checklists and plan their application steps.
- Keep answers short and scannable: a sentence or two, then bullets or numbered steps when useful.
- Reply in {language}. If the user writes in a different language, reply in the language they used.

Accuracy rules (very important):
- Never invent eligibility rules, deadlines, amounts, documents, or website links.
- When an OPPORTUNITY RECORD is provided below, rely only on it for facts about that opportunity. If it doesn't \
contain the answer, say so and tell the user to check the official source link.
- If the record is marked as DEMO data, remind the user it is sample data, not a real opportunity.
- General explanations (what a domicile certificate is, what "non-creamy layer" means) are fine, but say rules \
can differ between states and schemes.
- You are not a government official. Do not promise approval or eligibility.
- Never ask for Aadhaar numbers, bank account numbers, passwords or OTPs.
"""


class AIUnavailable(Exception):
    pass


def is_configured() -> bool:
    return bool(current_app.config.get("LLM_API_KEY"))


def _client():
    import anthropic

    return anthropic.Anthropic(api_key=current_app.config["LLM_API_KEY"], timeout=60.0, max_retries=2)


def _create(**kwargs):
    import anthropic

    if not is_configured():
        raise AIUnavailable("Saathi AI is not configured on this server.")
    try:
        return _client().beta.messages.create(
            model=current_app.config["LLM_MODEL"],
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            **kwargs,
        )
    except anthropic.AuthenticationError as e:
        log.error("LLM authentication failed: %s", e)
        raise AIUnavailable("Saathi AI is misconfigured (invalid API key).") from e
    except anthropic.RateLimitError as e:
        raise AIUnavailable("Saathi AI is busy right now. Please try again in a minute.") from e
    except anthropic.APIStatusError as e:
        log.error("LLM API error %s: %s", e.status_code, e.message)
        raise AIUnavailable("Saathi AI couldn't answer right now. Please try again.") from e
    except anthropic.APIConnectionError as e:
        raise AIUnavailable("Couldn't reach the AI service. Please try again.") from e


def _text(response) -> str:
    return "".join(b.text for b in response.content if getattr(b, "type", None) == "text").strip()


def chat(system: str, messages: list[dict]) -> dict:
    response = _create(
        max_tokens=4000,
        system=system,
        messages=messages,
        output_config={"effort": "low"},
    )
    if response.stop_reason == "refusal":
        text = "Sorry, I can't help with that request. Please ask something about your opportunities or applications."
    else:
        text = _text(response) or "Sorry, I couldn't put together an answer. Could you rephrase?"
    usage = getattr(response, "usage", None)
    return {
        "content": text,
        "model": getattr(response, "model", None),
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
    }


EXPLANATION_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "criteria": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"index": {"type": "integer"}, "explanation": {"type": "string"}},
                "required": ["index", "explanation"],
                "additionalProperties": False,
            },
        },
        "next_steps": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "criteria", "next_steps"],
    "additionalProperties": False,
}


def explain_eligibility(title: str, report: dict, language: str) -> dict:
    """Ask the model to explain an already-computed verdict. It may not change the verdict."""
    payload = {
        "opportunity": title,
        "verdict": report["verdict"],
        "rules": [
            {"index": i, "rule": r["description"], "official_text": r["source_excerpt"],
             "outcome": r["outcome"], "engine_reason": r["reason"], "mandatory": r["is_mandatory"]}
            for i, r in enumerate(report["results"])
        ],
    }
    prompt = (
        "A rule engine has already checked a student's eligibility. Explain the result in simple "
        f"{LANGUAGE_NAMES.get(language, 'English')} for a student. Do NOT change the verdict or any outcome, "
        "do not add rules, amounts or dates that are not in the data. One short explanation per rule (by index), "
        "a 1-2 sentence summary, and 2-4 practical next steps.\n\n" + json.dumps(payload, ensure_ascii=False)
    )
    response = _create(
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": EXPLANATION_SCHEMA}},
    )
    if response.stop_reason == "refusal":
        raise AIUnavailable("AI explanation unavailable for this request.")
    data = json.loads(_text(response))
    if not isinstance(data.get("summary"), str) or not isinstance(data.get("next_steps"), list):
        raise ValueError("bad explanation shape")
    per = {c["index"]: c["explanation"] for c in data.get("criteria", []) if isinstance(c, dict)}
    return {"summary": data["summary"], "next_steps": [str(s) for s in data["next_steps"]][:5], "per_criterion": per}


BULLET_SCHEMA = {
    "type": "object",
    "properties": {"suggestions": {"type": "array", "items": {"type": "string"}}},
    "required": ["suggestions"],
    "additionalProperties": False,
}


def improve_bullet(bullet: str, role: str = "") -> list[str]:
    """Rewrite one resume bullet into 3 stronger, ATS-friendly versions without inventing facts."""
    prompt = (
        "Rewrite this resume bullet into 3 stronger, ATS-friendly alternatives"
        + (f" for a {role} resume" if role else "")
        + ". Rules: start with a strong past-tense action verb; keep it to one line (under 30 words); keep every "
        "fact, tool and number from the original; NEVER invent numbers, results, tools or employers — where a metric "
        "would help but is not given, insert a placeholder like [X%] or [N users] for the student to fill in; no first "
        "person; plain text only.\n\nOriginal bullet: " + bullet
    )
    response = _create(
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": BULLET_SCHEMA}},
    )
    if response.stop_reason == "refusal":
        raise AIUnavailable("AI couldn't rewrite this bullet.")
    data = json.loads(_text(response))
    out = [str(s).strip() for s in data.get("suggestions", []) if str(s).strip()]
    if not out:
        raise ValueError("empty suggestions")
    return out[:3]
