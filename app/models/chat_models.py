from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class Message(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_message: str
    ai_response: str

class ChatConversation(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_email: str
    roadmap_topic: str
    conversation: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str
        }