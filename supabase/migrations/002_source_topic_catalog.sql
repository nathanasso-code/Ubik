-- Ubik source-first topic catalogue v1. Apply only after review; no live migration executed.
-- Independent of Mastodon, Bluesky, RSS, GDELT and other acquisition channels.
create table if not exists public.ubik_publishers (
 id bigint generated always as identity primary key,
 hostname text not null unique,
 display_name text,
 homepage_url text,
 feed_url text,
 feed_status text not null default 'unreviewed' check (feed_status in ('unreviewed','candidate','active','unavailable','blocked')),
 last_feed_check_at timestamptz,
 created_at timestamptz not null default now()
);
create table if not exists public.ubik_documents (
 id bigint generated always as identity primary key,
 canonical_url text not null unique,
 publisher_id bigint references public.ubik_publishers(id),
 title text,
 published_at timestamptz,
 document_type text,
 validation_status text not null default 'unreviewed'
  check (validation_status in ('unreviewed','in_review','reviewed','disputed')),
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
create table if not exists public.ubik_document_discoveries (
 id bigint generated always as identity primary key,
 document_id bigint not null references public.ubik_documents(id) on delete cascade,
 channel text not null,
 external_id text not null,
 source_account_url text,
 discovered_at timestamptz not null default now(),
 metadata jsonb not null default '{}'::jsonb,
 unique(channel,external_id,document_id)
);
create index if not exists ubik_document_discoveries_document_idx on public.ubik_document_discoveries(document_id);
create table if not exists public.ubik_topics (
 id text primary key,
 name text not null,
 created_at timestamptz not null default now()
);
create table if not exists public.ubik_topic_documents (
 topic_id text not null references public.ubik_topics(id) on delete cascade,
 document_id bigint not null references public.ubik_documents(id) on delete cascade,
 relevance_status text not null default 'candidate'
  check (relevance_status in ('candidate','relevant','excluded')),
 essential_status text not null default 'not_reviewed'
  check (essential_status in ('not_reviewed','approved','revoked')),
 essential_reason text,
 essential_reviewed_at timestamptz,
 updated_at timestamptz not null default now(),
 primary key(topic_id,document_id),
 constraint essential_requires_review check (
   essential_status <> 'approved' or
   (relevance_status = 'relevant' and essential_reason is not null and
    length(trim(essential_reason)) > 0 and essential_reviewed_at is not null))
);
create index if not exists ubik_topic_documents_topic_idx on public.ubik_topic_documents(topic_id,relevance_status,essential_status);
create table if not exists public.ubik_topic_review_history (
 id bigint generated always as identity primary key,
 topic_id text not null references public.ubik_topics(id),
 document_id bigint not null references public.ubik_documents(id),
 previous_status text,
 new_status text not null,
 reason text not null,
 reviewer_id text,
 reviewed_at timestamptz not null default now()
);
-- Default deny via RLS: no public grants/policies are introduced by this migration.
alter table public.ubik_publishers enable row level security;
alter table public.ubik_documents enable row level security;
alter table public.ubik_document_discoveries enable row level security;
alter table public.ubik_topics enable row level security;
alter table public.ubik_topic_documents enable row level security;
alter table public.ubik_topic_review_history enable row level security;
