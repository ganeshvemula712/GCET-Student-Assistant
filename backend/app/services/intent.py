import re

EXPLICIT_GCET_KEYWORDS = (
    "gcet", "geethanjali", "r22", "ar22", "r20", "r18", "r16",
    "attendance", "condonation", "credit", "credits",
    "placement", "placements", "recruitment", "recruiter", "recruiters",
    "sgpa", "cgpa", "syllabus", "curriculum", "sem", "semester", "mid", "mids",
    "examination", "examinations", "hostel", "principal", "hod", "detained", "promotion",
    "lpa", "ctc",
    "highest package", "average package", "lowest package", "package offered", "salary package",
    "highest salary", "average salary", "salary offered",
    "graduating batch", "graduates", "placement drive", "campus drive", "recruitment drive",
    "companies visited", "visited for placements", "company offered",
    "academic regulations", "gcet regulations", "college regulations", "academic rules"
)

GENERAL_GREETINGS = {
    "hello", "hi", "hey", "hloo", "hollo", "greetings", "good morning", "good afternoon", "good evening"
}

GENERAL_QUESTION_PREFIXES = (
    "what is", "what are", "what does", "explain", "describe", "define",
    "how does", "how do", "difference between", "examples of", "advantages of", "disadvantages of",
    "tell me about", "tutorial for"
)

GENERAL_CONCEPT_TERMS = (
    "ai", "ml", "aiml", "artificial intelligence", "machine learning", "deep learning",
    "neural network", "neural networks", "nlp", "natural language processing",
    "cv", "computer vision", "rag", "llm", "large language model", "generative ai",
    "python", "java", "c++", "c", "sql", "html", "css", "javascript", "react", "node",
    "data science", "cloud computing", "operating system", "operating systems",
    "dbms", "database", "databases", "computer networks", "data structures",
    "algorithms", "algorithm", "binary search", "bubble sort", "linked list",
    "stack", "queue", "tree", "graph", "sorting", "cybersecurity", "blockchain",
    "iot", "devops", "software engineering", "compiler", "compiler design"
)

GENERIC_POLYSEMY_PATTERNS = [
    r"\bpackage\s+in\s+\w+",
    r"\bbatch\s+in\s+\w+",
    r"\bdrive\s+in\s+\w+",
    r"\bwhat\s+is\s+a\s+(company|salary|package|batch|drive)\b",
    r"\bwhat\s+are\s+regulations\s+in\s+general\b"
]


def is_explicit_gcet_query(text: str) -> bool:
    """
    Returns True if the query explicitly asks about GCET-specific college context
    (academics, regulations, attendance, syllabus, placements, salary packages, graduating batches).
    """
    t_lower = text.lower().strip()
    return any(re.search(r'\b' + re.escape(kw) + r'\b', t_lower) for kw in EXPLICIT_GCET_KEYWORDS)


def is_pure_general_concept(text: str) -> bool:
    """
    Returns True if the query is a general technical, CS/AI/ML concept or greeting.
    """
    t_lower = text.lower().strip()

    if t_lower in GENERAL_GREETINGS:
        return True

    if "in general" in t_lower and not is_explicit_gcet_query(t_lower):
        return True

    if any(re.search(pat, t_lower) for pat in GENERIC_POLYSEMY_PATTERNS):
        return True

    has_prefix = any(t_lower.startswith(pref) for pref in GENERAL_QUESTION_PREFIXES)
    has_tech_term = any(re.search(r'\b' + re.escape(term) + r'\b', t_lower) for term in GENERAL_CONCEPT_TERMS)

    if has_prefix and has_tech_term:
        return True

    general_phrases = [
        "what is ai", "what is ml", "what is ai and ml", "what is ai & ml", "what is ai/ml",
        "explain ai", "explain ml", "explain ai and ml", "explain ai & ml",
        "what is artificial intelligence", "what is machine learning", "what is deep learning",
        "what is python", "what is rag", "what is nlp", "what is data science",
        "what is a neural network", "explain artificial intelligence", "explain machine learning"
    ]
    return any(phrase in t_lower for phrase in general_phrases)


def should_bypass_retrieval(question: str, search_query: str) -> bool:
    """
    Authoritative single-source routing decision.
    Returns True ONLY when a question is confidently a pure general concept / greeting
    AND contains no explicit GCET/college-specific keywords.
    """
    q_lower = question.lower().strip()
    sq_lower = search_query.lower().strip()

    is_gcet = is_explicit_gcet_query(sq_lower) or is_explicit_gcet_query(q_lower)
    if is_gcet:
        return False

    is_general = is_pure_general_concept(q_lower) or is_pure_general_concept(sq_lower)
    return is_general
