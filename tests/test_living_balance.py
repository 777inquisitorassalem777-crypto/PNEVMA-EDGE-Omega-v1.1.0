from living_balance import Action, EthicalGyroscope, AuditLedger, SpiralEngine, fuse_sensor_samples

def test_high_harm_flagged():
    result = EthicalGyroscope().evaluate(Action("danger", .9, .9, .2, .1, .4, .3))
    assert not result.accepted_for_consideration
    assert any("high_harm" in x for x in result.reasons)

def test_ledger_verifies_and_detects_tamper():
    ledger = AuditLedger()
    ledger.append({"hello": "world"})
    assert ledger.verify()
    ledger.events[0]["event"]["hello"] = "changed"
    assert not ledger.verify()

def test_patterns_pending_review():
    engine = SpiralEngine()
    p = engine.propose_pattern("novel", "test hypothesis", "compare on benchmark")
    assert p["status"] == "pending_review"

def test_sensor_fusion_rejects_bad_record():
    out = fuse_sensor_samples([
        {"sensor":"temp", "timestamp":1, "value":20, "quality":.9, "uncertainty":.1},
        {"sensor":"bad", "timestamp":2, "value":0, "quality":2, "uncertainty":.1},
    ])
    assert out["valid_count"] == 1
    assert len(out["rejected"]) == 1
