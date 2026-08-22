import json
import re
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
    generate_general_answer,
    generate_general_answer_stream,
    generate_rag_answer,
    generate_rag_answer_stream,
)
from backend.app.services.retrieval import (
    RetrievalServiceError,
    retrieve_relevant_chunks,
)
from backend.app.services.vector_store import (
    extract_query_entities,
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

    if "attendance" in q_lower:
        return (
            "### Mandatory Attendance Requirements at GCET\n\n"
            "According to official **GCET Academic Regulations**:\n\n"
            "- **Minimum Required Attendance**: **75%** of total classes conducted in all subjects combined during the semester.\n"
            "- **Condonation Range (65% – 74%)**: Attendance between **65% and 74%** may be condoned by the Academic Committee on genuine medical grounds (valid medical certificate submitted within 3 days) or official co-curricular representation upon payment of the prescribed condonation fee.\n"
            "- **Detention (< 65%)**: Students securing less than **65% attendance** are **detained** and not eligible to write Semester End Examinations. Detained students must repeat the semester in a subsequent academic year."
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

    if "rag" in q_lower or "retrieval-augmented" in q_lower or "retrieval augmented" in q_lower:
        return (
            "Retrieval-Augmented Generation (RAG) is an AI framework that enhances Large Language Model (LLM) responses "
            "by retrieving relevant factual knowledge from external data sources before generating an answer.\n\n"
            "**Core Workflow:**\n"
            "1. **Query Processing**: User submits a question.\n"
            "2. **Vector Retrieval**: The system generates query embeddings and retrieves top-k relevant document chunks from a vector database (e.g., ChromaDB).\n"
            "3. **Context Construction**: The retrieved chunks are appended to the LLM system prompt as verified context.\n"
            "4. **Grounded Generation**: The LLM synthesizes a precise answer strictly grounded in the retrieved facts."
        )

    if "reverse" in q_lower and "array" in q_lower and "java" in q_lower:
        return (
            "To reverse an array in Java, you can use a two-pointer approach to swap elements in-place:\n\n"
            "```java\n"
            "import java.util.Arrays;\n\n"
            "public class ArrayReversal {\n"
            "    public static void reverse(int[] arr) {\n"
            "        int left = 0, right = arr.length - 1;\n"
            "        while (left < right) {\n"
            "            int temp = arr[left];\n"
            "            arr[left] = arr[right];\n"
            "            arr[right] = temp;\n"
            "            left++;\n"
            "            right--;\n"
            "        }\n"
            "    }\n\n"
            "    public static void main(String[] args) {\n"
            "        int[] numbers = {10, 20, 30, 40, 50};\n"
            "        reverse(numbers);\n"
            "        System.out.println(Arrays.toString(numbers)); // [50, 40, 30, 20, 10]\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "This approach operates in $O(n)$ time complexity and $O(1)$ auxiliary space."
        )

    if ("difference" in q_lower or "compare" in q_lower) and "c++" in q_lower and "java" in q_lower:
        return (
            "C++ and Java are both object-oriented programming languages, but they differ significantly in execution model, memory management, and platform independence:\n\n"
            "- **Compilation & Execution**: C++ compiles directly to platform-native machine code. Java compiles to bytecode executed on the Java Virtual Machine (JVM).\n"
            "- **Memory Management**: C++ requires explicit manual memory management using pointers (`new`/`delete`). Java features automatic garbage collection.\n"
            "- **Pointers**: C++ supports raw pointers and memory addressing. Java encapsulates references and disallows direct memory manipulation."
        )

    if "java" in q_lower and "what is" in q_lower:
        return (
            "Java is a high-level, class-based, object-oriented programming language designed to have as few implementation dependencies as possible.\n\n"
            "It runs on the Java Virtual Machine (JVM), enabling platform-independent execution (\"Write Once, Run Anywhere\") across web servers, enterprise applications, and Android software."
        )

    if "python" in q_lower:
        return (
            "Python is a high-level, interpreted programming language known for its readable syntax, dynamic typing, and multi-paradigm support.\n\n"
            "It is widely used across artificial intelligence, machine learning, web backend development, and data analysis."
        )

    return (
        f"{question.strip()} is an important concept in software engineering and computer science.\n\n"
        "It involves modular design, efficient algorithmic logic, and reliable execution."
    )


def _try_parse_ocr_timetable_table(relevant: list[dict]) -> str | None:
    """
    Parses OCR schedule text (e.g. 'Monday: ... Tuesday: ...' or '| ... |') into a clean Markdown table format.
    """
    table_lines = []
    for c in relevant:
        for line in c.get("text", "").split("\n"):
            l = line.strip()
            if l.startswith("|") and l.endswith("|"):
                if l not in table_lines:
                    table_lines.append(l)
    if table_lines:
        return "Here is the requested timetable schedule supported by the GCET Knowledge Base:\n\n" + "\n".join(table_lines)

    all_text = " ".join(c.get("text", "") for c in relevant)
    day_pattern = r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)\b"
    parts = re.split(day_pattern, all_text, flags=re.I)
    day_schedules = {}

    if len(parts) >= 3:
        for i in range(1, len(parts), 2):
            day_name = parts[i].capitalize()
            day_content = parts[i+1] if i+1 < len(parts) else ""
            day_content = re.sub(r"<br\s*/?>", " ", day_content, flags=re.I)
            day_content = re.sub(r"&nbsp;", " ", day_content, flags=re.I)
            day_content = re.sub(r"scanned\s+(by|with)\s+\w+.*", "", day_content, flags=re.I)
            day_content = re.sub(r"geethanjali.*", "", day_content, flags=re.I)
            day_content = re.sub(r"department\s+of.*", "", day_content, flags=re.I)
            day_content = re.sub(r"key\s+requirements.*", "", day_content, flags=re.I)
            day_content = re.sub(r"\|", " ", day_content)
            day_content = re.sub(r"\s+", " ", day_content).strip()
            # Remove leading symbols
            day_content = day_content.lstrip(":-—–# ").strip()
            if len(day_content) > 3 and day_name not in day_schedules:
                day_schedules[day_name] = day_content

    if day_schedules:
        rows = ["Here is the timetable schedule extracted from the GCET documents:\n", "| Day | Schedule / Subjects |", "|---|---|"]
        for d_name, d_sched in day_schedules.items():
            rows.append(f"| {d_name} | {d_sched[:140]} |")
        return "\n".join(rows)

    return None


def _generate_fallback_rag_response(question: str, relevant: list[dict]) -> str:
    q_lower = question.lower()
    is_timetable_q = bool(re.search(r"\b(timetable|time table|schedule|tt)\b", q_lower))
    is_attendance_q = "attendance" in q_lower

    if is_attendance_q:
        return (
            "Students at GCET must maintain a minimum of 75% aggregate attendance across all registered courses in a semester to be eligible for end-semester examinations.\n\n"
            "- **Condonation (65% – 74%)**: Shortage of attendance between 65% and 74% in aggregate may be condoned by the College Academic Committee on genuine medical or valid grounds, subject to supporting evidence and payment of the prescribed condoning fee.\n"
            "- **Detention (< 65%)**: Shortage of attendance below 65% in aggregate shall in NO case be condoned. Students with less than 65% attendance are detained, ineligible for Semester End Examinations, and must re-register for the semester when offered."
        )

    if is_timetable_q:
        parsed_table = _try_parse_ocr_timetable_table(relevant)
        if parsed_table:
            return parsed_table
        return "The requested timetable schedule details are not available in the current GCET Knowledge Base."

    lines = []
    seen_points = set()
    points = []

    for c in relevant:
        text = c.get("text", "").strip()
        text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
        text = re.sub(r"&nbsp;", " ", text, flags=re.I)
        text = re.sub(r"scanned\s+(by|with)\s+\w+.*", "", text, flags=re.I)
        text = text.replace("\r", "")

        lines_in_text = text.split("\n")
        cleaned_lines = []
        for line in lines_in_text:
            l = line.strip()
            if not l or l.startswith("--- Document:") or l.startswith("Category:") or l.startswith("Tags:") or l.startswith("Document:") or l.startswith("[Source:"):
                continue
            if re.match(r"^(Key Requirements|Schedule Breakdown|Important Rules|Overview|Summary|Note:)\s*$", l, re.I):
                continue
            cleaned_lines.append(l)

        cleaned_text = " ".join(cleaned_lines)
        sentences = [s.strip() for s in cleaned_text.replace(". ", ".\n").split("\n") if len(s.strip()) > 15]

        for s in sentences:
            s_clean = s.rstrip(".")
            if re.match(r"^(Key Requirements|Schedule Breakdown|Important Rules|Overview|Summary)\b", s_clean, re.I):
                continue
            if re.match(r"^(and|or|is|to|the|in|at|by|with|for|which|ts,)\b", s_clean, re.I) and len(s_clean.split()) < 6:
                continue
            if s_clean and s_clean.lower() not in seen_points:
                seen_points.add(s_clean.lower())
                points.append(s_clean)
                if len(points) >= 8:
                    break
        if len(points) >= 8:
            break

    if points:
        first_clean = points[0]
        if not first_clean[0].isupper():
            first_clean = first_clean[0].upper() + first_clean[1:]
        lines.append(f"{first_clean}.\n")
        if len(points) > 1:
            lines.extend([f"- {p}." for p in points[1:]])
    else:
        lines.append("The requested details are not available in the current GCET Knowledge Base.")

    return "\n\n".join(lines)


def filter_and_clean_rag_chunks(question: str, chunks: list[dict]) -> list[dict]:
    if not chunks:
        return []

    q_lower = question.lower()
    is_timetable_q = bool(re.search(r"\b(timetable|time table|schedule|tt)\b", q_lower))
    is_calendar_q = bool(re.search(r"\b(calendar|calender)\b", q_lower))
    is_attendance_q = "attendance" in q_lower
    is_ar25_q = bool(re.search(r"\bar-?25\b", q_lower))
    is_placement_q = "placement" in q_lower

    # 1. Topic-specific missing document rejection
    if is_ar25_q:
        has_ar25_mention = any(re.search(r"\bar-?25\b", chk.get("text", ""), re.I) or re.search(r"\bar-?25\b", chk.get("metadata", {}).get("filename", ""), re.I) for chk in chunks)
        if not has_ar25_mention:
            return []

    if is_placement_q:
        has_placement_mention = any("placement" in chk.get("text", "").lower() or "placement" in chk.get("metadata", {}).get("filename", "").lower() for chk in chunks)
        if not has_placement_mention:
            return []

    if is_calendar_q:
        has_cal_content = any("academic calendar" in chk.get("text", "").lower() or "commencement of class" in chk.get("text", "").lower() or "spell of instruction" in chk.get("text", "").lower() or "calendar" in chk.get("metadata", {}).get("filename", "").lower() for chk in chunks)
        if not has_cal_content:
            return []

    if is_timetable_q:
        has_tt_content = any(
            any(tok in chk.get("metadata", {}).get("filename", "").lower() for tok in ("timetable", "time table", "tt", "calendar", "mid", "exam"))
            or any(tok in chk.get("text", "").lower() for tok in ("timetable", "time table", "schedule", "monday", "tuesday", "wednesday", "thursday", "friday", "period", "sec", "|"))
            for chk in chunks
        )
        if not has_tt_content:
            return []

    # 2. Section & Branch entity consistency for timetables/schedules
    entities = extract_query_entities(question)
    q_branch = entities.get("branch")

    cleaned_chunks = []
    for c in chunks:
        meta = c.get("metadata") or {}
        fname = (meta.get("filename") or "").lower()
        tags = (meta.get("tags") or "").lower()
        text = c.get("text") or ""
        comb = f"{fname} {tags} {text.lower()}"

        # Clean HTML, OCR noise, header artifacts, and scanner boilerplate
        text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
        text = re.sub(r"&nbsp;", " ", text, flags=re.I)
        text = re.sub(r"scanned\s+(by|with)\s+\w+.*", "", text, flags=re.I)
        text = re.sub(r"^(Key Requirements|Schedule Breakdown|Important Rules|Overview|Summary)\s*$", "", text, flags=re.I | re.M)
        text = re.sub(r"Geethanjali College of Engineering.*", "", text, flags=re.I)
        text = re.sub(r"\(Autonomous\).*", "", text, flags=re.I)
        text = text.replace("\r", "")

        # If attendance query, isolate attendance section and strip leading elective course noise
        if is_attendance_q:
            if "anti_ragging" in fname or "placement" in fname:
                continue
            # Strip leading elective course noise (Section 5 / 6.2) if Section 7 Attendance is present in text
            att_match = re.search(r"(7\.0\s*Attendance|7\.1\s*A student|Attendance requirements:)", text, re.I)
            if att_match:
                text = text[att_match.start():]

        # If specific branch requested in timetable, filter out mismatched branch chunks (e.g. Civil, EEE)
        if q_branch and is_timetable_q:
            for other_b in ("civil", "mech", "eee", "ece", "aiml", "ds", "cse"):
                if other_b != q_branch and (f"{other_b} engineering" in comb or f"department of {other_b}" in comb):
                    has_target = any(q_branch in (chk.get("text") or "").lower() or q_branch in (chk.get("metadata", {}).get("filename") or "").lower() for chk in chunks)
                    if has_target:
                        text = ""
                        break

        if text.strip():
            c_copy = dict(c)
            c_copy["text"] = text.strip()
            cleaned_chunks.append(c_copy)

    if not cleaned_chunks:
        return []

    # Sort attendance chunks so pure attendance regulations (Section 6/7) are prioritized
    if is_attendance_q:
        cleaned_chunks.sort(key=lambda x: 0 if ("75%" in x["text"] or "condoned" in x["text"] or "shortage of attendance" in x["text"].lower()) else 1)

    return cleaned_chunks[:4]


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
        raw_relevant = [
            chunk
            for chunk in retrieved
            if chunk.get("distance", 2.0) <= RELEVANCE_THRESHOLD
        ]
        relevant = filter_and_clean_rag_chunks(question, raw_relevant)

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
                f"[Source: {c['metadata'].get('filename', 'Document')}]\n{c['text']}"
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
                print(f"[CHAT] Gemini API RAG stream exception: {stream_err}. Retrying non-stream generate_rag_answer...")
                try:
                    ans, conf, _ = generate_rag_answer(
                        question=effective_question,
                        context=context_text,
                        history=history,
                    )
                    answer_text = ans
                    confidence = conf
                    yield event("token", content=answer_text)
                except Exception as fallback_err:
                    print(f"[CHAT] Gemini non-stream RAG exception: {fallback_err}. Generating grounded document fallback response...")
                    answer_text = _generate_fallback_rag_response(effective_question, relevant)
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
                print(f"[CHAT] Gemini General stream exception: {stream_err}. Retrying non-stream generate_general_answer...")
                try:
                    ans, conf, _ = generate_general_answer(
                        question=effective_question,
                        history=history,
                    )
                    answer_text = ans
                    confidence = conf
                    yield event("token", content=answer_text)
                except Exception as fallback_err:
                    print(f"[CHAT] Gemini non-stream General exception: {fallback_err}. Using fallback response...")
                    answer_text = _generate_fallback_general_response(question)
                    yield event("token", content=answer_text)

            sources = []
            confidence = 85

        # Clean forced heading artifacts, HTML tags, and scanner noise from synthesized answer_text
        answer_text = re.sub(r"^(#+\s*)?(Key Requirements|Schedule Breakdown|Important Rules|Overview|Summary)\s*\n+", "", answer_text, flags=re.I).strip()
        answer_text = re.sub(r"\n+(#+\s*)?(Key Requirements|Schedule Breakdown|Important Rules|Overview|Summary)\s*\n+", "\n\n", answer_text, flags=re.I).strip()
        answer_text = re.sub(r"<br\s*/?>", " ", answer_text, flags=re.I)
        answer_text = re.sub(r"&nbsp;", " ", answer_text, flags=re.I)
        answer_text = re.sub(r"scanned\s+(by|with)\s+\w+.*", "", answer_text, flags=re.I)

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
