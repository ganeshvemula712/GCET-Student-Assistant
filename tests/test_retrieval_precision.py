from unittest.mock import MagicMock, patch
from backend.app.services.vector_store import (
    extract_query_entities,
    score_chunk_metadata_alignment,
    search_chunks,
    deduplicate_and_rank_chunks,
)


def test_deduplicate_and_rank_chunks_filters_duplicate_and_overrepresented_pages():
    candidates = [
        {"text": "Attendance requirement is 75% aggregate.", "metadata": {"filename": "doc1.pdf", "page": 1}, "distance": 0.2},
        {"text": "Attendance requirement is 75% aggregate.", "metadata": {"filename": "doc1.pdf", "page": 1}, "distance": 0.22},  # Duplicate text
        {"text": "Mobile phone restriction in classes.", "metadata": {"filename": "doc1.pdf", "page": 1}, "distance": 0.3},
        {"text": "Dress code uniform guidelines.", "metadata": {"filename": "doc1.pdf", "page": 1}, "distance": 0.4},  # 3rd chunk on page 1 -> should cap at 2
        {"text": "Placement eligibility criteria details.", "metadata": {"filename": "doc2.pdf", "page": 2}, "distance": 0.35},
    ]

    deduped = deduplicate_and_rank_chunks(candidates, max_results=3)

    assert len(deduped) == 3
    assert deduped[0]["text"] == "Attendance requirement is 75% aggregate."
    assert deduped[1]["text"] == "Mobile phone restriction in classes."
    assert deduped[2]["text"] == "Placement eligibility criteria details."


def test_section_identifier_d_is_not_lost():
    """F: Verify single-character section identifier 'D' is extracted cleanly."""
    entities_1 = extract_query_entities("What is the timetable for 4th year DS-D 1st semester?")
    assert entities_1["branch"] == "ds"
    assert entities_1["section"] == "d"
    assert entities_1["year"] == "4"

    entities_2 = extract_query_entities("Show me section D schedule for 2nd year AIML")
    assert entities_2["branch"] == "aiml"
    assert entities_2["section"] == "d"
    assert entities_2["year"] == "2"


def test_search_chunks_prioritizes_ds_d_over_aiml_d():
    """A: Verify DS-D timetable document is prioritized over AIML-D when query asks for DS-D."""
    mock_coll = MagicMock()
    mock_coll.query.return_value = {
        "documents": [["AIML-D Content", "DS-D Content"]],
        "metadatas": [[
            {"filename": "IV-BTech 1sem AIML-D section TT.jpeg", "tags": "4th Year, 1st Semester, AIML-D, AI ML, Timetable"},
            {"filename": "IV-BTech 1sem DS-D section TT.jpeg", "tags": "4th Year, 1st Semester, DS-D, Data Science, Timetable"}
        ]],
        "distances": [[0.42, 0.44]],  # Raw distance: AIML-D looks slightly closer
    }

    with patch("backend.app.services.vector_store.get_collection", return_value=mock_coll):
        results = search_chunks(
            query_embedding=[0.1] * 768,
            n_results=2,
            query_text="What is the timetable for 4th year DS-D 1st semester?",
        )

    # Top result MUST be DS-D despite higher raw distance
    assert len(results) == 2
    assert results[0]["metadata"]["filename"] == "IV-BTech 1sem DS-D section TT.jpeg"
    assert results[0]["distance"] < results[1]["distance"]


def test_search_chunks_prioritizes_aiml_a_over_aiml_d():
    """B: Verify AIML-A section timetable is prioritized over AIML-D when query asks for AIML-A."""
    mock_coll = MagicMock()
    mock_coll.query.return_value = {
        "documents": [["AIML-D Content", "AIML-A Content"]],
        "metadatas": [[
            {"filename": "IV-BTech 1sem AIML-D section TT.jpeg", "tags": "4th Year, 1st Semester, AIML-D, AI ML, Timetable"},
            {"filename": "II-BTech 1sem AIML-A section TT.jpeg", "tags": "2nd Year, 1st Semester, AIML-A, AI ML, Timetable"}
        ]],
        "distances": [[0.40, 0.45]],
    }

    with patch("backend.app.services.vector_store.get_collection", return_value=mock_coll):
        results = search_chunks(
            query_embedding=[0.1] * 768,
            n_results=2,
            query_text="What is the timetable for 2nd year AIML-A section?",
        )

    assert len(results) == 2
    assert results[0]["metadata"]["filename"] == "II-BTech 1sem AIML-A section TT.jpeg"


