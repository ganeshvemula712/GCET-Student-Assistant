import re
from sqlalchemy.orm import Session

from backend.app.models.message import Message


def get_conversation_history(
    conversation_id: str,
    db: Session,
    limit: int = 10,
) -> str:
    """
    Returns the latest conversation history formatted
    for the LLM prompt.
    """

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    history = []

    for message in messages[-limit:]:
        role = "User" if message.role == "user" else "Assistant"

        history.append(
            f"{role}: {message.content}"
        )

    return "\n".join(history)


GCET_ACADEMIC_TOPICS = {
    "gcet", "geethanjali", "admission", "admissions", "donation", "donations", "fee", "fees",
    "management", "quota", "seat", "seats", "cutoff", "cutoffs",
    "eligibility", "criteria", "regulation", "regulations", "r22", "ar22", "r20",
    "attendance", "condonation", "credit", "credits", "detained", "promotion",
    "sgpa", "cgpa", "exam", "exams", "timetable", "mid", "lab", "hostel",
    "syllabus", "curriculum", "placement", "placements"
}

BRANCH_MODIFIERS = {"cse", "ece", "eee", "mech", "civil", "ds", "aiml", "it", "csd", "csm"}

ANAPHORA_PRONOUNS = {"its", "it", "this", "that", "these", "those", "same", "above", "former", "latter", "which"}

FOLLOWUP_PREFIXES = (
    "what about", "how about", "what are its", "what is its", "tell me about",
    "and for", "for cse", "for ece", "for eee", "which one", "how is it", "how does it"
)

MATH_PATTERNS = [
    r"^\s*how\s+much\s+is\s+\d+", r"^\s*\d+\s*[\+\-\*\/]\s*\d+"
]

GENERAL_CONCEPT_PATTERNS = [
    r"\b(binary search|bubble sort|linked list)\b",
    r"\b(what is machine learning|what is ai|what is deep learning|what is python)\b"
]


def build_contextual_search_query(
    question: str,
    db: Session,
    conversation_id: str,
) -> tuple[str, bool]:
    """
    Constructs a concise, topic-preserving search query for vector retrieval
    and conversation memory across both GCET and General Knowledge contexts.

    Returns tuple: (search_query, is_followup)
    Consumes 0 Gemini API calls/quota (100% deterministic, 0ms).
    """
    q_clean = question.strip()
    q_lower = q_clean.lower()
    words = set(re.findall(r"\b\w+\b", q_lower))

    # 1. Check for pure Math / Calculator expressions
    is_math = any(re.search(pat, q_lower) for pat in MATH_PATTERNS)
    if is_math:
        return q_clean, False

    # 2. Check for explicit standalone general CS questions (e.g. "What is machine learning?")
    is_standalone_general_concept = any(re.search(pat, q_lower) for pat in GENERAL_CONCEPT_PATTERNS)
    has_explicit_gcet_brand = any(brand in q_lower for brand in ("gcet", "geethanjali", "ar22", "r22", "r20"))

    if is_standalone_general_concept and not has_explicit_gcet_brand:
        return q_clean, False

    # 3. Check for explicit standalone GCET topic nouns in current question (e.g., "What is the attendance requirement?")
    current_gcet_topics = words.intersection(GCET_ACADEMIC_TOPICS)
    has_anaphora = any(p in words for p in ANAPHORA_PRONOUNS)
    has_followup_prefix = any(q_lower.startswith(p) for p in FOLLOWUP_PREFIXES)

    if current_gcet_topics and not has_anaphora and not has_followup_prefix:
        return q_clean, False

    # 4. Determine if current question is a follow-up intent
    is_short = len(words) <= 7
    is_followup_intent = is_short or has_anaphora or has_followup_prefix or bool(words.intersection(BRANCH_MODIFIERS))

    if not is_followup_intent:
        return q_clean, False

    # 5. Fetch recent user messages from PostgreSQL (last 5 turns)
    past_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    if not past_messages:
        return q_clean, False

    user_past = [m.content for m in past_messages if m.role == "user" and m.content.strip() != q_clean]

    if not user_past:
        return q_clean, False

    history_window = user_past[-5:]
    last_user_q = history_window[-1]

    # 6. Extract root topic and active branch for GCET follow-ups vs General follow-ups
    combined_history = " ".join(history_window).lower()
    history_words = set(re.findall(r"\b\w+\b", combined_history))
    history_gcet_topics = history_words.intersection(GCET_ACADEMIC_TOPICS)

    if history_gcet_topics or has_explicit_gcet_brand:
        # --- GCET FOLLOW-UP CONTEXT ---
        root_question = history_window[0]
        for uq in reversed(history_window):
            uq_words = set(re.findall(r"\b\w+\b", uq.lower()))
            if uq_words.intersection(GCET_ACADEMIC_TOPICS):
                root_question = uq
                break

        current_branches = words.intersection(BRANCH_MODIFIERS)
        active_branch = ""
        if current_branches:
            active_branch = list(current_branches)[0].upper()
        else:
            for uq in reversed(history_window):
                uq_branches = set(re.findall(r"\b\w+\b", uq.lower())).intersection(BRANCH_MODIFIERS)
                if uq_branches:
                    active_branch = list(uq_branches)[0].upper()
                    break

        if active_branch and active_branch.lower() not in root_question.lower():
            concise_query = f"{root_question} {active_branch} {q_clean}"
        else:
            concise_query = f"{root_question} {q_clean}"

        return concise_query, True
    else:
        # --- GENERAL KNOWLEDGE FOLLOW-UP CONTEXT ---
        concise_query = f"{last_user_q} {q_clean}"
        return concise_query, True