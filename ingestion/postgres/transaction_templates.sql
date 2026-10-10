-- Transaction templates for a PostgreSQL-backed ingestion worker.
-- Bind parameters using a database driver. Never interpolate scope/user input.
-- These are design references, not automatically applied migrations.

-- ACQUIRE: one transaction. A new lease increments the fencing epoch.
-- :scope_key text, :owner uuid, :ttl_seconds integer (1..3600)
BEGIN;
INSERT INTO ubik_ingestion.scopes(scope_key)
VALUES (:scope_key) ON CONFLICT (scope_key) DO NOTHING;
SELECT lease_owner, lease_until, lease_epoch, cursor, head_sha256
FROM ubik_ingestion.scopes WHERE scope_key = :scope_key FOR UPDATE;
-- Application must refuse acquisition when lease_owner IS NOT NULL
-- AND lease_until > transaction_timestamp(). Otherwise:
UPDATE ubik_ingestion.scopes
SET lease_owner = :owner,
    lease_until = transaction_timestamp() + (:ttl_seconds * interval '1 second'),
    lease_epoch = lease_epoch + 1,
    updated_at = transaction_timestamp()
WHERE scope_key = :scope_key
RETURNING cursor, head_sha256, lease_epoch;
COMMIT;

-- COMMIT PAGE: one transaction, only if lease owner AND epoch match.
-- Lock scope first and reject an expired or superseded lease.
BEGIN;
SELECT lease_owner, lease_epoch, lease_until
FROM ubik_ingestion.scopes WHERE scope_key = :scope_key FOR UPDATE;
-- Application must reject unless owner=:owner, epoch=:epoch,
-- and lease_until > transaction_timestamp().
INSERT INTO ubik_ingestion.pages(scope_key, payload_sha256, payload)
VALUES (:scope_key, :digest, :payload::jsonb)
ON CONFLICT (scope_key, payload_sha256) DO NOTHING;
-- If inserted, insert each normalized observation with a stable position.
-- If conflict, verify the existing payload matches the submitted page.
-- Then atomically advance cursor/head only while the same lease is held:
UPDATE ubik_ingestion.scopes
SET cursor = :next_cursor, head_sha256 = :digest,
    lease_until = transaction_timestamp() + (:ttl_seconds * interval '1 second'),
    updated_at = transaction_timestamp()
WHERE scope_key = :scope_key AND lease_owner = :owner
  AND lease_epoch = :epoch AND lease_until > transaction_timestamp();
-- Application must require exactly one updated row.
COMMIT;

-- RELEASE: compare-and-set, never clear a newer owner's lease.
UPDATE ubik_ingestion.scopes
SET lease_owner = NULL, lease_until = NULL, updated_at = now()
WHERE scope_key = :scope_key AND lease_owner = :owner AND lease_epoch = :epoch;
