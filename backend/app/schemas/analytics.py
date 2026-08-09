from typing import List, Optional
from pydantic import BaseModel


class TimeSeriesPoint(BaseModel):
    date: str
    count: int


class AnalyticsSummaryResponse(BaseModel):
    total_conversations: int
    total_messages: int
    total_documents: int
    total_chunks: int
    total_pages: int
    avg_messages_per_conversation: float
    avg_confidence: float
    grounded_responses_count: int
    total_sources_cited: int
    total_file_size_bytes: int
    conversations_over_time: List[TimeSeriesPoint]
    messages_over_time: List[TimeSeriesPoint]
    documents_status: dict
    is_admin: bool
