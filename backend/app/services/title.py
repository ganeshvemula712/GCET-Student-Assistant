from backend.app.services.gemini import client


def generate_conversation_title(
    question: str,
) -> str:
    """
    Generate a short conversation title.
    """

    prompt = f"""
Generate a very short conversation title.

Rules:
- Maximum 5 words.
- No quotation marks.
- No punctuation at the end.
- Title Case.
- Only return the title.

Question:

{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text.strip()