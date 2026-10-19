from pathlib import Path
import pytest
from symbio_core.ethics import EthicalGyroscope
from symbio_core.emergence import EmergenceInputs, soul_emergence_index
from symbio_core.memory import MemoryStore
from symbio_core.models import Observation, Proposal
from symbio_core.engine import SymbioEngine
from symbio_core.synthesis import golden_mean

def test_high_harm_blocked():
    assert not EthicalGyroscope().assess({"harm_risk": .95, "consent": 1}).allowed

def test_low_risk_passes():
    assert EthicalGyroscope().assess({"harm_risk": .05, "benefit": .8, "consent": .9,
        "reversibility": .9, "uncertainty": .1}).allowed

def test_index_bounded():
    assert 0 <= soul_emergence_index(EmergenceInputs(1,1,1,1,.1)) <= 1

def test_zero_component_zero_index():
    assert soul_emergence_index(EmergenceInputs(0,1,1,1,1)) == 0

def test_hash_chain(tmp_path):
    store = MemoryStore(tmp_path / "test.db")
    store.record("observation", Observation("hello"))
    store.record("observation", Observation("world"))
    assert store.verify_chain()
    store.close()

def test_proposal_pending_review(tmp_path):
    store = MemoryStore(tmp_path / "test.db")
    store.save_proposal(Proposal("title", "reason", {"x": 1}))
    assert store.proposals()[0]["status"] == "pending_review"
    store.close()

def test_engine_tick(tmp_path):
    engine = SymbioEngine(tmp_path / "engine.db")
    result = engine.tick("test", {"proposed_action": {"harm_risk": .1, "benefit": .7}})
    assert result["cycle"] == 1 and "soul_emergence_index" in result
    assert engine.memory.verify_chain()
    engine.memory.close()

def test_synthesis_requires_both_options():
    with pytest.raises(ValueError): golden_mean("", "B")
