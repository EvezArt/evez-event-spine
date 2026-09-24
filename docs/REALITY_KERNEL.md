# EVEZ Reality Kernel

Dependency-free deterministic gate separating claims, evidence, authority and effects.

Core invariant:

CLAIM != EVIDENCE != AUTHORITY != INTENT != EFFECT

Claims may be recorded without receiving causal authority.

ProofEnvelope carries actor, target, intent, requested effect, authority, evidence
references, policy version, reversibility, human gate, simulation flag, result, and a
deterministic SHA-256 hash.

The kernel performs no network calls, executes no external actions, and stores no
secrets. Put it before tool execution, memory mutation, deployment, and other
consequential boundaries.

Laws:
1. Claims cannot directly modify reality.
2. Agents cannot grant themselves authority.
3. Contradictions remain records.
4. Irreversible actions require human authorization.
5. Removing an agent cannot remove its historical evidence.
