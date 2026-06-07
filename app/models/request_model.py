from typing import Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    # When omitted, the backend creates a new session and returns its id.
    session_id: Optional[str] = None
