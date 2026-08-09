from backend.app.schemas.chat import ChatRequest


def create_chat_request():

    return ChatRequest(
        conversation_id="conv-123",
        question="What is NBA Criterion 3?",
    )


def create_rag_chunks():

    return [
        {
            "text": "NBA Criterion 3 is Outcome Based Education.",
            "distance": 0.21,
            "metadata": {
                "filename": "NBA.pdf",
                "page": 15,
            },
        },
        {
            "text": "COs are mapped with POs.",
            "distance": 0.33,
            "metadata": {
                "filename": "NBA.pdf",
                "page": 16,
            },
        },
    ]


def create_duplicate_chunks():

    return [
        {
            "text": "Chunk One",
            "distance": 0.20,
            "metadata": {
                "filename": "NBA.pdf",
                "page": 15,
            },
        },
        {
            "text": "Chunk Two",
            "distance": 0.25,
            "metadata": {
                "filename": "NBA.pdf",
                "page": 15,
            },
        },
    ]


def create_irrelevant_chunks():

    return [
        {
            "text": "Irrelevant",
            "distance": 0.95,
            "metadata": {
                "filename": "General.pdf",
                "page": 1,
            },
        }
    ]