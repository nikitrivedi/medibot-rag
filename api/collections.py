from fastapi import APIRouter, HTTPException

from api.models import CollectionsResponse
from chunker.medichunker import DEPARTMENT_ACCESS

router = APIRouter(prefix="/api", tags=["collections"])

VALID_ROLES = {role for roles in DEPARTMENT_ACCESS.values() for role in roles}


def accessible_collections(role: str) -> list[str]:
    return sorted(name for name, roles in DEPARTMENT_ACCESS.items() if role in roles)


@router.get("/collections/{role}", response_model=CollectionsResponse)
def get_collections(role: str) -> CollectionsResponse:
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")

    return CollectionsResponse(role=role, collections=accessible_collections(role))
