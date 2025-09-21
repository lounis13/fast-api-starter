from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, Depends

from app.application.use_cases import get_random_fact as get_random_fact_uc
from app.domain.entities import Fact
from app.schemas.responses import FactResponse

router = APIRouter(prefix="/v1", tags=["facts"])


@router.get("/facts/random", response_model=FactResponse, summary="Get a random fact")
async def get_random_fact(
        fact: Annotated[Fact, Depends(get_random_fact_uc)],
        min_length: Annotated[int | None, Query(ge=1, le=500)] = None,
) -> FactResponse:
    if min_length is not None and len(fact.text) < min_length:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No fact satisfies the requested minimum length")
    return FactResponse(text=fact.text, source=fact.source)
