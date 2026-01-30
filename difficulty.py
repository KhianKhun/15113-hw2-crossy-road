# difficulty.py
from __future__ import annotations
from dataclasses import dataclass

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

@dataclass(frozen=True)
class SpeedProfile:
    start_mult: float   # score=0 时的倍速（越小越慢）
    max_mult: float     # 上限阈值
    per_score: float    # 每 1 分增加多少倍速（线性）

    def mult(self, score: int) -> float:
        # 线性增长 + 封顶
        return clamp(self.start_mult + self.per_score * max(0, score), self.start_mult, self.max_mult)

# 你可以在这里统一调参（方便调试）
CAR_PROFILE   = SpeedProfile(start_mult=0.45, max_mult=1.10, per_score=0.007)
LOG_PROFILE   = SpeedProfile(start_mult=0.40, max_mult=1.05, per_score=0.008)
TRAIN_PROFILE = SpeedProfile(start_mult=0.40, max_mult=1.05, per_score=0.006)

def lane_speed_multiplier(kind: str, score: int) -> float:
    """Return current speed multiplier for lane kind."""
    if kind == "road":
        return CAR_PROFILE.mult(score)
    if kind == "water":
        return LOG_PROFILE.mult(score)
    if kind == "rail":
        return TRAIN_PROFILE.mult(score)
    return 1.0

def debug_string(score: int) -> str:
    """For debugging in HUD."""
    car = CAR_PROFILE.mult(score)
    log = LOG_PROFILE.mult(score)
    trn = TRAIN_PROFILE.mult(score)
    return f"spd x car:{car:.2f} log:{log:.2f} train:{trn:.2f}"
