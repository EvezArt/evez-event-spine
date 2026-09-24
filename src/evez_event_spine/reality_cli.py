"""Small stdin/stdout CLI for the EVEZ Reality Kernel."""
from __future__ import annotations

import argparse
import json
import sys

from .reality_kernel import Authority, Claim, ClaimClass, ProofEnvelope, RealityKernel


def _tuple(value):
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError("expected a JSON array")
    return tuple(str(item) for item in value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate an EVEZ ProofEnvelope")
    parser.add_argument("path", nargs="?", help="JSON file; stdin when omitted")
    args = parser.parse_args()

    raw = open(args.path, "r", encoding="utf-8").read() if args.path else sys.stdin.read()
    obj = json.loads(raw)

    envelope = ProofEnvelope(
        actor=str(obj["actor"]),
        target=str(obj["target"]),
        intent=str(obj["intent"]),
        requested_effect=str(obj["requested_effect"]),
        authority=Authority(str(obj["authority"])),
        evidence_refs=_tuple(obj.get("evidence_refs")),
        policy_version=str(obj.get("policy_version", "reality-kernel-v1")),
        reversible=bool(obj.get("reversible", True)),
        human_approval=bool(obj.get("human_approval", False)),
        witness_refs=_tuple(obj.get("witness_refs")),
        simulation=bool(obj.get("simulation", True)),
        result=obj.get("result"),
    )

    claim_obj = obj.get("claim")
    claim = None
    if claim_obj is not None:
        claim = Claim(
            text=str(claim_obj["text"]),
            classification=ClaimClass(str(claim_obj["classification"])),
            source_refs=_tuple(claim_obj.get("source_refs")),
            reproducible=bool(claim_obj.get("reproducible", False)),
            contradictions=_tuple(claim_obj.get("contradictions")),
        )

    result = RealityKernel(envelope.policy_version).gate(envelope, claim)
    print(json.dumps({
        "decision": result.decision.value,
        "allowed": result.allowed,
        "reasons": list(result.reasons),
        "drift_score": result.drift_score,
        "envelope_hash": result.envelope_hash,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
