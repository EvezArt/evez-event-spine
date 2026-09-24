from evez_event_spine.reality_kernel import (
    Authority,
    Claim,
    ClaimClass,
    Decision,
    ProofEnvelope,
    RealityKernel,
    declared_effective_match,
)


def test_claim_without_provenance_becomes_unknown():
    kernel = RealityKernel()
    claim = Claim("the swarm coordinated independently", ClaimClass.VERIFIED_FACT)
    assert kernel.classify_claim(claim) == ClaimClass.UNKNOWN


def test_simulation_can_run_with_simulation_authority():
    kernel = RealityKernel()
    claim = Claim("scenario", ClaimClass.HYPOTHESIS, reproducible=True)
    envelope = ProofEnvelope("SCOUT", "sandbox", "test", "simulate", Authority.SIMULATE)
    assert kernel.gate(envelope, claim).decision == Decision.ALLOW


def test_external_action_requires_authority_and_evidence():
    result = RealityKernel().gate(
        ProofEnvelope("AGENT", "external", "mutate", "write", Authority.OBSERVE,
                      simulation=False, reversible=True)
    )
    assert result.decision == Decision.BLOCK
    assert result.reasons


def test_reversible_external_action_with_evidence_is_allowed():
    env = ProofEnvelope(
        "AGENT", "external", "write", "write", Authority.MUTATE_REVERSIBLE,
        evidence_refs=("evt-1",), simulation=False, reversible=True
    )
    assert RealityKernel().gate(env).decision == Decision.ALLOW


def test_irreversible_action_requests_witness_before_execution():
    env = ProofEnvelope(
        "AGENT", "external", "delete", "delete", Authority.MUTATE_IRREVERSIBLE,
        evidence_refs=("evt-1",), simulation=False, reversible=False
    )
    result = RealityKernel().gate(env)
    assert result.decision == Decision.WITNESS_REQUIRED
    assert "human approval" in " ".join(result.reasons)
    assert "witness_refs" in " ".join(result.reasons)


def test_irreversible_action_requires_both_approval_and_witness():
    env = ProofEnvelope(
        "AGENT", "external", "delete", "delete", Authority.MUTATE_IRREVERSIBLE,
        evidence_refs=("evt-1",), witness_refs=("wit-1",), simulation=False,
        reversible=False, human_approval=True
    )
    assert RealityKernel().gate(env).decision == Decision.ALLOW


def test_uncertain_claim_cannot_authorize_external_action():
    claim = Claim("maybe true", ClaimClass.HYPOTHESIS, source_refs=("src-1",))
    env = ProofEnvelope(
        "AGENT", "external", "write", "write", Authority.MUTATE_REVERSIBLE,
        evidence_refs=("src-1",), simulation=False, reversible=True
    )
    assert RealityKernel().gate(env, claim).decision == Decision.BLOCK


def test_declared_and_effective_are_distinct():
    declared = {"authority": "OBSERVE", "requested_effect": "read", "target": "x"}
    effective = {"authority": "MUTATE_REVERSIBLE", "requested_effect": "read", "target": "x"}
    assert not declared_effective_match(declared, effective)


def test_envelope_hash_is_deterministic():
    env = ProofEnvelope("A", "B", "inspect", "read", Authority.SIMULATE)
    assert len(env.envelope_hash) == 64
    assert env.envelope_hash == ProofEnvelope(
        "A", "B", "inspect", "read", Authority.SIMULATE
    ).envelope_hash
