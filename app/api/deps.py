"""FastAPI dependencies. Auth is a stub: the caller identifies via the X-Staff-Id header."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, Request

from app.container import Container
from app.domain import Staff
from app.errors import PermissionDeniedError


def get_container(request: Request) -> Container:
    return request.app.state.container


ContainerDep = Annotated[Container, Depends(get_container)]


def current_staff(container: ContainerDep, x_staff_id: Annotated[int, Header()]) -> Staff:
    staff = container.staff.get(x_staff_id)
    if staff is None:
        raise PermissionDeniedError("Unknown staff member")
    return staff


CurrentStaff = Annotated[Staff, Depends(current_staff)]
