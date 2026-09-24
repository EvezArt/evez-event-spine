import json
from evez_event_spine import reality_cli


def test_cli_reads_stdin_and_returns_json(monkeypatch, capsys):
    payload = {
        "actor": "SCOUT",
        "target": "sandbox",
        "intent": "inspect",
        "requested_effect": "read",
        "authority": "SIMULATE",
        "simulation": True,
        "claim": {
            "text": "scenario",
            "classification": "HYPOTHESIS",
            "reproducible": True
        }
    }
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(json.dumps(payload)))
    assert reality_cli.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert result["decision"] == "ALLOW"
    assert result["allowed"] is True
