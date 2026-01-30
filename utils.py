# utils.py
from __future__ import annotations
from dataclasses import dataclass

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

@dataclass(frozen=True)
class IPoint:
    x: int
    y: int
