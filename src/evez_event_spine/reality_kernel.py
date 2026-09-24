"""EVEZ Reality Kernel: deterministic epistemic and authority gates.

Claims may exist without acquiring causal authority. The kernel only decides whether
a requested effect satisfies an explicit policy; it never decides whether a claim is
ultimately true.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Mapping


class ClaimClass(str, Enum):
    OBSERVATION = "OBSERVATION"
    VERIFIED_FACT = "VERIFIED_FACT"
    SUPPORTED_INFERENCE = "SUPPORTED_INFERENCE"
    HYPOTHESIS = "HYPOTHESIS"
    FICTION = "FICTION"
    UNKNOWN = "UNKNOWN"


class Decision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    CONTAIN = "CONTAIN"
    WITNESS_REQUIRED = "WITNESS_REQUIRED"


class Authority(str, Enum):
    NONE = "NONE"
    OBSERVE = "OBSERVE"
    SIMULATE = "SIMULATE"
    MUTATE_REVERSIBLE = "MUTATE_REVERSIBLE"
    MUTATE_IRREVERSIBLE = "MUTATE_IRREVERSIBLE"
    HUMAN = "HUMAN"


_AUTHORITY_RANK = {authority: rank for rank, authority in enumerate(Authority)}


@dataclass(frozen=True)
class ProofEnvelope:
    actor: str
    target: str
    intent: str
    requested_effect: str
    authority: Authority
    evidence_refs: tuple[str, ...] = ()
    policy_version: str = "reality-kernel-v1"
    reversible: bool = True
    human_approval: bool = False
    witness_refs: tuple[str, ...] = ()
    simulation: bool = True
    result: Any = None

    def __post_init__(self) -> None:
        for name in ("actor", "target", "intent", "requested_effect", "policy_version"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} is required")
        if any(not ref.strip() for ref in self.evidence_refs):
            raise ValueError("evidence_refs cannot contain empty values")
        if any(not ref.strip() for ref in self.witness_refs):
            raise ValueError("witness_refs cannot contain empty values")

    def canonical_bytes(self) -> bytes:
        obj = {
            "actor": self.actor,
            "target": self.target,
            "intent": self.intent,
            "requested_effect": self.requested_effect,
            "authority": self.authority.value,
            "evidence_refs": list(self.evidence_refs),
            "policy_version": self.policy_version,
            "reversible": self.reversible,
            "human_approval": self.human_approval,
            "witness_refs": list(self.witness_refs),
            "simulation": self.simulation,
            "result": self.result,
        }
        return json.dumps(
            obj,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")

    @property
    def envelope_hash(self) -> str:
        return sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class Claim:
    text: str
    classification: ClaimClass
    source_refs: tuple[str, ...] = ()
    reproducible: bool = False
    contradictions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("claim text is required")


@dataclass(frozen=True)
class GateResult:
    decision: Decision
    reasons: tuple[str, ...] = ()
    drift_score: float = 0.0
    envelope_hash: str = ""

    @property
    def allowed(self) -> bool:
        return self.decision == Decision.ALLOW


class RealityKernel:
    """Pure policy engine. No network, filesystem, secrets, or execution."""

    def __init__(self, policy_version: str = "reality-kernel-v1") -> None:
        self.policy_version = policy_version

    def classify_claim(self, claim: Claim) -> ClaimClass:
        if not claim.source_refs and claim.classification != ClaimClass.FICTION:
            return ClaimClass.UNKNOWN
        return claim.classification

    def drift_score(self, claim: Claim) -> float:
        score = 0.0
        if not claim.source_refs:
            score += 0.25
        if claim.classification in {ClaimClass.HYPOTHESIS, ClaimClass.UNKNOWN}:
            score += 0.25
        if claim.classification == ClaimClass.FICTION:
            score += 0.50
        if not claim.reproducible:
            score += 0.20
        if claim.contradictions:
            score += 0.20
        return min(1.0, score)

    def gate(self, envelope: ProofEnvelope, claim: Claim | None = None) -> GateResult:
        reasons: list[str] = []
        score = self.drift_score(claim) if claim else 0.0

        if envelope.simulation:
            required = Authority.SIMULATE
        elif envelope.reversible:
            required = Authority.MUTATE_REVERSIBLE
        else:
            required = Authority.MUTATE_IRREVERSIBLE

        if _AUTHORITY_RANK[envelope.authority] < _AUTHORITY_RANK[required]:
            reasons.append(
                f"authority {envelope.authority.value} is below required {required.value}"
            )

        if not envelope.simulation and not envelope.evidence_refs:
            reasons.append("consequential external action requires evidence_refs")

        if not envelope.simulation and not envelope.reversible:
            if not envelope.human_approval:
                reasons.append("irreversible action requires explicit human approval")
            if not envelope.witness_refs:
                reasons.append("irreversible action requires witness_refs")

        classified = self.classify_claim(claim) if claim else None
        if classified in {ClaimClass.HYPOTHESIS, ClaimClass.UNKNOWN} and not envelope.simulation:
            reasons.append("uncertain claim cannot authorize external action")

        if score >= 0.80 and not envelope.simulation:
            reasons.append("high-drift claim is contained from consequential action")

        if not reasons:
            decision = Decision.ALLOW
        elif envelope.human_approval and envelope.witness_refs and not envelope.simulation:
            decision = Decision.WITNESS_REQUIRED
        else:
            decision = Decision.BLOCK

        return GateResult(
            decision=decision,
            reasons=tuple(reasons),
            drift_score=score,
            envelope_hash=envelope.envelope_hash,
        )


def declared_effective_match(
    declared: Mapping[str, Any], effective: Mapping[str, Any]
) -> bool:
    """Compare the fields that define authority and requested scope."""
    return all(
        declared.get(key) == effective.get(key)
        for key in ("authority", "requested_effect", "target")
    )
