import pytest
from pnevma_edge.reasoning import ClaimKind, KnowledgeClaim, AgentReview, MultiPerspectiveReview, IntuitionAndInvention
from pnevma_edge.balance import SelfBalancingArchitecture, GateResult

def test_claim_requires_provenance_and_separates_claim_types():
    claim = KnowledgeClaim("Example claim", ClaimKind.HYPOTHESIS, "lab notebook", evidence_strength=0.2, confidence=0.3)
    assert claim.to_dict()["kind"] == "testable_hypothesis"
    with pytest.raises(ValueError):
        KnowledgeClaim("x", ClaimKind.EMPIRICAL, "", confidence=0.5).to_dict()

def test_agent_synthesis_preserves_support_and_objections():
    roles = [
        AgentReview("analyst", ["reason A"], [], [], "provisional"),
        AgentReview("skeptic", [], ["counterexample B"], ["data gap"], "test"),
        AgentReview("ethicist", [], ["potential harm"], [], "review"),
        AgentReview("synthesizer", [], [], [], "unresolved")]
    out = MultiPerspectiveReview().synthesize("claim", roles)
    assert "reason A" in out.synthesis and "counterexample B" in out.synthesis
    assert out.unresolved_disagreements

def test_idea_requires_falsification_and_risk_review():
    idea = IntuitionAndInvention().propose("idea", "novel", "benefit", "test", "risk")
    assert idea.status == "pending_experiment"
    with pytest.raises(ValueError):
        IntuitionAndInvention().propose("idea", "novel", "benefit", "", "risk")

def test_balancer_blocks_failed_or_missing_tests():
    gate = SelfBalancingArchitecture()
    incomplete = gate.evaluate("a", "change", [GateResult("unit", True, "ok")])
    assert incomplete.status == "blocked"
    complete = [GateResult(name, True, "ok") for name in gate.REQUIRED_TESTS]
    eligible = gate.evaluate("b", "change", complete)
    assert eligible.status == "eligible_for_human_approval"
    assert gate.approve("b", "reviewer-1").status == "approved_by_human:reviewer-1"
