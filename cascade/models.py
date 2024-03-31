from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    role: str
    content: str

class Conversation(BaseModel):
    messages: List[Message]