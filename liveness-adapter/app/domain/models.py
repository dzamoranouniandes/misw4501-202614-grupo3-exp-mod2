from dataclasses import dataclass
from enum import StrEnum


class LivenessStatus(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class VerificationCommand:
    customer_id: str
    evidence_ref: str
    correlation_id: str


@dataclass(frozen=True)
class VerificationResult:
    verification_id: str
    status: LivenessStatus
    correlation_id: str

