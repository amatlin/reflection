-- Run this in the Supabase SQL Editor

create table if not exists events (
  id bigint generated always as identity primary key,
  timestamp timestamptz not null default now(),
  event_type text not null,
  page_path text,
  element_id text,
  element_tag text,
  element_text text,
  visitor_id text,
  raw_properties jsonb default '{}'::jsonb
);

-- Index for recent-events queries
create index if not exists idx_events_timestamp on events (timestamp desc);

-- Enable Realtime (for future multi-worker use)
alter publication supabase_realtime add table events;

-- RLS: anon can read, service_role can insert
alter table events enable row level security;

create policy "anon_read" on events
  for select to anon
  using (true);

create policy "service_role_insert" on events
  for insert to service_role
  with check (true);
