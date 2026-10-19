from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any
import json
import uuid

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class Observation:
    text: str
    context: dict[str, Any] | None = None
    source: str = "user"
    created_at: str = ""

    def __post_init__(self):
        if not self.text.strip():
            raise ValueError("Observation text must not be empty")
        self.context = self.context or {}
        self.created_at = self.created_at or utc_now()

@dataclass
class EthicalAssessment:
    score: float
    allowed: bool
    rationale: list[str]
    uncertainty: float
    reversibility: float
    consent: float

@dataclass
class Reflection:
    observation: str
    interpretation: str
    current_position: str
    counterargument: str
    confidence: float
    update_trigger: str
    created_at: str = ""

    def __post_init__(self):
        self.created_at = self.created_at or utc_now()
        self.confidence = min(1.0, max(0.0, float(self.confidence)))

@dataclass
class Proposal:
    title: str
    rationale: str
    change: dict[str, Any]
    status: str = "pending_review"
    proposal_id: str = ""

    def __post_init__(self):
        self.proposal_id = self.proposal_id or str(uuid.uuid4())
        if self.status not in {"pending_review", "accepted", "rejected", "superseded"}:
            raise ValueError("Unsupported proposal status")

def jsonable(obj: Any) -> str:
    return json.dumps(asdict(obj) if hasattr(obj, "__dataclass_fields__") else obj,
                      ensure_ascii=False, sort_keys=True, default=str)
