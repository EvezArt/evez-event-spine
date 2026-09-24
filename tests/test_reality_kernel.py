from evez_event_spine.reality_kernel import *

def test_claim_without_provenance_becomes_unknown():
    k = RealityKernel()
    claim = Claim("x", ClaimClass.VERIFIED_FACT)
    assert k.classify_claim(claim) == ClaimClass.UNKNOWN

def test_simulation_can_run():
    k = RealityKernel()
    claim = Claim("scenario", ClaimClass.HYPOTHESIS)
    env = ProofEnvelope("SCOUT", "sandbox", "test", "simulate", Authority.SIMULATE, simulation=True)
    assert k.gate(env, claim).decision == Decision.ALLOW

def test_external_action_requires_authority_and_evidence():
    env = ProofEnvelope("AGENT", "external", "mutate", "write", Authority.OBSERVE, simulation=False)
    assert k.gate(env).decision == Decision.BLOCK if False else RealityKernel().gate(env).decision == Decision.BLOCK

def test_irreversible_requires_human_gate():
    env = ProofEnvelope("AGENT", "external", "delete", "delete", Authority.MUTATE_IRREVERSIBLE,
                        evidence_refs=("evt-1",), simulation=False, reversible=False, human_gate=False)
    assert RealityKernel().gate(env).decision == Decision.BLOCK

def test_irreversible_with_human_gate_requires_witness():
    env = ProofEnvelope("AGENT", "external", "delete", "delete", Authority.MUTATE_IRREVERSIBLE,
                        evidence_refs=("evt-1",), simulation=False, reversible=False, human_gate=True)
    assert RealityKernel().gate(env).decision == Decision.WITNESS_REQUIRED

def test_declared_effective_are_distinct():
    a = {"authority":"OBSERVE","requested_effect":"read","target":"x"}
    b = {"authority":"MUTATE_REVERSIBLE","requested_effect":"read","target":"x"}
    assert not declared_effective_match(a,b)