def test_search_chunks_prioritizes_cs_a():
    """C: Verify CS-A timetable document is prioritized when CS-A is queried."""
    mock_coll = MagicMock()
    mock_coll.query.return_value = {
        "documents": [["AIML-D Content", "CS-A Content"]],
        "metadatas": [[
            {"filename": "IV-BTech 1sem AIML-D section TT.jpeg", "tags": "4th Year, 1st Semester, AIML-D, AI ML, Timetable"},
            {"filename": "IV-BTech 1sem CS-A section TT.pdf", "tags": "4th Year, 1st Semester, CS-A, Timetable"}
        ]],
        "distances": [[0.40, 0.43]],
    }

    with patch("backend.app.services.vector_store.get_collection", return_value=mock_coll):
        results = search_chunks(
            query_embedding=[0.1] * 768,
            n_results=2,
            query_text="What is the timetable for 4th year CS-A section?",
        )

    assert len(results) == 2
    assert results[0]["metadata"]["filename"] == "IV-BTech 1sem CS-A section TT.pdf"


def test_search_chunks_general_queries_unaffected_by_entity_boost():
    """D: Verify general non-timetable queries retain standard raw vector similarity ranking."""
    mock_coll = MagicMock()
    mock_coll.query.return_value = {
        "documents": [["Doc A", "Doc B"]],
        "metadatas": [[
            {"filename": "Academic Calendar 2025-26.pdf", "tags": "Calendar"},
            {"filename": "Regulations 2025.pdf", "tags": "Regulations"}
        ]],
        "distances": [[0.30, 0.50]],
    }

    with patch("backend.app.services.vector_store.get_collection", return_value=mock_coll):
        results = search_chunks(
            query_embedding=[0.1] * 768,
            n_results=2,
            query_text="What is the minimum attendance requirement at GCET?",
        )

    assert len(results) == 2
    assert results[0]["distance"] == 0.30
    assert results[1]["distance"] == 0.50


def test_search_chunks_out_of_scope_query_maintains_fallback():
    """E: Verify out-of-scope query does not get artificially boosted to look like a close match."""
    meta = {"filename": "IV-BTech 1sem AIML-D section TT.jpeg", "tags": "4th Year, 1st Semester, AIML-D, AI ML, Timetable"}
    entities = extract_query_entities("What is the timetable for 1st year Mechanical Engineering section B?")

    raw_dist = 0.60
    adjusted_dist = score_chunk_metadata_alignment(meta, entities, raw_dist)

    # Conflicting branch ('mech' vs 'aiml') MUST apply conflict penalty
    assert adjusted_dist > raw_dist


def test_deduplicate_and_rank_chunks_empty_input():
    """1. Empty input must return []"""
    assert deduplicate_and_rank_chunks([]) == []


def test_deduplicate_and_rank_chunks_single_chunk():
    """2. One valid chunk must remain unchanged."""
    chunk = {"text": "GCET Attendance Rule", "metadata": {"filename": "AR22.pdf", "page": 1}, "distance": 0.1}
    res = deduplicate_and_rank_chunks([chunk], max_results=3)
    assert len(res) == 1
    assert res[0] == chunk


def test_deduplicate_and_rank_chunks_exact_duplicates():
    """3. Exact duplicate text must be removed, preserving highest relevance (lowest distance)."""
    candidates = [
        {"text": "75% aggregate attendance required.", "metadata": {"filename": "AR22.pdf", "page": 1}, "distance": 0.30},
        {"text": "75% aggregate attendance required.", "metadata": {"filename": "AR22.pdf", "page": 1}, "distance": 0.15},
    ]
    res = deduplicate_and_rank_chunks(candidates, max_results=3)
    assert len(res) == 1
    assert res[0]["distance"] == 0.15


