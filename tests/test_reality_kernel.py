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
    envelope = ProofEnvelope(
        actor="SCOUT",
        target="sandbox",
        intent="test",
        requested_effect="simulate",
        authority=Authority.SIMULATE,
        simulation=True,
    )
    assert kernel.gate(envelope, claim).decision == Decision.ALLOW


def test_external_action_requires_authority_and_evidence():
    kernel = RealityKernel()
    envelope = ProofEnvelope(
        actor="AGENT",
        target="external",
        intent="mutate",
        requested_effect="write",
        authority=Authority.OBSERVE,
        simulation=False,
        reversible=True,
    )
    result = kernel.gate(envelope)
    assert result.decision == Decision.BLOCK
    assert result.reasons


def test_reversible_external_action_with_evidence_is_allowed():
    kernel = RealityKernel()
    envelope = ProofEnvelope(
        actor="AGENT",
        target="external",
        intent="write",
        requested_effect="write",
        authority=Authority.MUTATE_REVERSIBLE,
        evidence_refs=("evt-1",),
        simulation=False,
        reversible=True,
    )
    assert kernel.gate(envelope).decision == Decision.ALLOW


def test_irreversible_action_requires_human_approval_and_witness():
    kernel = RealityKernel()
    envelope = ProofEnvelope(
        actor="AGENT",
        target="external",
        intent="delete",
        requested_effect="delete",
        authority=Authority.MUTATE_IRREVERSIBLE,
        evidence_refs=("evt-1",),
        simulation=False,
        reversible=False,
    )
    result = kernel.gate(envelope)
    assert result.decision == Decision.BLOCK
    assert "explicit human approval" in " ".join(result.reasons)
    assert "witness_refs" in " ".join(result.reasons)


def test_irreversible_action_with_human_approval_is_witness_checked():
    kernel = RealityKernel()
    envelope = ProofEnvelope(
        actor="AGENT",
        target="external",
        intent="delete",
        requested_effect="delete",
        authority=Authority.MUTATE_IRREVERSIBLE,
        evidence_refs=("evt-1",),
        witness_refs=("wit-1",),
        simulation=False,
        reversible=False,
        human_approval=True,
    )
    result = kernel.gate(envelope)
    assert result.decision == Decision.ALLOW


def test_uncertain_claim_cannot_authorize_external_action():
    kernel = RealityKernel()
    claim = Claim("maybe true", ClaimClass.HYPOTHESIS, source_refs=("src-1",), reproducible=False)
    envelope = ProofEnvelope(
        actor="AGENT",
        target="external",
        intent="write",
        requested_effect="write",
        authority=Authority.MUTATE_REVERSIBLE,
        evidence_refs=("src-1",),
        simulation=False,
        reversible=True,
    )
    assert kernel.gate(envelope, claim).decision == Decision.BLOCK


def test_declared_and_effective_are_distinct():
    declared = {"authority": "OBSERVE", "requested_effect": "read", "target": "x"}
    effective = {"authority": "MUTATE_REVERSIBLE", "requested_effect": "read", "target": "x"}
    assert not declared_effective_match(declared, effective)


def test_envelope_hash_is_deterministic():
    env = ProofEnvelope("A", "B", "inspect", "read", Authority.SIMULATE)
    assert env.envelope_hash == env.envelope_hash
    assert len(env.envelope_hash) == 64
