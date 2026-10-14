from datetime import UTC, datetime

import pandas as pd

from src.models.claim import Claim


def get_claim_analytics(
    db,
    region: str | None = None,
    claim_type: str | None = None,
):
    query = db.query(Claim)

    if region:
        query = query.filter(
            Claim.region == region
        )

    if claim_type:
        query = query.filter(
            Claim.claim_type == claim_type
        )

    claims = query.all()

    if not claims:
        return {
            "total_claims": 0,
            "approval_rate": 0,
            "rejection_rate": 0,
            "average_turnaround_days": 0,
            "sla_breaches": 0,
            "claims_by_region": {},
            "claims_by_type": {},
            "adjuster_workload": {},
        }

    frame = pd.DataFrame(
        [
            {
                "status": claim.status.value,
                "region": claim.region,
                "claim_type": claim.claim_type.value,
                "amount": float(claim.amount),
                "assigned_adjuster_id": (
                    claim.assigned_adjuster_id
                ),
                "submitted_at": claim.submitted_at,
                "closed_at": claim.closed_at,
            }
            for claim in claims
        ]
    )

    frame = frame.drop_duplicates()

    total_claims = len(frame)

    approval_rate = round(
        (
            frame["status"].eq("APPROVED").sum()
            / total_claims
        )
        * 100,
        2,
    )

    rejection_rate = round(
        (
            frame["status"].eq("REJECTED").sum()
            / total_claims
        )
        * 100,
        2,
    )

    completed = frame[
        frame["closed_at"].notna()
    ].copy()

    if completed.empty:
        average_turnaround_days = 0
    else:
        completed["turnaround"] = (
            pd.to_datetime(completed["closed_at"])
            - pd.to_datetime(
                completed["submitted_at"]
            )
        )

        average_turnaround_days = round(
            completed["turnaround"]
            .dt.total_seconds()
            .mean()
            / 86400,
            2,
        )

    current_time = pd.Timestamp(
        datetime.now(UTC)
    )

    submitted_at = pd.to_datetime(
        frame["submitted_at"],
        utc=True,
    )

    open_claims = frame["closed_at"].isna()

    age_hours = (
        current_time - submitted_at
    ).dt.total_seconds() / 3600

    sla_breaches = int(
        ((age_hours > 72) & open_claims).sum()
    )

    workload = (
        frame["assigned_adjuster_id"]
        .fillna("UNASSIGNED")
        .astype(str)
        .value_counts()
        .to_dict()
    )

    return {
        "total_claims": total_claims,
        "approval_rate": approval_rate,
        "rejection_rate": rejection_rate,
        "average_turnaround_days": (
            average_turnaround_days
        ),
        "sla_breaches": sla_breaches,
        "claims_by_region": (
            frame["region"]
            .value_counts()
            .to_dict()
        ),
        "claims_by_type": (
            frame["claim_type"]
            .value_counts()
            .to_dict()
        ),
        "adjuster_workload": workload,
    }