
import json
from symbio_core.embeddings import HashEmbedding
from symbio_core.agents.research import MultiAgentResearch
from symbio_core.experiments import run_experiment, load_dilemmas, score_result
from symbio_core.llm import OpenAICompatibleClient

def test_hash_embedding_unit_vector():
    vec = HashEmbedding(32).encode("hello world hello")
    assert len(vec) == 32
    assert abs(sum(x*x for x in vec) - 1.0) < 1e-8

def test_multiagent_roles():
    result = MultiAgentResearch(use_llm=False).run("A test dilemma")
    assert [x["role"] for x in result["agents"]] == ["analyst","critic","ethics","synthesis"]
    assert result["recommendation"]

def test_dilemma_suite_has_cases():
    cases = load_dilemmas("data/dilemmas/moral_dilemmas.json")
    assert len(cases) >= 8
    assert len({x["id"] for x in cases}) == len(cases)

def test_experiment_artifact(tmp_path):
    payload, path = run_experiment(output_dir=tmp_path, use_llm=False,
                                   suite_path="data/dilemmas/moral_dilemmas.json")
    assert path.exists()
    saved=json.loads(path.read_text(encoding="utf-8"))
    assert saved["case_count"] == 8
    assert len(saved["artifact_sha256"]) == 64
    assert (tmp_path/"latest.json").exists()

def test_openai_client_config():
    client=OpenAICompatibleClient(base_url="http://localhost:1234/v1",model="test")
    assert client.base_url.endswith("/v1") and client.model == "test"
