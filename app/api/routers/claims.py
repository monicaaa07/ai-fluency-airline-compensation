"""Routers are thin: parse input, call one service method, shape the output."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter

from app.api.deps import ContainerDep, CurrentStaff
from app.domain import ClaimStatus
from app.schemas import ClaimCreate, ClaimList, ClaimOut

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post("", response_model=ClaimOut, status_code=201)
async def file_claim(body: ClaimCreate, container: ContainerDep, staff: CurrentStaff) -> ClaimOut:
    claim = container.claim_service.file_claim(
        incident_id=body.incident_id,
        passenger_name=body.passenger_name,
        passport_number=body.passport_number,
        amount_cents=body.amount_cents,
        reason=body.reason,
        filed_by=staff.id,
    )
    return ClaimOut.from_domain(claim)


@router.get("", response_model=ClaimList)
async def list_claims(
    container: ContainerDep,
    staff: CurrentStaff,
    status: Optional[ClaimStatus] = None,  # Optional, not "| None": FastAPI evaluates this at runtime (Python 3.9)
    limit: int = 50,
    offset: int = 0,
) -> ClaimList:
    items, total = container.claim_service.list_claims(status, limit, offset)
    return ClaimList(items=[ClaimOut.from_domain(c) for c in items], total=total, limit=limit, offset=offset)


@router.get("/{claim_id}", response_model=ClaimOut)
async def get_claim(claim_id: int, container: ContainerDep, staff: CurrentStaff) -> ClaimOut:
    return ClaimOut.from_domain(container.claim_service.get_claim(claim_id))


@router.post("/{claim_id}/cancel", response_model=ClaimOut)
async def cancel_claim(claim_id: int, container: ContainerDep, staff: CurrentStaff) -> ClaimOut:
    return ClaimOut.from_domain(container.claim_service.cancel_claim(claim_id, staff.id))
