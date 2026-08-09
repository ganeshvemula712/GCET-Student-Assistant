import json
import re
import time
from typing import Generator

from backend.app.core.prompts import (
    GENERAL_SYSTEM_PROMPT,
    RAG_SYSTEM_PROMPT,
)
from backend.app.services.gemini import client

MODELS_FALLBACK_ORDER = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
]


def _extract_json_block(text: str) -> dict:
    match = re.search(r"```json\s*(.*?)```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def _generate_content_with_fallback(prompt: str):
    last_err = None
    for model_name in MODELS_FALLBACK_ORDER:
        try:
            res = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if res and res.text:
                return res
        except Exception as e:
            last_err = e
            time.sleep(0.5)
            continue
    if last_err:
        raise last_err
    raise RuntimeError("All Gemini models failed.")


def _stream_answer(prompt: str) -> Generator[str, None, None]:
    """Yield displayable Markdown tokens with automatic model fallback."""
    last_err = None
    for model_name in MODELS_FALLBACK_ORDER:
        try:
            stream = client.models.generate_content_stream(
                model=model_name,
                contents=prompt,
            )
            has_yielded = False
            for chunk in stream:
                text = getattr(chunk, "text", None)
                if text:
                    has_yielded = True
                    yield text
            if has_yielded:
                return
        except Exception as e:
            last_err = e
            time.sleep(0.5)
            continue

    # Raise genuine exception so caller treats model/API/network failure as an error state
    if last_err:
        raise last_err
    raise RuntimeError("All Gemini API models failed to stream content.")


def build_rag_payload(question: str, context: str, history: str = "") -> str:
    return f"""
{RAG_SYSTEM_PROMPT}

Conversation History:
{history}

Knowledge Base Documents:
{context}

Student Question:
{question}

Instructions:
- Answer the student's question accurately using the provided Knowledge Base documents.
- Format your response cleanly using natural Markdown (paragraphs, bullet points, code blocks where appropriate).
- Do NOT force rigid section headers like 'Overview', 'Key Points', 'Conclusion' unless natural to the topic.
- Return ONLY the student-facing answer in Markdown. Do not return JSON.
"""


def build_general_payload(question: str, history: str = "") -> str:
    return f"""
{GENERAL_SYSTEM_PROMPT}

Conversation History:
{history}

User Question:
{question}

Instructions:
- Answer the user's question using your general knowledge.
- Provide a clear, natural, and helpful answer in Markdown (paragraphs, bullet points, syntax-highlighted code blocks where appropriate).
- Do NOT mention GCET, college knowledge base, or document retrieval unless specifically asked.
- Do NOT say "The requested information is not available in the current GCET Knowledge Base".
- Return ONLY the direct answer in Markdown. Do not return JSON.
"""


def generate_rag_answer(question: str, context: str, history: str = "") -> tuple[str, int, list[str]]:
    prompt = build_rag_payload(question, context, history)
    response = _generate_content_with_fallback(prompt)
    payload = _extract_json_block(response.text or "")
    answer = payload.get("answer") or response.text
    confidence = int(payload.get("confidence", 85) or 85)
    follow_up_questions = payload.get("follow_up_questions") or []
    return answer, min(max(confidence, 0), 100), follow_up_questions[:3]


def generate_general_answer(question: str, history: str = "") -> tuple[str, int, list[str]]:
    prompt = build_general_payload(question, history)
    response = _generate_content_with_fallback(prompt)
    payload = _extract_json_block(response.text or "")
    answer = payload.get("answer") or response.text
    confidence = int(payload.get("confidence", 85) or 85)
    follow_up_questions = payload.get("follow_up_questions") or []
    return answer, min(max(confidence, 0), 100), follow_up_questions[:3]


def generate_response_metadata(
    question: str,
    answer: str,
    used_knowledge_base: bool,
) -> tuple[int, list[str]]:
    """Generate metadata after a streamed Markdown answer has completed."""
    prompt = f"""
Evaluate this completed assistant response for a student.

Student question: {question}
Assistant answer: {answer}
Knowledge-base context used: {"yes" if used_knowledge_base else "no"}

Return only a JSON object with:
- confidence: an integer from 0 to 100 reflecting support and certainty
- follow_up_questions: exactly three short, useful follow-up questions
"""
    try:
        response = _generate_content_with_fallback(prompt)
        payload = _extract_json_block(response.text or "")
        confidence = int(payload.get("confidence", 85) or 85)
        follow_up_questions = payload.get("follow_up_questions") or []
        return min(max(confidence, 0), 100), follow_up_questions[:3]
    except Exception:
        return 85, [
            "Can you clarify further details on this?",
            "What are related guidelines or resources?",
            "How does this apply in practice?"
        ]


def generate_rag_answer_stream(
    question: str,
    context: str,
    history: str = "",
) -> Generator[str, None, None]:
    prompt = build_rag_payload(question, context, history)
    yield from _stream_answer(prompt)


def generate_general_answer_stream(
    question: str,
    history: str = "",
) -> Generator[str, None, None]:
    prompt = build_general_payload(question, history)
    yield from _stream_answer(prompt)
