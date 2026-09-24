"""Execution gateway that binds Reality Kernel decisions to Event Spine receipts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .file_spine import FileEventSpine
from .reality_kernel import Claim, Decision, ProofEnvelope, RealityKernel


@dataclass(frozen=True)
class ExecutionReceipt:
    decision: str
    envelope_hash: str
    drift_score: float
    reasons: tuple[str, ...]
    audit_seq: int


class GuardedExecutor:
    """Record every attempt and execute only when the kernel returns ALLOW."""

    def __init__(self, spine: FileEventSpine, kernel: RealityKernel | None = None) -> None:
        self.spine = spine
        self.kernel = kernel or RealityKernel()

    def attempt(
        self,
        envelope: ProofEnvelope,
        claim: Claim | None = None,
        effect: Callable[[], Any] | None = None,
    ) -> ExecutionReceipt:
        result = self.kernel.gate(envelope, claim)

        audit = self.spine.append(
            actor=envelope.actor,
            event_type="KERNEL_DECISION",
            data={
                "decision": result.decision.value,
                "reasons": list(result.reasons),
                "drift_score": result.drift_score,
                "envelope_hash": result.envelope_hash,
                "target": envelope.target,
                "requested_effect": envelope.requested_effect,
                "simulation": envelope.simulation,
            },
        )

        if result.decision != Decision.ALLOW:
            return ExecutionReceipt(
                decision=result.decision.value,
                envelope_hash=result.envelope_hash,
                drift_score=result.drift_score,
                reasons=result.reasons,
                audit_seq=audit["seq"],
            )

        value = effect() if effect is not None else None
        completed = self.spine.append(
            actor=envelope.actor,
            event_type="EFFECT_COMPLETED",
            data={
                "envelope_hash": result.envelope_hash,
                "target": envelope.target,
                "requested_effect": envelope.requested_effect,
                "result": value,
            },
        )

        return ExecutionReceipt(
            decision=Decision.ALLOW.value,
            envelope_hash=result.envelope_hash,
            drift_score=result.drift_score,
            reasons=(),
            audit_seq=completed["seq"],
        )