def test_deduplicate_and_rank_chunks_near_duplicates():
    """4. Chunks with normalized leading 30 words identical must be deduplicated."""
    w30 = " ".join([f"word{i}" for i in range(30)])
    c1 = {"text": f"{w30} extra text A", "metadata": {"filename": "doc.pdf", "page": 1}, "distance": 0.2}
    c2 = {"text": f"{w30} extra text B", "metadata": {"filename": "doc.pdf", "page": 1}, "distance": 0.25}
    res = deduplicate_and_rank_chunks([c1, c2], max_results=3)
    assert len(res) == 1
    assert res[0]["text"] == f"{w30} extra text A"


def test_deduplicate_and_rank_chunks_same_page_capping():
    """5. Maximum 2 chunks from same (filename, page). Two highest-ranked retained."""
    candidates = [
        {"text": "Chunk 1 on page 1", "metadata": {"filename": "overview.pdf", "page": 1}, "distance": 0.1},
        {"text": "Chunk 2 on page 1", "metadata": {"filename": "overview.pdf", "page": 1}, "distance": 0.2},
        {"text": "Chunk 3 on page 1", "metadata": {"filename": "overview.pdf", "page": 1}, "distance": 0.3},
    ]
    res = deduplicate_and_rank_chunks(candidates, max_results=3)
    assert len(res) == 2
    assert res[0]["text"] == "Chunk 1 on page 1"
    assert res[1]["text"] == "Chunk 2 on page 1"


def test_deduplicate_and_rank_chunks_complementary_pages():
    """6. Different pages from the same document allowed."""
    candidates = [
        {"text": "Attendance rules on page 1", "metadata": {"filename": "AR22.pdf", "page": 1}, "distance": 0.1},
        {"text": "Exam rules on page 2", "metadata": {"filename": "AR22.pdf", "page": 2}, "distance": 0.15},
    ]
    res = deduplicate_and_rank_chunks(candidates, max_results=3)
    assert len(res) == 2


def test_deduplicate_and_rank_chunks_complementary_documents():
    """7. Different documents allowed."""
    candidates = [
        {"text": "Attendance rules in AR22", "metadata": {"filename": "AR22.pdf", "page": 1}, "distance": 0.1},
        {"text": "Placement rules in Placement Policy", "metadata": {"filename": "Placement.pdf", "page": 1}, "distance": 0.12},
    ]
    res = deduplicate_and_rank_chunks(candidates, max_results=3)
    assert len(res) == 2


def test_deduplicate_and_rank_chunks_ranking_preservation():
    """8. Lower ChromaDB distance remains higher priority in returned output."""
    candidates = [
        {"text": "Rank 3 text", "metadata": {"filename": "doc.pdf", "page": 3}, "distance": 0.4},
        {"text": "Rank 1 text", "metadata": {"filename": "doc.pdf", "page": 1}, "distance": 0.1},
        {"text": "Rank 2 text", "metadata": {"filename": "doc.pdf", "page": 2}, "distance": 0.2},
    ]
    res = deduplicate_and_rank_chunks(candidates, max_results=3)
    assert res[0]["text"] == "Rank 1 text"
    assert res[1]["text"] == "Rank 2 text"
    assert res[2]["text"] == "Rank 3 text"


def test_deduplicate_and_rank_chunks_metadata_preservation():
    """9. Verify filename, page, category, tags and metadata remain intact."""
    candidate = {
        "text": "Metadata test snippet text",
        "metadata": {"filename": "Policy.pdf", "page": 5, "category": "Regulations", "tags": "Academic, Rules"},
        "distance": 0.15,
    }
    res = deduplicate_and_rank_chunks([candidate], max_results=3)
    assert len(res) == 1
    m = res[0]["metadata"]
    assert m["filename"] == "Policy.pdf"
    assert m["page"] == 5
    assert m["category"] == "Regulations"
    assert m["tags"] == "Academic, Rules"


def test_deduplicate_and_rank_chunks_multi_doc_unchanged():
    """10. Valid non-duplicate chunks from different docs remain available up to max_results."""
    candidates = [
        {"text": f"Unique content from doc {i}", "metadata": {"filename": f"doc_{i}.pdf", "page": 1}, "distance": 0.1 * i}
        for i in range(1, 6)
    ]
    res = deduplicate_and_rank_chunks(candidates, max_results=3)
    assert len(res) == 3
    assert res[0]["metadata"]["filename"] == "doc_1.pdf"
    assert res[1]["metadata"]["filename"] == "doc_2.pdf"
    assert res[2]["metadata"]["filename"] == "doc_3.pdf"

