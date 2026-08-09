from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    conversations: int
    responses: int
    documents: int
    account: str