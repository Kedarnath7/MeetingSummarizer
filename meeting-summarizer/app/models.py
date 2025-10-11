from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ActionItem(BaseModel):
    task: str
    assignee: Optional[str] = None
    deadline: Optional[str] = None

class SummaryResponse(BaseModel):
    summary: str
    key_decisions: List[str]
    action_items: List[ActionItem]

class MeetingResponse(BaseModel):
    id: int
    filename: str
    message: str
    summary: Dict[str, Any]
    transcript_preview: str
    created_at: str