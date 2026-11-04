from __future__ import annotations

import logging
import re
import sqlite3
from datetime import date

from app.clock import Clock
from app.db import transaction
from app.domain import Incident, IncidentKind, IncidentUpdate
from app.errors import InvalidInputError, NotFoundError
from app.repositories.incident_updates import IncidentUpdateRepository
from app.repositories.incidents import IncidentRepository
from app.repositories.staff import StaffRepository

logger = logging.getLogger(__name__)

_FLIGHT_NUMBER = re.compile(r"^[A-Z]{2}[0-9]{1,4}$")


class IncidentService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        incidents: IncidentRepository,
        updates: IncidentUpdateRepository,
        staff: StaffRepository,
        clock: Clock,
    ) -> None:
        self._conn = conn
        self._incidents = incidents
        self._updates = updates
        self._staff = staff
        self._clock = clock

    def create_incident(self, flight_number: str, flight_date: date, kind: IncidentKind) -> Incident:
        number = flight_number.strip().upper()
        if not _FLIGHT_NUMBER.match(number):
            raise InvalidInputError("Flight number must be two letters followed by 1-4 digits, e.g. BA123")
        with transaction(self._conn):
            incident = self._incidents.add(number, flight_date, kind, self._clock.now())
        logger.info("incident_created", extra={"incident_id": incident.id, "flight_number": number})
        return incident

    def get_incident(self, incident_id: int) -> Incident:
        incident = self._incidents.get(incident_id)
        if incident is None:
            raise NotFoundError("Incident not found")
        return incident

    def add_update(self, incident_id: int, note: str, author_id: int) -> IncidentUpdate:
        text = note.strip()
        if not text:
            raise InvalidInputError("Update note must not be empty")
        self.get_incident(incident_id)
        if self._staff.get(author_id) is None:
            raise NotFoundError("Staff member not found")
        with transaction(self._conn):
            return self._updates.add(incident_id, text, author_id, self._clock.now())

    def list_updates(self, incident_id: int) -> list[IncidentUpdate]:
        self.get_incident(incident_id)
        return self._updates.list_for_incident(incident_id)
