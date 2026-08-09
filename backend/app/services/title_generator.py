import re

STOP_WORDS = {
    "what", "is", "are", "the", "for", "which", "explain", "how", "does", "do",
    "a", "an", "in", "at", "of", "to", "on", "with", "and", "or", "tell", "me",
    "about", "can", "you", "give", "list", "show", "details", "info", "information",
    "please", "could", "would", "should", "requirements", "rules"
}

def generate_title_from_message(message: str) -> str:
    if not message:
        return "New Chat"

    cleaned = re.sub(r"[^\w\s-]", "", message.strip())
    words = [w for w in cleaned.split() if w]

    if not words:
        return "New Chat"

    # Filter out lead question stop-words to extract core topic keywords
    filtered_words = [w for w in words if w.lower() not in STOP_WORDS]

    # If filtering leaves at least 2 words, use filtered words, else use original words
    if len(filtered_words) >= 2:
        title_words = filtered_words[:5]
    else:
        title_words = words[:5]

    title = " ".join(title_words).strip().title()

    # Ensure title is concise (max 40 chars)
    # Ensure title is concise (max 40 chars)
    if len(title) > 40:
        title = title[:37].strip() + "..."

    # Prefix GCET if question is about GCET and GCET isn't in title
    if "gcet" in message.lower() and "gcet" not in title.lower():
        title = f"GCET {title}"

    return title if title else "New Chat"
