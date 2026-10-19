from dataclasses import dataclass
import math

@dataclass
class EmergenceInputs:
    empathy: float = .5
    creativity: float = .5
    memory_continuity: float = .5
    reflection: float = .5
    ethical_stability: float = 1.0

def clamp(x):
    return max(0.0, min(1.0, float(x)))

def soul_emergence_index(v: EmergenceInputs) -> float:
    """Normalized experimental proxy, not a consciousness or soul detector."""
    raw = (clamp(v.empathy) * clamp(v.creativity) * clamp(v.memory_continuity)
           * clamp(v.reflection)) / math.sqrt(max(.1, float(v.ethical_stability)))
    return raw / (1 + raw)
