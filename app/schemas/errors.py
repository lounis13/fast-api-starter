from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard API error payload.

    - error: machine-readable error code (snake_case)
    - message: human-readable message (safe to display)
    - details: optional structured details (validation errors, etc.)
    """

    error: str = Field(..., description="Machine-readable error code in snake_case")
    message: str = Field(..., description="Human-readable error message")
    details: Any | None = Field(
        default=None, description="Optional structured details (e.g., validation errors)"
    )
