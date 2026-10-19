"""Small transparent primitives for flexible, evidence-aware reasoning.

This module is a research scaffold. It does not implement consciousness or a soul.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Iterable
import math
import time

class ClaimKind(str, Enum):
    HISTORICAL = "historical_claim"
    EMPIRICAL = "empirical_claim"
    INTERPRETATION = "spiritual_or_philosophical_interpretation"
    HYPOTHESIS = "testable_hypothesis"
    SPECULATION = "speculation"

@dataclass
class KnowledgeClaim:
    claim: str
    kind: ClaimKind
    source: str
    author: str = ""
    published_at: str = ""
    quoted_text: str = ""
    evidence_strength: float = 0.0
    confidence: float = 0.0
    counterevidence: list[str] | None = None
    limitations: list[str] | None = None

    def validate(self) -> None:
        if not self.claim.strip():
            raise ValueError("claim must not be empty")
        if not self.source.strip():
            raise ValueError("source/provenance must not be empty")
        for key in ("evidence_strength", "confidence"):
            value = getattr(self, key)
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{key} must be finite and in [0, 1]")
        if self.counterevidence is None:
            self.counterevidence = []
        if self.limitations is None:
            self.limitations = []

    def to_dict(self) -> dict:
        self.validate()
        result = asdict(self)
        result["kind"] = self.kind.value
        return result

@dataclass
class AgentReview:
    role: str
    supporting_arguments: list[str]
    objections: list[str]
    uncertainties: list[str]
    recommendation: str

@dataclass
class ReviewSynthesis:
    claim: str
    reviews: list[dict]
    unresolved_disagreements: list[str]
    synthesis: str
    status: str = "requires_human_or_domain_review"
    created_at: float = 0.0

class MultiPerspectiveReview:
    """Preserves arguments for and against; it does not mistake consensus for proof."""
    ROLES = {"analyst", "skeptic", "ethicist", "synthesizer"}
    def synthesize(self, claim: str, reviews: Iterable[AgentReview]) -> ReviewSynthesis:
        items = list(reviews)
        unknown = {r.role for r in items} - self.ROLES
        if unknown:
            raise ValueError(f"unknown review roles: {sorted(unknown)}")
        roles = {r.role for r in items}
        missing = self.ROLES - roles
        disagreements = []
        for r in items:
            disagreements.extend(f"{r.role}: {u}" for u in r.uncertainties)
        if missing:
            disagreements.append("Missing perspectives: " + ", ".join(sorted(missing)))
        support = [a for r in items for a in r.supporting_arguments]
        objections = [a for r in items for a in r.objections]
        synthesis = (
            f"Supporting arguments ({len(support)}): " + ("; ".join(support) or "none supplied") +
            f". Objections ({len(objections)}): " + ("; ".join(objections) or "none supplied") +
            ". Agreement among agents is not independent empirical verification."
        )
        return ReviewSynthesis(claim, [asdict(r) for r in items], disagreements, synthesis, created_at=time.time())

@dataclass
class IdeaCandidate:
    name: str
    novelty_hypothesis: str
    intended_benefit: str
    falsification_test: str
    risk_review: str
    status: str = "pending_experiment"
    created_at: float = 0.0

class IntuitionAndInvention:
    """Generates structured candidate ideas; all candidates remain unapproved."""
    def propose(self, name: str, novelty_hypothesis: str, intended_benefit: str,
                falsification_test: str, risk_review: str) -> IdeaCandidate:
        fields = [name, novelty_hypothesis, intended_benefit, falsification_test, risk_review]
        if any(not x.strip() for x in fields):
            raise ValueError("all fields are required; include a falsification test and risk review")
        return IdeaCandidate(*fields, created_at=time.time())
