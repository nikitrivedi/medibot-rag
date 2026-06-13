from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class ChatRequest(BaseModel):
    question: str
    role: str


class ChatResponse(BaseModel):
    answer: str
    retrieval_type: str
    role: str
    sources: list[dict]
