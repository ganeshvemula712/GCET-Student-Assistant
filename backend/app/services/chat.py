from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation
from backend.app.models.user import User
from backend.app.schemas.chat import ChatRequest, ChatResponse, Source
from backend.app.services.memory import get_conversation_history
from backend.app.services.message import save_message
from backend.app.services.rag import (
    generate_general_answer,
    generate_rag_answer,
)
from backend.app.services.retrieval import retrieve_relevant_chunks

RELEVANCE_THRESHOLD = 1.25


def process_chat(
    request: ChatRequest,
    current_user: User,
    db: Session,
):
    sources = []

    # 1. Fetch or create conversation
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.conversation_id == request.conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if conversation is None:
        short_title = request.question.strip()
        if len(short_title) > 40:
            short_title = short_title[:37] + "..."
        conversation = Conversation(
            conversation_id=request.conversation_id,
            title=short_title or "New Conversation",
            user_id=current_user.id,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    if conversation.title == "New Conversation":
        short_title = request.question.strip()
        if len(short_title) > 40:
            short_title = short_title[:37] + "..."
        conversation.title = short_title
        db.commit()
        db.refresh(conversation)

    # 2. Get history & save user message
    conversation_history = get_conversation_history(
        conversation_id=request.conversation_id,
        db=db,
    )

    save_message(
        db=db,
        conversation_id=request.conversation_id,
        role="user",
        content=request.question,
    )

    # 3. Retrieve relevant chunks
    retrieved_chunks = retrieve_relevant_chunks(
        question=request.question,
        n_results=4,
    )

    relevant_chunks = [
        chunk
        for chunk in retrieved_chunks
        if chunk.get("distance", 2.0) <= RELEVANCE_THRESHOLD
    ]

    # 4. General AI fallback
    if not relevant_chunks:
        general_prompt = f"""
=========================
Conversation History
=========================

{conversation_history}

=========================
Current Student Question
=========================

{request.question}
"""

        answer, confidence, follow_up_questions = generate_general_answer(
            general_prompt
        )

        save_message(
            db=db,
            conversation_id=request.conversation_id,
            role="assistant",
            content=answer,
            sources=[],
            confidence=confidence,
            follow_up_questions=follow_up_questions,
        )

        return ChatResponse(
            answer=answer,
            sources=[],
            confidence=confidence,
            follow_up_questions=follow_up_questions,
        )

    # 5. RAG Answer
    context = "\n\n".join(
        chunk["text"]
        for chunk in relevant_chunks
    )

    full_context = f"""
=========================
Conversation History
=========================

{conversation_history}

=========================
GCET Knowledge Base
=========================

{context}

=========================
Current Student Question
=========================

{request.question}
"""

    answer, confidence, follow_up_questions = generate_rag_answer(
        question=request.question,
        context=full_context,
    )

    unique_sources = {
        (
            chunk["metadata"]["filename"],
            chunk["metadata"]["page"],
        )
        for chunk in relevant_chunks
        if chunk.get("metadata")
        and chunk["metadata"].get("filename")
        and chunk["metadata"].get("page") is not None
    }

    sources = [
        Source(
            filename=filename,
            page=page,
        )
        for filename, page in sorted(unique_sources)
    ]

    save_message(
        db=db,
        conversation_id=request.conversation_id,
        role="assistant",
        content=answer,
        sources=[source.model_dump() for source in sources],
        confidence=confidence,
        follow_up_questions=follow_up_questions,
    )

    return ChatResponse(
        answer=answer,
        sources=sources,
        confidence=confidence,
        follow_up_questions=follow_up_questions,
    )
