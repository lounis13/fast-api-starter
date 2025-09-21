from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Fact:
    text: str
    source: str
