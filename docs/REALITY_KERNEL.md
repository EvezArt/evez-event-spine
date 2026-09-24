# EVEZ Reality Kernel

The Reality Kernel is the policy boundary between an assertion and a side effect.

Core invariant:

    CLAIM != EVIDENCE != AUTHORITY != INTENT != EFFECT

## Runtime

`reality_kernel.py` is the pure decision engine.

`gateway.py` binds decisions to the append-only File Event Spine. Every attempt
produces a `KERNEL_DECISION` event. Allowed effects produce `EFFECT_COMPLETED`;
exceptions produce `EFFECT_FAILED`.

## Authority

- `OBSERVE`: observation/read scope.
- `SIMULATE`: sandbox execution.
- `MUTATE_REVERSIBLE`: reversible external mutation.
- `MUTATE_IRREVERSIBLE`: irreversible mutation, requiring explicit human approval
  and witness references.
- `HUMAN`: reserved for policies that delegate authority to a human principal.

Authority is not evidence. Evidence is not authority.

## Claim classes

`OBSERVATION`, `VERIFIED_FACT`, `SUPPORTED_INFERENCE`, `HYPOTHESIS`,
`FICTION`, and `UNKNOWN` are labels for evidence handling. They do not prove
the underlying proposition.

## Drift

Drift is a runtime signal based on missing provenance, uncertainty,
non-reproducibility, fiction markers, and contradictions. It is not a diagnosis of
a person or agent.

## CLI

After installation:

    printf '%s' '{"actor":"SCOUT","target":"sandbox","intent":"inspect","requested_effect":"read","authority":"SIMULATE","simulation":true}' | evez-reality-gate

The output is deterministic JSON containing the decision, reasons, drift score, and
Proof Envelope SHA-256.

## Cross-language contract

Use `schema/proof-envelope.schema.json` to validate envelopes before handing them
to a Python service.

## Non-goals

The kernel does not determine consciousness, intent, motive, moral worth, or ultimate
truth. It determines whether a requested effect satisfies procedural policy.

## Failure invariant

Blocked and witness-required attempts remain auditable. Rejection never erases the
attempt.
