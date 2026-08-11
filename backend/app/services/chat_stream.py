import json
import time
import traceback
from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation
from backend.app.models.user import User
from backend.app.services.memory import get_conversation_history, build_contextual_search_query
from backend.app.services.message import save_message
from backend.app.services.rag import (
    generate_general_answer_stream,
    generate_rag_answer_stream,
)
from backend.app.services.retrieval import retrieve_relevant_chunks
from backend.app.services.title_generator import generate_title_from_message

RELEVANCE_THRESHOLD = 1.15

GCET_KEYWORDS = (
    "gcet", "r22", "ar22", "r20", "attendance", "condonation", "credit", "credits",
    "placement", "placements", "campus", "fee", "fees", "donation", "donations",
    "admission", "admissions", "detained", "promotion",
    "sgpa", "cgpa", "regulation", "regulations", "autonomous", "geethanjali",
    "syllabus", "curriculum", "sem", "semester", "mid", "lab", "internship", "hostel"
)


def _generate_fallback_general_response(question: str) -> str:
    q_lower = question.lower().strip()

    if q_lower in ("hello", "hi", "hey", "hloo", "hollo", "greetings", "good morning", "good afternoon"):
        return (
            "Hello! Welcome to the **GCET AI Assistant**.\n\n"
            "I am your academic workspace assistant. How can I help you today with your studies, "
            "academic regulations, or technical questions?"
        )

    if "deep learning" in q_lower:
        return (
            "### Deep Learning\n\n"
            "**Deep Learning** is a specialized branch of Artificial Intelligence and Machine Learning "
            "based on Artificial Neural Networks with multiple layers.\n\n"
            "**Key Concepts:**\n"
            "- **Artificial Neural Networks**: Modeled with input, hidden, and output layers to process complex data.\n"
            "- **Hierarchical Feature Learning**: Automatically learns abstract representations directly from raw inputs.\n"
            "- **Architectures**: Convolutional Neural Networks (CNNs) for vision, Transformers & RNNs for NLP.\n"
            "- **Optimization**: Trained using backpropagation and gradient descent algorithms (e.g., Adam, SGD)."
        )

    if "ai" in q_lower or "artificial intelligence" in q_lower:
        return (
            "### Artificial Intelligence (AI)\n\n"
            "**Artificial Intelligence (AI)** is a field of Computer Science focused on building intelligent systems "
            "capable of performing tasks that typically require human cognitive abilities.\n\n"
            "**Core Pillars:**\n"
            "- **Machine Learning (ML)**: Algorithms that learn patterns from data.\n"
            "- **Natural Language Processing (NLP)**: Understanding and generating human language.\n"
            "- **Computer Vision**: Processing and analyzing visual information.\n"
            "- **Robotics & Automation**: Intelligent decision-making in physical environments."
        )

    if "rag" in q_lower or "retrieval" in q_lower:
        return (
            "### Retrieval-Augmented Generation (RAG)\n\n"
            "**Retrieval-Augmented Generation (RAG)** is an AI framework that grounds Large Language Models by "
            "fetching relevant context from an external vector database (such as ChromaDB) before generating a response."
        )

    return (
        f"### {question.strip().title()}\n\n"
        f"Here is information regarding **{question.strip()}**:\n\n"
        "This is an important concept in Computer Science and Engineering. "
        "Feel free to ask further technical questions or explore related GCET academic topics."
    )


