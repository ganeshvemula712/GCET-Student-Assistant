import re

DOCUMENT_EXPLICIT_PATTERNS = [
    r"\baccording\s+to\b",
    r"\buploaded(\s+document|\s+file)?\b",
    r"\bin\s+the\s+(uploaded\s+)?(document|pdf|file|calendar|timetable|table|sheet)\b",
    r"\bacademic\s+calendar\b",
    r"\btime\s*table\b",
    r"\bsemester\s+timetable\b",
    r"\bds_?ar25\b",
    r"\bar25\b",
    r"\bb\.?tech\b",
    r"\b(iv|iii|ii)\b",
    r"\b(iv|iii|ii|i)\s*[-_]?\s*(yr|year|sem|semester|b\.?tech|cse|ds|aiml|ece|eee|mech|civil)\b",
    r"\b(4th|3rd|2nd|1st)\s*(yr|year)?\s*(i|ii|1st|2nd|1sem|2sem)?\s*(sem|semester)?\s*(ds|aiml|cse|ece|eee|mech|civil)?\s*(a|b|c|d|e)?\s*(section|sec|tm)?\s*(time\s*table|timetable|schedule)?\b",
    r"\b(aiml|ds|cse|ece|eee|mech)\s*[-_]?\s*(a|b|c|d)\b",
    r"\bsummarize\s+the\b",
    r"\bdocument\s+(says|mentions|states|contains)\b",
]

EXPLICIT_GCET_KEYWORDS = (
    "gcet", "geethanjali", "geethanjali college", "gcet college",
    "r22", "ar22", "r20", "r18", "r16", "r25", "ar25", "ar24", "ar23", "ds_ar25", "ds ar25",
    "attendance", "condonation", "credit", "credits",
    "placement", "placements", "recruitment", "recruiter", "recruiters", "placement eligibility",
    "sgpa", "cgpa", "syllabus", "curriculum", "sem", "semester", "mid", "mids",
    "examination", "examinations", "exam", "exams", "hostel", "principal", "hod", "detained", "promotion",
    "lpa", "ctc",
    "highest package", "average package", "lowest package", "package offered", "salary package",
    "highest salary", "average salary", "salary offered",
    "graduating batch", "graduates", "placement drive", "campus drive", "recruitment drive",
    "companies visited", "visited for placements", "company offered",
    "academic regulations", "gcet regulations", "college regulations", "academic rules", "college rules", "gcet rules",
    "calendar", "calender", "caleder", "academic calendar", "events", "schedule",
    "timetable", "time table", "time-table", "date sheet", "dates", "exam dates",
    "notice", "notices", "circular", "circulars", "overview", "instructions", "instruction",
    "training", "internship", "workshop", "guidelines", "guide", "rules",
    "4th yr", "3rd yr", "2nd yr", "1st yr", "iv yr", "iii yr", "ii yr", "i yr",
    "4th year", "3rd year", "2nd year", "1st year", "iv year", "iii year", "ii year", "i year",
    "1st sem", "2nd sem", "3rd sem", "4th sem", "5th sem", "6th sem", "7th sem", "8th sem",
    "i sem", "ii sem", "iii sem", "iv sem", "v sem", "vi sem", "vii sem", "viii sem"
)

GENERAL_GREETINGS = {
    "hello", "hi", "hey", "hloo", "hollo", "greetings", "good morning", "good afternoon", "good evening",
    "hii", "hiii", "hiiii", "helloo", "hellooo", "heyy", "heyyy", "yo", "yoo", "yooo", "hyy", "hyyy"
}

GENERAL_QUESTION_PREFIXES = (
    "what is", "what are", "what does", "explain", "describe", "define",
    "how does", "how do", "how to", "write a", "write code", "code for",
    "create a", "implement", "show me", "can you write", "give me an example",
    "example of", "difference between", "compare", "why is", "why do", "how can i",
    "tell me about", "tutorial for"
)

GENERAL_CONCEPT_TERMS = (
    "ai", "ml", "aiml", "artificial intelligence", "machine learning", "deep learning",
    "neural network", "neural networks", "nlp", "natural language processing",
    "cv", "computer vision", "rag", "retrieval augmented generation", "retrieval-augmented generation",
    "llm", "large language model", "generative ai", "genai", "transformer", "embeddings",
    "vector database", "chromadb", "faiss", "prompt engineering", "machine learning models",
    "python", "java", "c++", "c", "sql", "html", "css", "javascript", "react", "node",
    "data science", "data analytics", "cloud computing", "operating system", "operating systems",
    "dbms", "database", "databases", "computer networks", "data structures", "dsa",
    "algorithms", "algorithm", "binary search", "bubble sort", "linked list",
    "stack", "queue", "tree", "graph", "sorting", "cybersecurity", "blockchain",
    "iot", "devops", "software engineering", "compiler", "compiler design",
    "api", "rest api", "fastapi", "flask", "django", "git", "github", "docker", "kubernetes", "linux",
    "programming", "program", "code", "coding",
    "array", "arrays", "string", "strings", "pointer", "pointers", "recursion", "loop", "loops",
    "function", "functions", "method", "methods", "class", "classes", "object", "objects", "oop", "constructor"
)

