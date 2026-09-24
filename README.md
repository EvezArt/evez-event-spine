# ⥋ EVEZ Event Spine

**Append-only, hash-linked, verifiable event log.**

1. History IS state. No edits. No deletes.
2. SHA-256 hash chain.
3. Verifiable integrity.
4. Projectable by domain.

## Installation
```bash
pip install evez-event-spine
```

## License
MIT


## Reality Kernel (1.1.0)

The package now includes a deterministic policy boundary between claims and effects.

`CLAIM != EVIDENCE != AUTHORITY != INTENT != EFFECT`

The Reality Kernel:
- classifies claims without treating classification as proof
- carries deterministic SHA-256 Proof Envelopes
- gates simulation, reversible mutation, and irreversible mutation separately
- requires evidence references for consequential external effects
- requires explicit human approval and witness references for irreversible effects
- preserves denied and witness-required attempts through the Guarded Executor

Phone-friendly JSON evaluation is available through `evez-reality-gate`.

Example:

```bash
printf '%s' '{"actor":"SCOUT","target":"sandbox","intent":"inspect","requested_effect":"read","authority":"SIMULATE","simulation":true}' | evez-reality-gate
```

The kernel does not determine consciousness, motive, or ultimate truth. It enforces
procedural boundaries and leaves the evidence trail intact.
