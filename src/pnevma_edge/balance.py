"""Compatibility checks and conservative adaptive-change gate."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import time

@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str

@dataclass
class ChangeProposal:
    identifier: str
    description: str
    tests: list[dict]
    status: str
    created_at: float

class SelfBalancingArchitecture:
    """Five-gate release policy; no automatic production mutation."""
    REQUIRED_TESTS = ("unit", "compatibility", "safety", "regression", "reproducibility")
    def __init__(self):
        self.proposals: list[ChangeProposal] = []

    def evaluate(self, identifier: str, description: str, results: list[GateResult]) -> ChangeProposal:
        by_name = {r.name: r for r in results}
        missing = [name for name in self.REQUIRED_TESTS if name not in by_name]
        failed = [name for name in self.REQUIRED_TESTS if name in by_name and not by_name[name].passed]
        unknown = sorted(set(by_name) - set(self.REQUIRED_TESTS))
        tests = [asdict(r) for r in results]
        if missing or failed or unknown:
            status = "blocked"
        else:
            status = "eligible_for_human_approval"
        if missing:
            tests.append({"name": "coverage", "passed": False, "detail": "missing required tests: " + ", ".join(missing)})
        if unknown:
            tests.append({"name": "unexpected_tests", "passed": False, "detail": "unknown test names: " + ", ".join(unknown)})
        proposal = ChangeProposal(identifier, description, tests, status, time.time())
        self.proposals.append(proposal)
        return proposal

    def approve(self, identifier: str, reviewer: str) -> ChangeProposal:
        if not reviewer.strip():
            raise ValueError("reviewer identity is required")
        for p in self.proposals:
            if p.identifier == identifier:
                if p.status != "eligible_for_human_approval":
                    raise ValueError("proposal is not eligible for approval")
                p.status = "approved_by_human:" + reviewer
                return p
        raise KeyError(identifier)
