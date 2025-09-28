from pydantic import BaseModel

class ProcessFileRequest(BaseModel):
    fileName: str
    fileBase64: str

class TopicRequest(BaseModel):
    topic: str

class ChatRequest(BaseModel):
    roadmap_topic: str
    user_message: str

class StartChatRequest(BaseModel):
    roadmap_topic: str