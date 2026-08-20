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
from backend.app.services.retrieval import (
    RetrievalServiceError,
    retrieve_relevant_chunks,
)
from backend.app.services.title_generator import generate_title_from_message

from backend.app.services.intent import (
    is_explicit_gcet_query,
    is_pure_general_concept,
    should_bypass_retrieval,
)

RELEVANCE_THRESHOLD = 1.45


def _generate_fallback_general_response(question: str) -> str:
    q_lower = question.lower().strip()

    if q_lower in ("hello", "hi", "hey", "hloo", "hollo", "greetings", "good morning", "good afternoon"):
        return (
            "Hello! Welcome to the **GCET AI Assistant**.\n\n"
            "I am your academic workspace assistant. How can I help you today with your studies, "
            "academic regulations, or technical questions?"
        )

    if "database" in q_lower or "dbms" in q_lower:
        return (
            "### What is a Database (DBMS)?\n\n"
            "A **Database** is an organized collection of structured data or information stored electronically in a computer system. "
            "A **Database Management System (DBMS)** is the software used to interact with the database, manage users, execute queries, and ensure data consistency.\n\n"
            "**Key Types of Databases:**\n"
            "- **Relational Databases (RDBMS)**: Uses structured tables with rows and columns (e.g., PostgreSQL, MySQL, SQLite, Oracle). Data is queried using **SQL**.\n"
            "- **NoSQL Databases**: Designed for unstructured or semi-structured data (e.g., MongoDB, Cassandra, Redis). Types include Document, Key-Value, Column-family, and Graph databases.\n"
            "- **Vector Databases**: Optimized for multi-dimensional vector embeddings used in AI & RAG systems (e.g., ChromaDB, Pinecone, pgvector).\n\n"
            "**Core Features of a DBMS (ACID Properties):**\n"
            "- **Atomicity**: Transactions commit completely or roll back entirely.\n"
            "- **Consistency**: Data adheres to constraints before and after transactions.\n"
            "- **Isolation**: Concurrent transactions do not interfere with each other.\n"
            "- **Durability**: Committed data survives system failures."
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
        f"**{question.strip()}** is a foundational concept in Computer Science and Engineering.\n\n"
        "**Overview & Application:**\n"
        f"It involves principles used across software development, system design, and algorithmic problem-solving. "
        "For specific GCET course syllabi, lab manuals, or regulations related to this topic, feel free to ask a grounded question or check the uploaded course materials."
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

        # 3. Intent Pre-Check & Vector Retrieval
        q_lower = question.lower().strip()
        sq_lower = search_query.lower().strip()
        is_explicit_gcet = (
            is_explicit_gcet_query(sq_lower)
            or is_explicit_gcet_query(q_lower)
        )
        bypass_retrieval = should_bypass_retrieval(question, search_query)

        if bypass_retrieval:
            print(f"[CHAT] Pre-retrieval intent check: bypassing vector retrieval for general question '{search_query[:50]}'")
            retrieved = []
            retrieval_failed = False
        else:
            t_retrieval_start = time.perf_counter()
            try:
                retrieved = retrieve_relevant_chunks(
                    question=search_query,
                    n_results=6,
                )
                retrieval_failed = False
            except RetrievalServiceError as ret_err:
                print(f"[CHAT] RetrievalServiceError encountered: {ret_err}")
                retrieved = []
                retrieval_failed = True
            t_retrieval_end = time.perf_counter()
            print(f"[CHAT] RAG retrieval completed: {(t_retrieval_end - t_retrieval_start)*1000:.1f} ms (Failed: {retrieval_failed}, Found {len(retrieved)} candidate chunks for query='{search_query[:60]}...')")

        if retrieval_failed:
            print(f"[CHAT] Embedding retrieval service unavailable for effective_question='{search_query}'. Returning controlled failure response...")
            service_unavailable_msg = (
                "GCET Knowledge Base retrieval is temporarily unavailable due to embedding API rate limits. "
                "Please try again in a few moments."
            )
            save_message(
                db=db,
                conversation_id=conversation_id,
                role="user",
                content=question,
            )
            yield event("token", content=service_unavailable_msg)

            message = save_message(
                db=db,
                conversation_id=conversation_id,
                role="assistant",
                content=service_unavailable_msg,
                sources=[],
                confidence=0,
                follow_up_questions=["Please try asking your question again in a minute."],
            )

            yield event(
                "done",
                mode="retrieval_unavailable",
                message_id=message.id,
                title=conversation.title,
                sources=[],
                confidence=0,
                is_rag=False,
                follow_up_questions=["Please try asking your question again in a minute."],
            )
            return

        # 4. Evaluate relevance & intent routing
        relevant = [
            chunk
            for chunk in retrieved
            if chunk.get("distance", 2.0) <= RELEVANCE_THRESHOLD
        ]

        if bypass_retrieval:
            is_rag_mode = False
        else:
            is_rag_mode = len(relevant) > 0 and (is_explicit_gcet or relevant[0].get("distance", 2.0) <= RELEVANCE_THRESHOLD)

        answer_text = ""
        sources = []

        # Save user message to database
        save_message(
            db=db,
            conversation_id=conversation_id,
            role="user",
            content=question,
        )

        effective_question = search_query

        if is_rag_mode:
            # CASE A — Grounded GCET RAG Mode
            print(f"[CHAT] Grounded GCET context found ({len(relevant)} relevant chunks). Executing RAG stream for effective_question='{effective_question}'...")
            context_text = "\n\n".join(
                f"--- Document: {c['metadata'].get('filename')} (Page {c['metadata'].get('page')}) ---\n{c['text']}"
                for c in relevant
            )

            try:
                stream_response = generate_rag_answer_stream(
                    question=effective_question,
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
        elif is_explicit_gcet:
            # CASE B — Explicit GCET Query with No Matching Document Chunks
            print(f"[CHAT] Explicit GCET query '{effective_question}' returned 0 matching chunks. Returning strict KB notice...")
            answer_text = "The requested information is not available in the current GCET Knowledge Base."
            yield event("token", content=answer_text)
            sources = []
            confidence = 0
        else:
            # CASE C — General Knowledge Mode
            print(f"[CHAT] Routing to General Gemini stream (is_explicit_gcet={is_explicit_gcet}, rel_count={len(relevant)}) for effective_question='{effective_question}'...")
            try:
                stream_response = generate_general_answer_stream(
                    question=effective_question,
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

        is_unavailable_text = answer_text.strip().startswith("The requested information is not available")

        if is_unavailable_text:
            determined_mode = "knowledge_unavailable"
            is_rag_mode = False
            sources = []
            confidence = 0
        elif is_rag_mode:
            determined_mode = "rag"
        elif is_explicit_gcet:
            determined_mode = "knowledge_unavailable"
        else:
            determined_mode = "general"

        yield event(
            "done",
            mode=determined_mode,
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