GENERIC_POLYSEMY_PATTERNS = [
    r"\bpackage\s+in\s+\w+",
    r"\bbatch\s+in\s+\w+",
    r"\bdrive\s+in\s+\w+",
    r"\bwhat\s+is\s+a\s+(company|salary|package|batch|drive|timetable|calendar|schedule|document|file)\b",
    r"\bwhat\s+are\s+regulations\s+in\s+general\b",
    r"\breverse\s+a\s+string\b",
    r"\bwrite\s+(a\s+)?(java|python|c\+\+|c|js|javascript)\s+program\b",
    r"\b(python|java|c\+\+|javascript)\s+lists?\b"
]


def is_explicit_gcet_query(text: str) -> bool:
    """
    Returns True if the query explicitly asks about GCET-specific college context,
    uploaded document titles, regulations, syllabus, calendars, or timetables.
    """
    t_lower = text.lower().strip()

    if "in general" in t_lower:
        return False

    # Generic definition questions ("What is a timetable?", "Write a Java program...") stay general
    if any(re.search(pat, t_lower) for pat in GENERIC_POLYSEMY_PATTERNS):
        return False

    # Check explicit document patterns (regex)
    if any(re.search(pat, t_lower) for pat in DOCUMENT_EXPLICIT_PATTERNS):
        return True

    # Direct keyword check
    if any(re.search(r'\b' + re.escape(kw) + r'\b', t_lower) for kw in EXPLICIT_GCET_KEYWORDS):
        return True

    # Common substrings & typos for calendar / timetable / academic keywords
    academic_stems = ("calen", "caled", "timetab", "time tab", "syllab", "regulatio", "attendan", "acadami", "academ", "overview", "instructi", "ds_ar25", "ar25")
    if any(stem in t_lower for stem in academic_stems):
        # Guard against general tech terms like "fastapi", "operating system instructions"
        if not any(tech in t_lower for tech in ("fastapi", "retrieval-augmented generation", "retrieval augmented generation", "python", "java")):
            return True

    return False


def is_pure_general_concept(text: str) -> bool:
    """
    Returns True if the query is a general technical, CS/AI/ML concept, general programming request, or greeting.
    """
    t_lower = text.lower().strip()

    if is_explicit_gcet_query(t_lower):
        return False

    if t_lower in GENERAL_GREETINGS or re.match(r"^(h+i+|h+e+l+o+|h+e+y+|y+o+|h+y+)\b", t_lower):
        return True

    if "in general" in t_lower:
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
        "what is python", "what is java", "what is rag", "what is nlp", "what is data science",
        "what is a neural network", "explain artificial intelligence", "explain machine learning",
        "what is retrieval-augmented generation", "what is retrieval augmented generation",
        "what is fastapi", "what is an api", "what is api", "explain python lists"
    ]
    if any(phrase in t_lower for phrase in general_phrases):
        return True

    # General programming action & manipulation patterns (e.g. "reverse an array", "how to sort a string", "implement a linked list")
    general_action_patterns = [
        r"\b(reverse|sort|search|find|count|convert|merge|filter|swap)\s+(a\s+|an\s+)?(array|string|list|number|integer|element|elements|vector|matrix|linked\s*list)\b",
        r"\b(how\s+do\s+i|how\s+to|how\s+can\s+i)\s+(reverse|sort|search|find|count|convert|merge|swap|implement)\b",
        r"\b(write|create|implement|show)\s+(a\s+)?\w*\s*(program|code|function|script|algorithm|method|class)\b",
    ]
    if any(re.search(pat, t_lower) for pat in general_action_patterns):
        return True

    return False


def should_bypass_retrieval(question: str, search_query: str) -> bool:
    """
    Authoritative single-source routing decision with explicit priority:
    1. Explicit GCET query -> NEVER bypass retrieval.
    2. Pure general concept / greeting -> BYPASS retrieval.
    3. Other/ambiguous query -> Default to safe handling based on GCET keyword rules.
    """
    q_lower = question.lower().strip()
    sq_lower = search_query.lower().strip()

    # Rule 1: Explicit GCET query HAS ABSOLUTE PRIORITY. Never bypass retrieval!
    if is_explicit_gcet_query(q_lower) or is_explicit_gcet_query(sq_lower):
        return False

    # Rule 2: Pure general concepts bypass retrieval completely
    is_general_q = is_pure_general_concept(q_lower)
    is_general_sq = is_pure_general_concept(sq_lower)

    if is_general_q:
        return True

    return is_general_sq

