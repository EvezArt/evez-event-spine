from evez_event_spine.file_spine import FileEventSpine
from evez_event_spine.gateway import GuardedExecutor
from evez_event_spine.reality_kernel import Authority, Claim, ClaimClass, Decision, ProofEnvelope


def test_blocked_action_is_logged_and_not_executed(tmp_path):
    spine = FileEventSpine(tmp_path / "spine.jsonl")
    executor = GuardedExecutor(spine)
    called = []
    env = ProofEnvelope("AGENT", "outside", "write", "write", Authority.OBSERVE,
                         simulation=False, reversible=True)
    receipt = executor.attempt(env, effect=lambda: called.append(True))
    assert receipt.decision == Decision.BLOCK.value
    assert receipt.execution_status == "NOT_EXECUTED"
    assert called == []
    assert spine.verify()["valid"]
    assert [event["event_type"] for event in spine.replay()] == ["KERNEL_DECISION"]


def test_witness_required_is_logged_and_not_executed(tmp_path):
    spine = FileEventSpine(tmp_path / "spine.jsonl")
    executor = GuardedExecutor(spine)
    called = []
    env = ProofEnvelope("AGENT", "outside", "delete", "delete",
                        Authority.MUTATE_IRREVERSIBLE, evidence_refs=("evt-1",),
                        simulation=False, reversible=False)
    receipt = executor.attempt(env, effect=lambda: called.append(True))
    assert receipt.decision == Decision.WITNESS_REQUIRED.value
    assert receipt.execution_status == "NOT_EXECUTED"
    assert called == []


def test_allowed_action_logs_completion(tmp_path):
    spine = FileEventSpine(tmp_path / "spine.jsonl")
    executor = GuardedExecutor(spine)
    called = []
    env = ProofEnvelope("AGENT", "sandbox", "run", "simulate", Authority.SIMULATE)
    receipt = executor.attempt(env, effect=lambda: called.append("ran"))
    assert receipt.decision == Decision.ALLOW.value
    assert receipt.execution_status == "COMPLETED"
    assert called == ["ran"]
    assert spine.verify()["valid"]
    assert [event["event_type"] for event in spine.replay()] == [
        "KERNEL_DECISION", "EFFECT_COMPLETED"
    ]


def test_failed_effect_is_audited(tmp_path):
    spine = FileEventSpine(tmp_path / "spine.jsonl")
    executor = GuardedExecutor(spine)
    def explode():
        raise RuntimeError("boom")
    env = ProofEnvelope("AGENT", "sandbox", "run", "simulate", Authority.SIMULATE)
    receipt = executor.attempt(env, effect=explode)
    assert receipt.decision == Decision.ALLOW.value
    assert receipt.execution_status == "FAILED"
    assert [event["event_type"] for event in spine.replay()] == [
        "KERNEL_DECISION", "EFFECT_FAILED"
    ]
    assert spine.verify()["valid"]


def test_uncertain_external_claim_is_blocked(tmp_path):
    spine = FileEventSpine(tmp_path / "spine.jsonl")
    executor = GuardedExecutor(spine)
    claim = Claim("maybe", ClaimClass.HYPOTHESIS, source_refs=("src-1",))
    env = ProofEnvelope("AGENT", "external", "write", "write",
                        Authority.MUTATE_REVERSIBLE, evidence_refs=("src-1",),
                        simulation=False, reversible=True)
    receipt = executor.attempt(env, claim, effect=lambda: 99)
    assert receipt.decision == Decision.BLOCK.value
