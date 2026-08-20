from unittest.mock import MagicMock, patch
from backend.app.services.vector_store import (
    extract_query_entities,
    score_chunk_metadata_alignment,
    search_chunks,
)


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
