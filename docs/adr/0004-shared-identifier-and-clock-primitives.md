# ADR 0004: Centralize UUID and UTC clock primitives

## Status

Accepted

## Context

Feature modules will need application-owned identifiers and timezone-aware timestamps. Repeating
direct calls to UUID and clock libraries makes these technical dependencies harder to standardize
and replace in tests.

## Decision

Expose `new_uuid()` from `app.shared.identifiers` and `utc_now()` from `app.shared.clock`. Shared
persistence mixins use these primitives by default. Feature code uses the same primitives whenever
it needs an identifier or current UTC time.

## Consequences

- Timestamps are consistently timezone-aware and UTC-based.
- UUID and clock behavior has one documented extension point.
- Tests can patch a single clock primitive where deterministic time is required.
