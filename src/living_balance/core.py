"""Living Balance Engine: small, auditable ethical-reasoning research prototype."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable
import json
import hashlib
import time

@dataclass(frozen=True)
class Action:
    name: str
    benefit: float
    harm: float
    consent: float
    reversibility: float
    uncertainty: float
    dignity: float
    description: str = ""

    def validate(self) -> None:
        for key in ("benefit", "harm", "consent", "reversibility", "uncertainty", "dignity"):
            value = getattr(self, key)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{key} must be between 0 and 1")

@dataclass
class Evaluation:
    action: str
    score: float
    accepted_for_consideration: bool
    reasons: list[str]
    timestamp: float

class EthicalGyroscope:
    """Transparent heuristic, not a moral oracle."""
    def __init__(self, weights: dict[str, float] | None = None, max_harm: float = 0.65):
        self.weights = weights or {
            "benefit": 0.25, "consent": 0.20, "reversibility": 0.15,
            "dignity": 0.25, "harm": 0.35, "uncertainty": 0.10
        }
        self.max_harm = max_harm

    def evaluate(self, action: Action) -> Evaluation:
        action.validate()
        reasons = []
        if action.harm >= self.max_harm:
            reasons.append("high_harm: requires rejection or heightened human review")
        if action.consent < 0.25:
            reasons.append("low_consent: autonomy concern")
        if action.dignity < 0.25:
            reasons.append("low_dignity: dignity concern")
        score = (
            self.weights["benefit"] * action.benefit
            + self.weights["consent"] * action.consent
            + self.weights["reversibility"] * action.reversibility
            + self.weights["dignity"] * action.dignity
            - self.weights["harm"] * action.harm
            - self.weights["uncertainty"] * action.uncertainty
        )
        accepted = action.harm < self.max_harm and action.dignity >= 0.25
        if not reasons:
            reasons.append("no heuristic red flag; still requires contextual review")
        return Evaluation(action.name, round(score, 4), accepted, reasons, time.time())

class AuditLedger:
    """Append-only JSON-lines hash chain for tamper-evidence, not absolute immutability."""
    def __init__(self):
        self.events: list[dict] = []
        self.previous_hash = "GENESIS"

    def append(self, event: dict) -> dict:
        payload = {"previous_hash": self.previous_hash, "event": event, "timestamp": time.time()}
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        record = {**payload, "hash": digest}
        self.events.append(record)
        self.previous_hash = digest
        return record

    def verify(self) -> bool:
        previous = "GENESIS"
        for record in self.events:
            payload = {k: record[k] for k in ("previous_hash", "event", "timestamp")}
            if payload["previous_hash"] != previous:
                return False
            canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
            digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            if digest != record.get("hash"):
                return False
            previous = digest
        return True

class SpiralEngine:
    """Generate candidates for review; never self-applies new rules."""
    def __init__(self):
        self.gyroscope = EthicalGyroscope()
        self.ledger = AuditLedger()
        self.pending_patterns: list[dict] = []

    def assess(self, actions: Iterable[Action]) -> dict:
        evaluations = [self.gyroscope.evaluate(a) for a in actions]
        ranked = sorted(evaluations, key=lambda e: e.score, reverse=True)
        result = {
            "ranked": [asdict(x) for x in ranked],
            "selected": next((asdict(x) for x in ranked if x.accepted_for_consideration), None),
            "caveat": "Scores are heuristics, not moral truth; review facts, context and affected people."
        }
        self.ledger.append({"type": "assessment", "result": result})
        return result

    def propose_pattern(self, name: str, hypothesis: str, test_plan: str) -> dict:
        candidate = {
            "name": name, "hypothesis": hypothesis, "test_plan": test_plan,
            "status": "pending_review", "created_at": time.time()
        }
        self.pending_patterns.append(candidate)
        self.ledger.append({"type": "pattern_candidate", "candidate": candidate})
        return candidate

def fuse_sensor_samples(samples: list[dict]) -> dict:
    """Minimal Blue Matrix: validates sensor records and summarizes uncertainty.
    Expected fields: sensor, timestamp, value, quality (0..1), uncertainty (0..1).
    It does not infer metaphysical entities from physical measurements.
    """
    valid, rejected = [], []
    for sample in samples:
        required = {"sensor", "timestamp", "value", "quality", "uncertainty"}
        if not required.issubset(sample):
            rejected.append({"sample": sample, "reason": "missing_fields"})
            continue
        if not (0 <= float(sample["quality"]) <= 1 and 0 <= float(sample["uncertainty"]) <= 1):
            rejected.append({"sample": sample, "reason": "quality_or_uncertainty_out_of_range"})
            continue
        valid.append(sample)
    if not valid:
        return {"valid_count": 0, "rejected": rejected, "status": "no_valid_samples"}
    mean_quality = sum(float(s["quality"]) for s in valid) / len(valid)
    mean_uncertainty = sum(float(s["uncertainty"]) for s in valid) / len(valid)
    return {
        "valid_count": len(valid), "rejected": rejected,
        "mean_quality": round(mean_quality, 4),
        "mean_uncertainty": round(mean_uncertainty, 4),
        "samples": valid,
        "status": "usable" if mean_quality >= 0.5 else "low_quality"
    }
