-- 001_initial: staff, incidents, append-only incident updates, compensation claims.
-- Never edit an applied migration; add 002_..., 003_... instead (ADR 0006).

CREATE TABLE staff (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('agent', 'supervisor', 'manager'))
);

CREATE TABLE incidents (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number TEXT NOT NULL,
    flight_date   TEXT NOT NULL,
    kind          TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

-- Append-only: the triggers below make UPDATE and DELETE impossible (ADR 0003).
CREATE TABLE incident_updates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL REFERENCES incidents(id),
    note        TEXT NOT NULL,
    author_id   INTEGER NOT NULL REFERENCES staff(id),
    created_at  TEXT NOT NULL
);

CREATE TRIGGER incident_updates_no_update
BEFORE UPDATE ON incident_updates
BEGIN
    SELECT RAISE(ABORT, 'incident_updates is append-only');
END;

CREATE TRIGGER incident_updates_no_delete
BEFORE DELETE ON incident_updates
BEGIN
    SELECT RAISE(ABORT, 'incident_updates is append-only');
END;

-- amount_cents is an integer number of cents (ADR 0002).
CREATE TABLE claims (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id     INTEGER NOT NULL REFERENCES incidents(id),
    passenger_name  TEXT NOT NULL,
    passport_number TEXT NOT NULL,
    amount_cents    INTEGER NOT NULL CHECK (amount_cents > 0),
    reason          TEXT NOT NULL,
    status          TEXT NOT NULL,
    filed_by        INTEGER NOT NULL REFERENCES staff(id),
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- One active claim per passenger per incident (see ACTIVE_STATUSES in app/domain.py).
CREATE UNIQUE INDEX ux_claims_one_active_per_passenger_incident
ON claims (incident_id, passport_number)
WHERE status = 'filed';
