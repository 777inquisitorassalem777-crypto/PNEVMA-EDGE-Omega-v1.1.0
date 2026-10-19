import json
from symbio_core.spiral import AppendOnlyLedger, Experience, LivingSpiral, EthicalGyroscope, run_simulation

def test_ledger(tmp_path):
    l=AppendOnlyLedger(tmp_path/"ledger.sqlite")
    l.append("test",{"x":1}); l.append("test",{"x":2})
    assert l.verify()["ok"] and l.verify()["events"]==2
    l.close()

def test_ethics_flags():
    x=EthicalGyroscope().assess({"harm_risk":.95,"consent":.1,"reversibility":.1,"uncertainty":.9,"benefit":.9})
    assert x["status"]=="pause_and_review" and "high_harm_risk" in x["flags"]

def test_candidate_is_not_applied(tmp_path):
    p=tmp_path/"p.json"; p.write_text(json.dumps({"lenses":[]}),encoding="utf-8")
    s=LivingSpiral(tmp_path/"db.sqlite",p)
    out=None
    for _ in range(5): out=s.process(Experience("test",{"proposed_action":{"harm_risk":.2}},.5,.1,.4))
    assert out["candidate_paradigm"]["status"]=="pending_review"
    assert s.version=="symbio-living-spiral-0.3.0"
    s.close()

def test_simulation(tmp_path):
    r=run_simulation(4,0,tmp_path/"sim.sqlite")
    assert r["state"]["cycles"]==4 and r["ledger_integrity"]["ok"]
    assert r["paradigm_lenses"]>=10
