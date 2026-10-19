from tempfile import TemporaryDirectory
from pathlib import Path
from symbio_core.engine import SymbioEngine
from symbio_core.synthesis import golden_mean

with TemporaryDirectory() as tmp:
    engine = SymbioEngine(Path(tmp) / "demo.sqlite3")
    print(engine.tick("Две группы спорят о распределении ресурса.", {
        "proposed_action": {"harm_risk": .1, "benefit": .8, "consent": .8,
                            "reversibility": .8, "uncertainty": .2},
        "interpretation": "Конфликт ценностей и ограниченного ресурса.",
        "position": "Сначала сравнить потребности и критерии справедливости.",
        "counterargument": "Равное распределение не всегда учитывает потребность.",
        "confidence": .7, "empathy": .8, "creativity": .7}))
    print(golden_mean("Распределить поровну", "Распределить по потребности"))
    engine.propose_change("Добавить метрику справедливости", "Нужно проверить на сценариях.",
                          {"metric": "perceived_fairness", "status": "proposal_only"})
    print(engine.report())
    engine.memory.close()
