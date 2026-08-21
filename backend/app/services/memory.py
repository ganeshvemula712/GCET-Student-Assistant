import re
from sqlalchemy.orm import Session

from backend.app.services.intent import is_explicit_gcet_query, is_pure_general_concept
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
    "eligibility", "criteria", "regulation", "regulations", "r22", "ar22", "r20", "ar25", "r25",
    "attendance", "condonation", "credit", "credits", "detained", "promotion",
    "sgpa", "cgpa", "exam", "exams", "timetable", "schedule", "calendar", "calender", "caleder",
    "overview", "instructions", "training", "mid", "lab", "hostel",
    "syllabus", "curriculum", "placement", "placements"
}

UNAMBIGUOUS_BRANCHES = {"cse", "ece", "eee", "mech", "civil", "ds", "aiml", "csd", "csm"}
BRANCH_MODIFIERS = UNAMBIGUOUS_BRANCHES | {"it"}

ANAPHORA_PRONOUNS = {"its", "it", "this", "that", "these", "those", "same", "above", "former", "latter", "which"}

FOLLOWUP_PREFIXES = (
    "what about", "how about", "what are its", "what is its", "tell me about",
    "and for", "for cse", "for ece", "for eee", "which one", "how is it", "how does it"
)

FOLLOWUP_EXPLICIT_PATTERNS = [
    r"^\s*what\s+about\s+(for\s+)?",
    r"^\s*how\s+about\s+(for\s+)?",
    r"^\s*and\s+for\s+",
    r"^\s*for\s+(cse|ece|eee|mech|civil|ds|aiml|it)\s*\??$",
]

MATH_PATTERNS = [
    r"^\s*how\s+much\s+is\s+\d+", r"^\s*\d+\s*[\+\-\*\/]\s*\d+"
]

GENERAL_CONCEPT_PATTERNS = [
    r"\b(binary search|bubble sort|linked list)\b",
    r"\b(what is machine learning|what is ai|what is deep learning|what is python)\b"
]


def extract_branch_modifier(question: str) -> str | None:
    """
    Extracts explicit academic branch modifier from question if present.
    Distinguishes the English pronoun 'it' from Information Technology 'IT'.
    """
    q_clean = question.strip()
    q_lower = q_clean.lower()
    words = set(re.findall(r"\b\w+\b", q_lower))

    # 1. Check unambiguous branch acronyms (CSE, ECE, EEE, MECH, CIVIL, DS, AIML, CSD, CSM)
    found_unambiguous = words.intersection(UNAMBIGUOUS_BRANCHES)
    if found_unambiguous:
        return list(sorted(found_unambiguous))[0].upper()

    # 2. Check for Information Technology (IT) branch:
    # Requires uppercase 'IT', explicit branch/dept keywords, or explicit branch phrasing ('for IT', 'and for IT')
    if "it" in words:
        is_uppercase_it = bool(re.search(r"\bIT\b", q_clean))
        has_branch_keyword = bool(re.search(r"\b(it\s+(branch|dept|department|course|stream)|(branch|dept|department|stream)\s+of\s+it)\b", q_lower))
        is_explicit_branch_phrase = bool(re.search(r"^\s*(what\s+about|how\s+about|and\s+for|for)\s+(the\s+)?IT\b", q_clean, re.IGNORECASE))
        is_generic_pronoun_phrase = bool(re.search(r"^\s*(what\s+about|how\s+about|how\s+much\s+is|is\s+it|does\s+it|can\s+it)\s+it\b", q_lower))

        if (is_uppercase_it or has_branch_keyword or is_explicit_branch_phrase) and not (is_generic_pronoun_phrase and not is_uppercase_it and not has_branch_keyword):
            return "IT"

    return None


def build_contextual_search_query(
    question: str,
    db: Session,
    conversation_id: str,
) -> tuple[str, bool]:
    """
    Constructs an effective, contextually framed question for vector retrieval
    and LLM prompt generation when the user asks a follow-up question.

    Returns tuple: (effective_question, is_followup)
    Consumes 0 Gemini API calls/quota (100% deterministic, 0ms).
    """
    q_clean = question.strip()
    q_lower = q_clean.lower()
    words = set(re.findall(r"\b\w+\b", q_lower))

    # 1. Math / Calculation expressions are never follow-ups
    if any(re.search(pat, q_lower) for pat in MATH_PATTERNS):
        return q_clean, False

    # 2. Standalone general CS concepts / programming queries without anaphora are not follow-ups
    has_anaphora = any(p in words for p in ANAPHORA_PRONOUNS)
    has_followup_pattern = any(re.search(pat, q_lower) for pat in FOLLOWUP_EXPLICIT_PATTERNS)
    has_followup_prefix = any(q_lower.startswith(p) for p in FOLLOWUP_PREFIXES)

    is_standalone_general = is_pure_general_concept(q_lower)
    has_explicit_gcet_brand = any(brand in q_lower for brand in ("gcet", "geethanjali", "ar22", "r22", "r20"))

    if is_standalone_general and not has_explicit_gcet_brand and not has_anaphora and not has_followup_pattern:
        return q_clean, False

    # 3. Check for standalone GCET topic nouns / explicit document queries
    if is_explicit_gcet_query(q_lower) and not (has_anaphora or has_followup_pattern):
        return q_clean, False

    current_gcet_topics = words.intersection(GCET_ACADEMIC_TOPICS)
    if current_gcet_topics and not has_anaphora and not has_followup_pattern and not (has_followup_prefix and len(words) <= 5):
        return q_clean, False

    # 4. Determine if current question is a follow-up
    detected_branch = extract_branch_modifier(q_clean)
    is_short_branch = len(words) <= 5 and bool(detected_branch)
    is_followup = is_short_branch or has_anaphora or has_followup_pattern or (has_followup_prefix and len(words) <= 7)

    if not is_followup:
        return q_clean, False

    # 5. Fetch previous user messages from PostgreSQL for current conversation_id ONLY
    past_user_msgs = (
        db.query(Message.content)
        .filter(
            Message.conversation_id == conversation_id,
            Message.role == "user"
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    user_past = [m[0] for m in past_user_msgs if m[0].strip() != q_clean]

    if not user_past:
        return q_clean, False

    # Immediate previous turn (Q1) takes 1st priority for follow-up resolution
    last_user_q = user_past[-1].strip()

    if any(re.search(pat, last_user_q.lower()) for pat in MATH_PATTERNS):
        return q_clean, False

    # Construct effective question:
    # Handle branch follow-up: e.g. Q1="What is the minimum attendance required at GCET?" + Q2="What about CSE?"
    # -> effective_question = "What is the minimum attendance required for CSE at GCET?"
    if detected_branch:
        branch_str = detected_branch
        if branch_str.lower() not in last_user_q.lower():
            if "at gcet" in last_user_q.lower():
                effective_q = re.sub(r"(?i)\bat gcet\b", f"for {branch_str} at GCET", last_user_q)
            else:
                effective_q = f"{last_user_q.rstrip('?')} for {branch_str}?"
            return effective_q, True

    # Handle pronoun follow-up: e.g. Q1="What is deep learning?" + Q2="What are its applications?"
    # -> effective_question = "What are the applications of deep learning?"
    if "its applications" in q_lower or "their applications" in q_lower:
        topic_match = re.sub(r"(?i)^\s*what\s+is\s+", "", last_user_q).rstrip("?")
        return f"What are the applications of {topic_match}?", True

    if "how much is it" in q_lower or "how much is that" in q_lower or "is it mandatory" in q_lower:
        return last_user_q, True

    effective_q = f"{last_user_q} ({q_clean})"
    return effective_q, True