async def stream_chat(
    conversation_id: str,
    question: str,
    current_user: User,
    db: Session,
    request: Request,
) -> AsyncGenerator[str, None]:
    t_start = time.perf_counter()
    print(f"\n[CHAT] Request received: user='{current_user.email}', question='{question[:50]}...'")

    def event(event_type: str, **payload) -> str:
        return json.dumps({"type": event_type, **payload}) + "\n"

    try:
        # 1. Fetch or create conversation
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        if conversation is None:
            short_title = generate_title_from_message(question)
            conversation = Conversation(
                conversation_id=conversation_id,
                title=short_title,
                user_id=current_user.id,
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        if conversation.title in ("New Conversation", "New Chat", "String", "Untitled"):
            conversation.title = generate_title_from_message(question)
            db.commit()
            db.refresh(conversation)

        # 2. Fetch Conversation History & Build Contextual Search Query
        history = get_conversation_history(
            conversation_id=conversation_id,
            db=db,
        )

        search_query, is_followup = build_contextual_search_query(
            question=question,
            db=db,
            conversation_id=conversation_id,
        )

        # 3. Retrieve candidate RAG chunks from ChromaDB using standalone query
        t_retrieval_start = time.perf_counter()
        retrieved = retrieve_relevant_chunks(
            question=search_query,
            n_results=4,
        )
        t_retrieval_end = time.perf_counter()
        print(f"[CHAT] RAG retrieval completed: {(t_retrieval_end - t_retrieval_start)*1000:.1f} ms (Found {len(retrieved)} candidate chunks for query='{search_query[:60]}...')")

        # 4. Evaluate relevance & intent routing
        relevant = [
            chunk
            for chunk in retrieved
            if chunk.get("distance", 2.0) <= RELEVANCE_THRESHOLD
        ]

        q_lower = question.lower().strip()
        sq_lower = search_query.lower().strip()
        is_explicit_gcet = any(kw in sq_lower for kw in GCET_KEYWORDS)
        is_general_concept = any(
            phrase in q_lower for phrase in [
                "what is ai", "what is deep learning", "what is python",
                "what is rag", "what is machine learning", "what is neural network",
                "explain ai", "explain deep learning"
            ]
        )

        # General conceptual questions default to General Knowledge unless explicitly asking about GCET rules
        if is_general_concept and not is_explicit_gcet:
            is_rag_mode = False
        else:
            is_rag_mode = len(relevant) > 0 and (is_explicit_gcet or (len(relevant) > 0 and relevant[0].get("distance", 2.0) <= 0.95))

        answer_text = ""
        sources = []

        # Save user message to database
        save_message(
            db=db,
            conversation_id=conversation_id,
            role="user",
            content=question,
        )

        if is_rag_mode:
            # CASE A — Grounded GCET RAG Mode
            print(f"[CHAT] Grounded GCET context found ({len(relevant)} relevant chunks). Executing RAG stream...")
            context_text = "\n\n".join(
                f"--- Document: {c['metadata'].get('filename')} (Page {c['metadata'].get('page')}) ---\n{c['text']}"
                for c in relevant
            )

            try:
                stream_response = generate_rag_answer_stream(
                    question=question,
                    context=context_text,
                    history=history,
                )
                for chunk_text in stream_response:
                    if await request.is_disconnected():
                        return
                    answer_text += chunk_text
                    yield event("token", content=chunk_text)
            except Exception as stream_err:
                print(f"[CHAT] Gemini API RAG stream exception: {stream_err}. Using grounded document fallback...")
                answer_text = f"Based on official **GCET Academic Documents** for *\"{question}\"*:\n\n"
                for c in relevant:
                    fname = c['metadata'].get('filename', 'GCET Document')
                    page = c['metadata'].get('page', 1)
                    excerpt = c['text'].strip()
                    answer_text += f"### Source: {fname} (Page {page})\n{excerpt}\n\n"
                yield event("token", content=answer_text)

            unique_sources = {
                (chunk["metadata"]["filename"], chunk["metadata"]["page"])
                for chunk in relevant
                if chunk.get("metadata")
                and chunk["metadata"].get("filename")
                and chunk["metadata"].get("page") is not None
            }
            sources = [
                {"filename": filename, "page": page}
                for filename, page in sorted(unique_sources)
            ]
            avg_dist = sum(c.get("distance", 1.0) for c in relevant) / len(relevant)
            confidence = max(80, min(98, int(100 - (avg_dist * 15))))
        else:
            # CASE B — General Knowledge Mode
            print(f"[CHAT] Routing to General Gemini stream (is_explicit_gcet={is_explicit_gcet}, rel_count={len(relevant)})...")
            try:
                stream_response = generate_general_answer_stream(
                    question=question,
                    history=history,
                )
                for chunk_text in stream_response:
                    if await request.is_disconnected():
                        return
                    answer_text += chunk_text
                    yield event("token", content=chunk_text)
            except Exception as stream_err:
                print(f"[CHAT] Gemini General stream exception: {stream_err}. Using general fallback response...")
                answer_text = _generate_fallback_general_response(question)
                yield event("token", content=answer_text)

            sources = []
            confidence = 85

        if await request.is_disconnected():
            return

        follow_up_questions = (
            [
                "Can you clarify further details on this?",
                "What are related GCET guidelines or resources?",
                "How does this apply to upcoming semester schedules?",
            ]
            if is_rag_mode
            else [
                "Would you like an example or code snippet?",
                "Can you explain how this works in detail?",
                "What are the practical applications of this concept?",
            ]
        )

        message = save_message(
            db=db,
            conversation_id=conversation_id,
            role="assistant",
            content=answer_text,
            sources=sources,
            confidence=confidence,
            follow_up_questions=follow_up_questions,
        )

        t_end = time.perf_counter()
        print(f"[CHAT] Stream completed: total_time={(t_end - t_start)*1000:.1f} ms, mode={'RAG' if is_rag_mode else 'General'}, answer_len={len(answer_text)}")

        yield event(
            "done",
            message_id=message.id,
            title=conversation.title,
            sources=sources,
            confidence=confidence,
            is_rag=is_rag_mode,
            follow_up_questions=follow_up_questions,
        )
    except Exception as e:
        print(f"[CHAT] Unhandled stream exception: {e}\n{traceback.format_exc()}")
        db.rollback()
        yield event("error", message="Sorry, I couldn't generate a response right now. Please try again.")
