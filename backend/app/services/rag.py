from backend.app.services.gemini import client


def generate_rag_answer(
    question: str,
    context: str,
) -> str:
    """
    Generate an answer using retrieved GCET document context.
    """

    prompt = f"""
You are the GCET Student Assistant.

Answer the student's question using the provided GCET document context.

Rules:
1. Use the provided context as the source of truth for college-specific information.
2. Do not invent college rules, policies, dates, marks, attendance,
   placement information, or regulations.
3. Give a clear, concise, student-friendly answer.
4. If the context does not contain enough information to answer the
   question, clearly say that the available GCET documents do not
   contain enough information.

Context:
{context}

Student Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text


def generate_general_answer(
    question: str,
) -> str:
    """
    Generate an answer for general academic or student questions.
    """

    prompt = f"""
You are a helpful AI assistant for college students.

Answer the student's question clearly and accurately.

The question may be related to:

- Academic subjects
- Programming
- Placements
- Career preparation
- General knowledge
- Aptitude

Do not claim to know private or current GCET-specific information unless it is provided through the college knowledge base.

Student Question:

{question}

Answer:
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text