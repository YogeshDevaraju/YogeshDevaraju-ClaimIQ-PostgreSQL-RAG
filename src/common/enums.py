from enum import Enum


class UserRole(str, Enum):
    admin = "ADMIN"
    claims_manager = "CLAIMS_MANAGER"
    claims_adjuster = "CLAIMS_ADJUSTER"
    support_agent = "SUPPORT_AGENT"


class PolicyType(str, Enum):
    motor = "MOTOR"
    health = "HEALTH"
    property = "PROPERTY"


class PolicyStatus(str, Enum):
    active = "ACTIVE"
    inactive = "INACTIVE"
    expired = "EXPIRED"


class ClaimStatus(str, Enum):
    submitted = "SUBMITTED"
    under_review = "UNDER_REVIEW"
    approved = "APPROVED"
    rejected = "REJECTED"
    closed = "CLOSED"


class DocumentStatus(str, Enum):
    active = "ACTIVE"
    inactive = "INACTIVE"