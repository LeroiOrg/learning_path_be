from pydantic import BaseModel

class ProcessFileRequest(BaseModel):
    fileName: str
    fileBase64: str

class TopicRequest(BaseModel):
    topic: str
