-- Ubik ingestion: isolated experimental PostgreSQL schema.
-- Apply only to a dedicated development database after review.
-- No triggers, cron jobs, grants, production table modifications, or RLS bypass.
BEGIN;
CREATE SCHEMA IF NOT EXISTS ubik_ingestion;
CREATE TABLE IF NOT EXISTS ubik_ingestion.scopes (
    scope_key text PRIMARY KEY,
    cursor text,
    head_sha256 text,
    lease_owner uuid,
    lease_epoch bigint NOT NULL DEFAULT 0,
    lease_until timestamptz,
    updated_at timestamptz NOT NULL DEFAULT now(),
    CHECK (head_sha256 IS NULL OR head_sha256 ~ '^[0-9a-f]{64}$')
);
CREATE TABLE IF NOT EXISTS ubik_ingestion.pages (
    page_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    scope_key text NOT NULL REFERENCES ubik_ingestion.scopes(scope_key),
    payload_sha256 text NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
    payload jsonb NOT NULL,
    observed_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (scope_key, payload_sha256),
    CHECK (jsonb_typeof(payload) = 'object'),
    CHECK (jsonb_typeof(payload->'observations') = 'array')
);
CREATE TABLE IF NOT EXISTS ubik_ingestion.observations (
    page_id bigint NOT NULL REFERENCES ubik_ingestion.pages(page_id),
    position integer NOT NULL CHECK (position >= 0),
    connector text NOT NULL,
    source_id text NOT NULL,
    external_id text NOT NULL,
    payload jsonb NOT NULL,
    PRIMARY KEY (page_id, position),
    CHECK (connector <> '' AND source_id <> '' AND external_id <> '')
);
CREATE INDEX IF NOT EXISTS ingestion_observations_identity
    ON ubik_ingestion.observations (connector, source_id, external_id);
-- Keep the prototype isolated. Explicit access policy is a deployment prerequisite.
REVOKE ALL ON SCHEMA ubik_ingestion FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA ubik_ingestion FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA ubik_ingestion FROM PUBLIC;
COMMIT;
