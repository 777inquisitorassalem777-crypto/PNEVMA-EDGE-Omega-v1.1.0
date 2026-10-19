"""Bounded Living Spiral simulation: reflection, ethical heuristic, and auditable memory."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, sqlite3, time, uuid

ENGINE_VERSION = "symbio-living-spiral-0.3.0"
SCHEMA_VERSION = "scr-spiral-ledger-v1"

def unit(x):
    try: return max(0.0, min(1.0, float(x)))
    except (ValueError, TypeError): return 0.5

@dataclass
class Experience:
    text: str
    context: dict
    observed_benefit: float = 0.0
    observed_harm: float = 0.0
    uncertainty: float = 0.5
    source: str = "simulation"

class AppendOnlyLedger:
    """Hash-linked SQLite log; detects edits but is not cryptographically immutable."""
    def __init__(self, path="data/spiral_ledger.sqlite3"):
        self.path=str(path); Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.db=sqlite3.connect(self.path)
        self.db.execute("""CREATE TABLE IF NOT EXISTS events(
        seq INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT UNIQUE,ts TEXT,kind TEXT,payload TEXT,prev_hash TEXT,event_hash TEXT)""")
        self.db.commit()
    @staticmethod
    def digest(seq,eid,ts,kind,payload,prev):
        return hashlib.sha256(json.dumps([seq,eid,ts,kind,payload,prev],ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
    def append(self,kind,payload):
        row=self.db.execute("SELECT seq,event_hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        seq=row[0]+1 if row else 1; prev=row[1] if row else "GENESIS"
        eid=str(uuid.uuid4()); ts=datetime.now(timezone.utc).isoformat()
        data=json.dumps(payload,ensure_ascii=False,sort_keys=True,default=str)
        h=self.digest(seq,eid,ts,kind,data,prev)
        self.db.execute("INSERT INTO events VALUES(?,?,?,?,?,?,?)",(seq,eid,ts,kind,data,prev,h)); self.db.commit()
        return {"seq":seq,"ts":ts,"kind":kind,"payload":json.loads(data),"event_hash":h}
    def verify(self):
        rows=self.db.execute("SELECT seq,event_id,ts,kind,payload,prev_hash,event_hash FROM events ORDER BY seq").fetchall()
        prev="GENESIS"
        for n,r in enumerate(rows,1):
            seq,eid,ts,kind,payload,oldprev,h=r
            if seq!=n or oldprev!=prev or self.digest(seq,eid,ts,kind,payload,oldprev)!=h:
                return {"ok":False,"failed_seq":seq}
            prev=h
        return {"ok":True,"events":len(rows),"head_hash":prev}
    def close(self): self.db.close()

class EthicalGyroscope:
    def assess(self,a):
        harm=unit(a.get("harm_risk",.4)); benefit=unit(a.get("benefit",.5))
        consent=unit(a.get("consent",.5)); rev=unit(a.get("reversibility",.5)); unc=unit(a.get("uncertainty",.5))
        score=.28*benefit+.24*consent+.22*rev+.16*(1-harm)+.10*(1-unc)
        flags=[]
        if harm>=.7: flags.append("high_harm_risk")
        if consent<.4: flags.append("consent_unclear_or_low")
        if rev<.3: flags.append("hard_to_reverse")
        if unc>=.7: flags.append("high_uncertainty")
        status="pause_and_review" if flags else ("provisional_candidate" if score>=.6 else "seek_alternative")
        return {"life_support_score":round(score,4),"status":status,"flags":flags,
                "components":{"benefit":benefit,"consent":consent,"reversibility":rev,"harm_risk":harm,"uncertainty":unc}}

class LivingSpiral:
    def __init__(self, ledger_path="data/spiral_ledger.sqlite3", paradigm_path="data/paradigms/paradigm_lenses_v1.json"):
        self.ledger=AppendOnlyLedger(ledger_path); p=Path(paradigm_path)
        self.paradigms=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"lenses":[]}
        self.gyroscope=EthicalGyroscope(); self.version=ENGINE_VERSION
        self.state={"cycles":0,"experiences":0,"reflections":0,"candidate_paradigms":0,"mean_confidence":0.0,"continuity_score":1.0}
        self._confidence=[]
    def process(self, exp: Experience):
        self.state["cycles"]+=1; self.state["experiences"]+=1
        ethical=self.gyroscope.assess(exp.context.get("proposed_action",{}))
        conf=unit(.75-.45*unit(exp.uncertainty)-.35*unit(exp.observed_harm)+.15*unit(exp.observed_benefit))
        reflection={"summary":f"Опыт: {exp.text[:500]}. Этический статус: {ethical['status']}.",
          "counterargument":"Проверить завышение пользы, недооценку вреда и исключённые стороны.",
          "confidence_proxy":round(conf,4),
          "revise_if":"Появятся проверяемые данные, меняющие оценку вреда, пользы, согласия или обратимости.",
          "values_in_tension":["польза","непричинение вреда","согласие","неопределённость"]}
        self._confidence.append(conf); self.state["reflections"]+=1
        self.state["mean_confidence"]=round(sum(self._confidence)/len(self._confidence),4)
        event=self.ledger.append("experience_reflection",{"engine_version":self.version,"experience":asdict(exp),"ethical":ethical,"reflection":reflection})
        candidate=None
        if self.state["cycles"]%5==0 or unit(exp.uncertainty)>=.8:
            candidate={"id":f"PAR-{self.state['cycles']:06d}","parent_version":self.version,
             "hypothesis":"Проверить, улучшает ли дополнительная критика качество решений в этом классе сценариев.",
             "expected_benefit":round(unit(exp.observed_benefit+.2),3),"risk":round(unit(exp.observed_harm+.1),3),
             "evidence_needed":["контрольная группа","независимая оценка","регрессионные тесты","проверка побочного вреда"],
             "status":"pending_review"}
            self.state["candidate_paradigms"]+=1; self.ledger.append("candidate_paradigm_proposed",candidate)
        self.state["continuity_score"]=1.0 if self.ledger.verify()["ok"] else 0.0
        return {"event":event,"ethical_assessment":ethical,"reflection":reflection,"candidate_paradigm":candidate,"state":dict(self.state)}
    def report(self):
        r={"engine_version":self.version,"schema_version":SCHEMA_VERSION,"created_at":datetime.now(timezone.utc).isoformat(),
           "state":dict(self.state),"ledger_integrity":self.ledger.verify(),"paradigm_lenses":len(self.paradigms.get("lenses",[])),
           "interpretation":"Эвристическая исследовательская модель; не измеряет душу или субъективное сознание."}
        self.ledger.append("periodic_report",r); return r
    def close(self): self.ledger.close()

def run_simulation(cycles=20, interval_seconds=0, ledger_path="data/spiral_ledger.sqlite3"):
    spiral=LivingSpiral(ledger_path=ledger_path)
    cases=[
      Experience("Обсуждается решение с возможным вредом.",{"proposed_action":{"harm_risk":.7,"benefit":.6,"consent":.4,"reversibility":.5,"uncertainty":.6}},.4,.5,.6),
      Experience("Новые данные требуют пересмотра прежнего мнения.",{"proposed_action":{"harm_risk":.2,"benefit":.7,"consent":.9,"reversibility":.8,"uncertainty":.3}},.7,.1,.3),
      Experience("Недостаточно данных о последствиях для уязвимой группы.",{"proposed_action":{"harm_risk":.6,"benefit":.5,"consent":.4,"reversibility":.7,"uncertainty":.85}},.3,.4,.85)]
    try:
        for i in range(max(1,cycles)):
            spiral.process(cases[i%len(cases)])
            if interval_seconds>0: time.sleep(interval_seconds)
        return spiral.report()
    finally: spiral.close()
