
"""FastAPI service and lightweight monitoring dashboard. Optional dependency: fastapi/uvicorn."""
from __future__ import annotations
import os, html, json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from .agents.research import MultiAgentResearch
from .llm import OpenAICompatibleClient
from .experiments import run_experiment
from .engine import SymbioEngine

app=FastAPI(title="Symbio Core Research API", version="0.2.0",
            description="Research scaffold; outputs are provisional and require human review.")
engine=SymbioEngine(os.getenv("SYMBIO_DB_PATH","data/symbio_core.sqlite3"))
client=OpenAICompatibleClient.from_env()
workflow=MultiAgentResearch(client=client, use_llm=os.getenv("SYMBIO_USE_LLM","false").lower()=="true")

class ResearchRequest(BaseModel):
    dilemma: str = Field(min_length=3, max_length=12000)
    context: dict = Field(default_factory=dict)

@app.get("/health")
def health():
    return {"status":"ok","version":"0.2.0","llm_configured":bool(os.getenv("SYMBIO_USE_LLM","false").lower()=="true")}

@app.get("/report")
def report():
    return engine.report()

@app.get("/events")
def events(limit: int=100):
    if not 1 <= limit <= 1000: raise HTTPException(400,"limit must be between 1 and 1000")
    return engine.memory.events(limit)

@app.post("/research")
def research(req: ResearchRequest):
    result=workflow.run(req.dilemma, req.context)
    engine.memory.record("multiagent_research",result)
    return result

@app.post("/experiments/run")
def experiments():
    payload,path=run_experiment(output_dir=os.getenv("SYMBIO_RESULTS_DIR","results"),
                                use_llm=workflow.synthesis.enabled, client=client)
    engine.memory.record("experiment_completed",{"path":str(path),"hash":payload["artifact_sha256"]})
    return {"artifact":str(path),"artifact_sha256":payload["artifact_sha256"],
            "case_count":payload["case_count"],"summary_metrics":payload["summary_metrics"]}

@app.get("/experiments")
def experiments_list():
    folder=Path(os.getenv("SYMBIO_RESULTS_DIR","results"))
    return [{"name":p.name,"bytes":p.stat().st_size} for p in sorted(folder.glob("experiment_*.json"))]

@app.get("/",response_class=HTMLResponse)
def dashboard():
    report_data=engine.report()
    result_files=sorted(Path(os.getenv("SYMBIO_RESULTS_DIR","results")).glob("experiment_*.json"),reverse=True)
    body=f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
    <title>SCR Monitor</title><style>body{{font:16px system-ui;max-width:980px;margin:2rem auto;padding:0 1rem;color:#202124}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:1rem}}section{{border:1px solid #ddd;border-radius:12px;padding:1rem}}
    code{{overflow-wrap:anywhere}}a{{color:#1456a0}}button{{padding:.6rem 1rem}}</style></head><body>
    <h1>Symbio Core Research</h1><p>Мониторинг исследовательского контура — не индикатор сознания.</p>
    <div class="grid"><section><b>Событий в отчёте</b><h2>{report_data['events_in_report']}</h2></section>
    <section><b>Целостность hash-chain</b><h2>{'OK' if report_data['memory_integrity'] else 'CHECK FAILED'}</h2></section>
    <section><b>Ожидают проверки</b><h2>{report_data['pending_proposals']}</h2></section>
    <section><b>Экспериментальных артефактов</b><h2>{len(result_files)}</h2></section></div>
    <h2>API</h2><ul><li><a href="/docs">Интерактивная документация</a></li><li><a href="/health">Health</a></li><li><a href="/report">Отчёт</a></li><li><a href="/experiments">Эксперименты</a></li></ul>
    <h2>Типы событий</h2><pre>{html.escape(json.dumps(report_data['event_types'],ensure_ascii=False,indent=2))}</pre>
    <p>Все рекомендации предварительны; решения с риском вреда проверяет человек.</p></body></html>"""
    return HTMLResponse(body)
