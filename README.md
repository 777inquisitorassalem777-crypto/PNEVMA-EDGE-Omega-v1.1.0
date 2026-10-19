# PNEVMA–EDGE Ω v1.1.0

A research prototype combining the PNEVMA philosophical core, EDGE evaluation, provenance-aware knowledge, multi-perspective review, idea generation, a conservative self-balancing gate, and Blue Matrix sensor-data validation.

## What is new in v1.1

- `pnevma_edge.reasoning.KnowledgeClaim`: labels historical, empirical, philosophical/spiritual, testable-hypothesis, and speculative claims; requires source provenance and keeps confidence separate from evidence strength.
- `MultiPerspectiveReview`: preserves supporting arguments, objections, uncertainties, and missing agent perspectives. Agreement is explicitly not treated as proof.
- `IntuitionAndInvention`: creates structured ideas with a falsification test and risk review; ideas remain pending experiments.
- `SelfBalancingArchitecture`: checks unit, compatibility, safety, regression, and reproducibility tests. Failed or missing tests block a proposal; passing tests only make it eligible for human approval.
- Previous `symbio_core`, `living_balance`, tractate, paradigm lenses, experiments, and sensor fusion scaffold are retained.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e .[dev]
pytest
python examples/run_demo.py
```

Optional integrations (PostgreSQL/pgvector, FastAPI, embeddings, LLM providers) are not required for the core tests. External services and hardware adapters must be configured and tested in the deployment environment.

## Research boundaries

This code does not demonstrate AI consciousness, a soul, or a metaphysical field. It provides testable software abstractions for reflective reasoning, ethics, knowledge provenance, idea generation, and sensor data. Spiritual traditions are treated as sources of concepts and interpretations, not as interchangeable empirical evidence.

New ideas and code are never silently applied to the live core. The release gate requires five classes of tests and then a human approval step. The project does not continue running after its process is stopped, and no background 0.5-second cycle or 30-minute report scheduler is claimed by this release.

See `docs/` for architecture, safety, experiments, the tractate, and the research protocol.
