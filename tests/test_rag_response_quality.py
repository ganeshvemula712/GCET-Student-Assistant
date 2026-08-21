import pytest
from backend.app.core.prompts import GENERAL_SYSTEM_PROMPT, RAG_SYSTEM_PROMPT
from backend.app.services.rag import build_general_payload, build_rag_payload


def test_rag_prompt_grounding_requirement():
    """1. Verify RAG system prompt requires grounding in GCET Knowledge Base context."""
    assert "ONLY the verified GCET Knowledge Base context provided below" in RAG_SYSTEM_PROMPT


def test_rag_prompt_direct_answer_requirement():
    """2. Verify RAG prompt requires answering student question DIRECTLY FIRST."""
    assert "Answer the student's exact question DIRECTLY FIRST" in RAG_SYSTEM_PROMPT
    assert "concise 1-3 sentence direct answer" in RAG_SYSTEM_PROMPT


def test_rag_prompt_unrelated_context_protection():
    """3. Verify RAG prompt explicitly forbids unrelated rules (dress code, mobile phones, etc.)."""
    assert "DO NOT include unrelated rules" in RAG_SYSTEM_PROMPT
    assert "dress code" in RAG_SYSTEM_PROMPT
    assert "mobile phone rules" in RAG_SYSTEM_PROMPT
    assert "identity card rules" in RAG_SYSTEM_PROMPT
    assert "seminar rules" in RAG_SYSTEM_PROMPT


def test_rag_prompt_no_document_dumping():
    """4. Verify RAG prompt forbids reproducing large document sections or full pages."""
    assert "Do NOT reproduce large sections or full pages" in RAG_SYSTEM_PROMPT


def test_rag_prompt_knowledge_base_unavailable_behavior():
    """5. Verify expected unavailable response string is explicitly defined."""
    assert "The requested information is not available in the current GCET Knowledge Base." in RAG_SYSTEM_PROMPT


def test_rag_prompt_no_hallucinated_regulations():
    """6. Verify prompt forbids inventing/fabricating college regulations, fees, or figures."""
    assert "Do not invent or fabricate college regulations" in RAG_SYSTEM_PROMPT


def test_build_rag_payload_structure():
    """7. Verify build_rag_payload clearly separates history, context, question, and instructions."""
    payload = build_rag_payload(
        question="What is the minimum attendance?",
        context="[Doc 1]: Attendance is 75%.",
        history="User: Hi\nAssistant: Hello"
    )

    assert "Conversation History:" in payload
    assert "Knowledge Base Documents:" in payload
    assert "Student Question:" in payload
    assert "Instructions:" in payload


def test_build_rag_payload_question_preservation():
    """8. Verify exact student question is present in the payload."""
    question = "What is the GCET placement eligibility CGPA?"
    payload = build_rag_payload(question=question, context="CGPA 6.0 required")
    assert question in payload


def test_build_rag_payload_context_preservation():
    """9. Verify retrieved context document content is present in the payload."""
    context = "[Document: AR22-CSE.pdf (Page 21)]\nMinimum attendance is 75%."
    payload = build_rag_payload(question="Attendance rule?", context=context)
    assert context in payload


def test_build_rag_payload_history_handling():
    """10. Verify conversation history is placed in history section without replacing context or question."""
    history = "User: What are midterm rules?\nAssistant: Midterm rules are..."
    question = "What about attendance?"
    context = "Attendance must be 75%."

    payload = build_rag_payload(question=question, context=context, history=history)

    assert history in payload
    assert question in payload
    assert context in payload

    # Check relative positioning order
    hist_idx = payload.index("Conversation History:")
    kb_idx = payload.index("Knowledge Base Documents:")
    q_idx = payload.index("Student Question:")

    assert hist_idx < kb_idx < q_idx


def test_build_general_payload_structure_and_isolation():
    """11. Verify general payload contains GENERAL_SYSTEM_PROMPT and prohibits GCET claims."""
    payload = build_general_payload(question="What is FastAPI?", history="")

    assert GENERAL_SYSTEM_PROMPT in payload
    assert "What is FastAPI?" in payload
    assert "Do NOT mention GCET, college knowledge base, or document retrieval" in payload
    assert 'Do NOT say "The requested information is not available in the current GCET Knowledge Base"' in payload
