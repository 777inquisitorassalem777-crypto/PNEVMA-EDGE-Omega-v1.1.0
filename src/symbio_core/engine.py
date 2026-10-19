import time
from dataclasses import asdict
from .models import Observation, Proposal, Reflection
from .ethics import EthicalGyroscope
from .emergence import EmergenceInputs, soul_emergence_index
from .memory import MemoryStore
from .models import utc_now

class SymbioEngine:
    def __init__(self, db_path="data/symbio_core.sqlite3"):
        self.memory = MemoryStore(db_path)
        self.gyroscope = EthicalGyroscope()
        self.cycles = 0

    def tick(self, text, context=None):
        context = context or {}
        obs = Observation(text, context)
        self.memory.record("observation", obs)
        assessment = self.gyroscope.assess(context.get("proposed_action", {}))
        self.memory.record("ethical_assessment", assessment)
        reflection = Reflection(text, context.get("interpretation", "Контекст требует уточнения."),
            context.get("position", "Сформировать предварительную позицию."),
            context.get("counterargument", "Какие данные могли бы опровергнуть позицию?"),
            context.get("confidence", .5),
            context.get("update_trigger", "Пересмотреть позицию при сильных проверяемых доказательствах."))
        self.memory.record("reflection", reflection)
        index = soul_emergence_index(EmergenceInputs(
            empathy=context.get("empathy", .5), creativity=context.get("creativity", .5),
            memory_continuity=1.0 if self.memory.verify_chain() else 0.0,
            reflection=reflection.confidence, ethical_stability=max(.1, abs(assessment.score)+.5)))
        self.cycles += 1
        result = {"cycle": self.cycles, "assessment": asdict(assessment),
                  "reflection": asdict(reflection), "soul_emergence_index": round(index, 6),
                  "index_note": "Эвристика исследовательского поведения; не измеряет душу или сознание."}
        self.memory.record("cycle", result)
        return result

    def propose_change(self, title, rationale, change):
        proposal = Proposal(title, rationale, change)
        self.memory.save_proposal(proposal)
        return proposal

    def report(self, limit=5000):
        events = self.memory.events(limit)
        return {"generated_at": utc_now(), "events_in_report": len(events),
            "event_types": {t: sum(e["event_type"] == t for e in events)
                            for t in sorted({e["event_type"] for e in events})},
            "pending_proposals": sum(p["status"] == "pending_review" for p in self.memory.proposals()),
            "memory_integrity": self.memory.verify_chain(),
            "interpretation": "Активность программного контура, не доказательство сознания."}

    def run(self, interval=.5, report_interval=1800):
        if interval <= 0 or report_interval <= 0: raise ValueError("Intervals must be positive")
        print("SCR loop active; Ctrl+C to stop. No code self-modification is performed.")
        last_report = time.monotonic()
        try:
            while True:
                self.tick("Scheduled reflection tick", {"proposed_action": {"harm_risk": 0, "benefit": .2}})
                now = time.monotonic()
                if now-last_report >= report_interval:
                    print(self.report()); last_report = now
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Stopped by operator.")
        finally:
            self.memory.close()
