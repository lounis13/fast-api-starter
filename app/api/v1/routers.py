from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, Depends

from app.application.use_cases import get_random_fact as get_random_fact_uc
from app.domain.entities import Fact
from app.di.container import CatFactProviderDep
from app.schemas.responses import FactResponse

router = APIRouter(prefix="/v1", tags=["facts"])


async def get_random_fact_safe(provider: CatFactProviderDep) -> Fact:
    """API-layer safe wrapper around the use case to ensure HTTP 500 is rendered as JSON.

    We intentionally translate unexpected exceptions into HTTPException(500) so that
    FastAPI always returns a JSON error body (handled by our HTTPException handler),
    even under TestClient default behavior.
    """
    from fastapi import HTTPException

    try:
        return await get_random_fact_uc(provider)
    except HTTPException:
        # Preserve explicit HTTP errors raised by the route logic
        raise
    except Exception as exc:  # noqa: BLE001 - translate to HTTP error for consistent API contract
        raise HTTPException(status_code=500, detail="Internal Server Error") from exc


@router.get("/facts/random", response_model=FactResponse, summary="Get a random fact")
async def get_random_fact(
        fact: Annotated[Fact, Depends(get_random_fact_safe)],
        min_length: Annotated[int | None, Query(ge=1, le=500)] = None,
) -> FactResponse:
    if min_length is not None and len(fact.text) < min_length:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No fact satisfies the requested minimum length")
    return FactResponse(text=fact.text, source=fact.source)
