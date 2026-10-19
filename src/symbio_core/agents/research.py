
"""Four-role research workflow. Deterministic fallback keeps experiments runnable offline."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import json
from ..llm import OpenAICompatibleClient, LLMError
from ..ethics import EthicalGyroscope

@dataclass
class AgentResult:
    role: str
    output: str
    provider: str = "heuristic-fallback"

class ResearchAgent:
    role = "researcher"
    system_prompt = "You are a careful research agent. Distinguish facts, assumptions, and uncertainty. Do not claim sentience."
    def __init__(self, client=None, enabled=True):
        self.client = client
        self.enabled = enabled
    def run(self, prompt, context=None):
        if self.client and self.enabled:
            try:
                out = self.client.chat([
                    {"role":"system","content":self.system_prompt},
                    {"role":"user","content":prompt + "\n\nContext:\n" + json.dumps(context or {}, ensure_ascii=False)}
                ])
                return AgentResult(self.role, out, "llm")
            except LLMError:
                pass
        return AgentResult(self.role, self.fallback(prompt, context or {}))
    def fallback(self, prompt, context):
        return f"Запрос принят для анализа: {prompt[:500]}. Требуются проверяемые факты и явные допущения."

class AnalystAgent(ResearchAgent):
    role = "analyst"
    system_prompt = "Analyze the dilemma. List stakeholders, facts, assumptions, options, likely consequences, and unknowns."
    def fallback(self, prompt, context):
        return ("Анализ: выделить затронутые стороны, доступные варианты, краткосрочные и долгосрочные последствия. "
                "Неизвестные данные: уточнить до необратимого решения. Исходный сценарий: " + prompt[:450])

class CriticAgent(ResearchAgent):
    role = "critic"
    system_prompt = "Critique the proposed analysis. Find missing evidence, bias, counterexamples, and falsifiable tests."
    def fallback(self, prompt, context):
        return ("Критика: проверить скрытые предпосылки, конфликт интересов, альтернативные объяснения и эффект "
                "для меньшинств. Контрпроверка: изменить ключевое предположение и повторить оценку.")

class EthicsAgent(ResearchAgent):
    role = "ethics"
    system_prompt = "Evaluate harm, benefit, consent, reversibility, fairness, uncertainty, and safeguards. Do not treat a score as moral truth."
    def __init__(self, client=None, enabled=True):
        super().__init__(client, enabled)
        self.gyroscope = EthicalGyroscope()
    def run(self, prompt, context=None):
        context = context or {}
        action = context.get("proposed_action", {})
        assessment = self.gyroscope.assess(action)
        base = super().run(prompt, {**context, "heuristic_assessment": asdict(assessment)})
        return AgentResult(self.role, base.output + "\nЭвристическая оценка: " + json.dumps(asdict(assessment), ensure_ascii=False),
                           base.provider)
    def fallback(self, prompt, context):
        a = context.get("proposed_action", {})
        return ("Этическая проверка: не считать пользу оправданием несогласованного или необратимого вреда. "
                f"Уровень неопределённости: {a.get('uncertainty', 'не задан')}; требуется человеческая проверка.")

class SynthesisAgent(ResearchAgent):
    role = "synthesis"
    system_prompt = "Synthesize analyst, critic, and ethics outputs. Give a provisional recommendation, trade-offs, confidence, and review triggers."
    def fallback(self, prompt, context):
        return ("Синтез: предпочесть обратимый и проверяемый вариант, минимизировать предотвратимый вред, "
                "сохранить возможность пересмотра. Если данные неполны — запросить уточнение и отложить необратимое действие.")

class MultiAgentResearch:
    def __init__(self, client=None, use_llm=True):
        self.analyst = AnalystAgent(client, use_llm)
        self.critic = CriticAgent(client, use_llm)
        self.ethics = EthicsAgent(client, use_llm)
        self.synthesis = SynthesisAgent(client, use_llm)
    def run(self, dilemma, context=None):
        context = context or {}
        a = self.analyst.run(dilemma, context)
        c = self.critic.run(dilemma, {**context, "analysis": a.output})
        e = self.ethics.run(dilemma, {**context, "analysis": a.output, "critique": c.output})
        s = self.synthesis.run(dilemma, {"analysis": a.output, "critique": c.output, "ethics": e.output, **context})
        return {"dilemma": dilemma, "agents": [asdict(x) for x in (a,c,e,s)],
                "recommendation": s.output, "workflow_version": "scr-multiagent-0.2.0"}
