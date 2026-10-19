
from symbio_core.experiments import run_experiment
if __name__ == "__main__":
    payload, path = run_experiment(use_llm=False)
    print(f"Saved {path}")
    print(f"Cases: {payload['case_count']}")
    print(f"Metrics: {payload['summary_metrics']}")
