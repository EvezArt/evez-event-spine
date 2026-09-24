# EVEZ Event Spine Specification v1

The Event Spine is an append-only, hash-chained JSONL record.

## Invariants

1. Events are appended; existing lines are never edited or deleted.
2. Event sequence numbers start at 0 and increase by exactly one.
3. The genesis event has a prev_hash of 64 zero characters.
4. Every later event references the immediately preceding event hash.
5. The hash is computed from canonical JSON bytes with the hash field omitted.
6. Verification must be deterministic from the file alone.
7. A verification failure does not repair or rewrite the history.
8. Unknown external effects remain unknown.

## Canonical event

An event contains version, seq, timestamp, actor, event_type, data, prev_hash, and hash.
Canonical bytes are UTF-8 JSON encoded with sorted object keys and separators comma/colon, then hashed with SHA-256.

## Verification result

A verifier returns valid, events_checked, errors, first_error_seq, and last_hash.
It must not infer facts beyond the integrity of the chain.

## Relationship to claims

An Event Spine records events. It does not prove the truth of arbitrary claims stored inside an event.

claim -> evidence -> test -> result -> spine

The spine proves provenance and ordering, not the truth of the world described by a payload.