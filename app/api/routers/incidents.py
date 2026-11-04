"""Routers are thin: parse input, call one service method, shape the output."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import ContainerDep, CurrentStaff
from app.schemas import IncidentCreate, IncidentOut, IncidentUpdateCreate, IncidentUpdateOut

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentOut, status_code=201)
async def create_incident(body: IncidentCreate, container: ContainerDep, staff: CurrentStaff) -> IncidentOut:
    incident = container.incident_service.create_incident(body.flight_number, body.flight_date, body.kind)
    return IncidentOut.from_domain(incident)


@router.get("/{incident_id}", response_model=IncidentOut)
async def get_incident(incident_id: int, container: ContainerDep, staff: CurrentStaff) -> IncidentOut:
    return IncidentOut.from_domain(container.incident_service.get_incident(incident_id))


@router.post("/{incident_id}/updates", response_model=IncidentUpdateOut, status_code=201)
async def add_update(
    incident_id: int, body: IncidentUpdateCreate, container: ContainerDep, staff: CurrentStaff
) -> IncidentUpdateOut:
    update = container.incident_service.add_update(incident_id, body.note, staff.id)
    return IncidentUpdateOut.from_domain(update)


@router.get("/{incident_id}/updates", response_model=list[IncidentUpdateOut])
async def list_updates(incident_id: int, container: ContainerDep, staff: CurrentStaff) -> list[IncidentUpdateOut]:
    return [IncidentUpdateOut.from_domain(u) for u in container.incident_service.list_updates(incident_id)]
