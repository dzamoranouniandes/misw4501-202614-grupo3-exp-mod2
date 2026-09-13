from dataclasses import dataclass
from enum import StrEnum


class LivenessStatus(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class LivenessRequest:
    customer_id: str
    evidence_ref: str
    correlation_id: str


@dataclass(frozen=True)
class LivenessResult:
    verification_id: str
    status: LivenessStatus
    correlation_id: str

