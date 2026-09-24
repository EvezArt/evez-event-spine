# EVEZ Reality Kernel

The Reality Kernel is the policy boundary between an assertion and a side effect.

Core invariant:

    CLAIM != EVIDENCE != AUTHORITY != INTENT != EFFECT

The repository contains two layers:

1. `reality_kernel.py` is a pure deterministic policy engine.
2. `gateway.py` binds kernel decisions to the append-only File Event Spine.

Every attempted consequential action is logged as a `KERNEL_DECISION`. An allowed
action is followed by an `EFFECT_COMPLETED` receipt. A blocked action gets no
effect call.

## Authority

- `OBSERVE`: observation/read scope.
- `SIMULATE`: sandbox execution.
- `MUTATE_REVERSIBLE`: reversible external mutation.
- `MUTATE_IRREVERSIBLE`: irreversible mutation, additionally requiring explicit
  human approval and witness references.
- `HUMAN`: reserved for policies that explicitly delegate authority to a human
  principal.

Authority is not evidence and evidence is not authority.

## Evidence

Evidence references are identifiers, not proof by themselves. The kernel requires
them for consequential external effects but does not independently validate their
truth. A higher layer must resolve each reference and preserve its provenance.

## Drift

Drift is a runtime signal derived from missing provenance, uncertain classification,
non-reproducibility, fiction markers, and contradictions. It is not a diagnosis of
a person or agent.

## Non-goals

The kernel does not determine consciousness, intent, motive, moral worth, or ultimate
truth. It controls whether a requested effect satisfies procedural policy.

## Failure invariant

A blocked or witnessed action remains an auditable event. Rejection never erases
the attempted action.
