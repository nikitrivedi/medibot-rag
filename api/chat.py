from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_session
from api.models import ChatRequest, ChatResponse
from api.rag import chat_answer

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, session: dict = Depends(get_session)) -> ChatResponse:
    token_role = session.get("role")
    if request.role != token_role:
        raise HTTPException(status_code=403, detail="Role does not match session token")

    try:
        result = chat_answer(request.question, request.role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ChatResponse(**result)
