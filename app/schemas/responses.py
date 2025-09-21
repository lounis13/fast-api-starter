from __future__ import annotations

from pydantic import BaseModel, Field


class FactResponse(BaseModel):
    text: str = Field(..., description="The fact text")
    source: str = Field(..., description="The source of the fact")
