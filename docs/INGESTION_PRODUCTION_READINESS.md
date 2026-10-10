# Ingestion production-readiness gates (design only)

This dossier is for the `develop/ubik-core` branch. It does not authorize a migration, scheduled job, or processing of personal data.

## PostgreSQL / Supabase
- [x] Isolated draft schema with page snapshots, observation identities, scope cursor, owner, expiry and fencing epoch.
- [x] Transaction templates describing owner/epoch checks and atomic page + cursor persistence.
- [ ] Implement and test a real PostgreSQL adapter against a disposable development database. SQL templates are **not executable transaction logic** without application-side validation.
- [ ] Verify unique identity, checksum canonicalization (JSONB reserialization changes byte digests), rollback, expired lease, stale fencing epoch and lease renewal.
- [ ] Define least-privilege database role and row-level security policy, backup/restore, retention, encryption, schema migration rollback.
- [ ] Choose durable object storage or database retention limits for raw snapshots; verify deletion propagation.
- [ ] Load test multi-host workers, lease expiry, retries and worker termination.

## Social content lifecycle
- [x] Read-only decision model for missing timestamps, age thresholds and externally verified removal IDs.
- [ ] Determine platform-specific public API deletion signals and terms; distinguish 404, 403, network errors and instance policy.
- [ ] Define a verified removal-event ingestion path; do not infer deletion from transient unavailability.
- [ ] Implement retention/deletion of raw observations, archives, backups, derived indexes and summaries.
- [ ] Privacy/security review, purpose limitation, data subject request workflow and auditable erasure.
- [ ] Confirm Mastodon HTTP 422 behavior on an authorized instance before enabling the connector.

## Scheduler and epistemic coverage
- [ ] Explicit approved source allowlists, per-source quotas, monitoring, backoff and outage handling.
- [ ] Event-level clustering must remain separate from acquisition; preserve singletons and source provenance.
- [ ] Measure actual coverage and duplicates across rolling windows; current smoke tests do not prove completeness.
- [ ] Add operator-visible pause/kill switch and idempotent deployment procedure.
- [ ] Obtain explicit approval for production credentials, migrations, and unattended recurring network requests.

## Current boundary
The existing SQLite runner is manually opt-in and covered by offline tests. PostgreSQL SQL is a draft. Social lifecycle code produces recommendations only, with **no automatic deletion**. No Supabase database or production system has been changed.
