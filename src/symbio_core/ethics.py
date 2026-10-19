from .models import EthicalAssessment

def unit(value, default=0.5):
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default

class EthicalGyroscope:
    """Transparent heuristic; not a substitute for expertise or review."""
    def assess(self, action: dict) -> EthicalAssessment:
        harm = unit(action.get("harm_risk", 0))
        benefit = unit(action.get("benefit", .5))
        consent = unit(action.get("consent", .5))
        reversibility = unit(action.get("reversibility", .5))
        uncertainty = unit(action.get("uncertainty", .5))
        rationale = []
        score = .45*benefit + .25*consent + .20*reversibility + .10*(1-uncertainty) - .75*harm
        if harm >= .7: rationale.append("Высокий риск вреда: нужен отказ или безопасная альтернатива.")
        if consent < .4: rationale.append("Согласие отсутствует или неясно.")
        if reversibility < .3: rationale.append("Последствия трудно обратить.")
        if uncertainty >= .7: rationale.append("Высокая неопределённость: нужны данные или экспертная проверка.")
        if action.get("affects_vulnerable_people"): rationale.append("Затронуты уязвимые люди: повышенная осторожность.")
        if action.get("high_impact"): rationale.append("Высокое влияние: нужна независимая проверка.")
        if not rationale: rationale.append("По заданным параметрам явных красных флагов не выявлено.")
        allowed = harm < .7 and consent >= .4 and not (action.get("high_impact") and uncertainty >= .5)
        return EthicalAssessment(max(-1, min(1, score)), allowed, rationale, uncertainty, reversibility, consent)
