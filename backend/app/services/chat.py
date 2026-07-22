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
from backend.app.services.title import generate_conversation_title

RELEVANCE_THRESHOLD = 0.75


def process_chat(
    request: ChatRequest,
    current_user: User,
    db: Session,
):
    # --------------------------------------------------
    # Find conversation that belongs to current user
    # --------------------------------------------------
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.conversation_id == request.conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    # --------------------------------------------------
    # Create conversation if it doesn't exist
    # --------------------------------------------------
    if conversation is None:

        conversation = Conversation(
            conversation_id=request.conversation_id,
            title="New Conversation",
            user_id=current_user.id,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # --------------------------------------------------
    # Generate title only once
    # --------------------------------------------------
    if conversation.title == "New Conversation":
        try:
            new_title = generate_conversation_title(
                request.question
            )

            conversation.title = new_title

            db.commit()
            db.refresh(conversation)

        except Exception as e:
            print(f"Title generation failed: {e}")

    # --------------------------------------------------
    # Load memory
    # --------------------------------------------------
    conversation_history = get_conversation_history(
        conversation_id=request.conversation_id,
        db=db,
    )

    # --------------------------------------------------
    # Save user message
    # --------------------------------------------------
    save_message(
        db=db,
        conversation_id=request.conversation_id,
        role="user",
        content=request.question,
    )

    # --------------------------------------------------
    # Retrieve relevant chunks
    # --------------------------------------------------
    retrieved_chunks = retrieve_relevant_chunks(
        question=request.question,
        n_results=3,
    )

    relevant_chunks = [
        chunk
        for chunk in retrieved_chunks
        if chunk["distance"] <= RELEVANCE_THRESHOLD
    ]
    # --------------------------------------------------
    # General AI
    # --------------------------------------------------
    if not relevant_chunks:

        general_prompt = f"""
Previous Conversation:

{conversation_history}

Current Question:

{request.question}
"""

        answer = generate_general_answer(
            general_prompt
        )

        save_message(
            db=db,
            conversation_id=request.conversation_id,
            role="assistant",
            content=answer,
        )

        return ChatResponse(
            answer=answer,
            sources=[],
        )
    # --------------------------------------------------
    # RAG
    # --------------------------------------------------
    context = "\n\n".join(
        chunk["text"]
        for chunk in relevant_chunks
    )

    full_context = f"""
Previous Conversation:

{conversation_history}

Knowledge Base:

{context}

Current Question:

{request.question}
"""

    answer = generate_rag_answer(
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
    )

    return ChatResponse(
        answer=answer,
        sources=sources,
    )