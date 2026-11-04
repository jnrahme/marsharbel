-- Contract for phase 4 (Postgres). Not applied in phase 1; content is file-backed until then.
create table content_item (
  id text primary key,
  type text not null check (type in ('news','saint','prayer','book','audio','rosary_episode')),
  slug text not null,
  status text not null default 'draft' check (status in ('draft','review','published','archived')),
  access text not null default 'public' check (access in ('public','subscriber')),
  published_at timestamptz,
  source_refs jsonb not null default '[]',
  rights jsonb not null default '{}',
  unique (type, slug)
);
create table content_locale (
  item_id text not null references content_item(id) on delete cascade,
  locale text not null,
  title text not null,
  body_json jsonb not null default '{}',
  status text not null default 'draft' check (status in ('draft','review','published')),
  reviewed_by text,
  master_sha256 text,
  primary key (item_id, locale)
);
create table media_asset (
  id text primary key,
  kind text not null,
  path text not null check (path like '/%'),
  mime text,
  bytes bigint,
  sha256 text,
  access text not null default 'public',
  rights jsonb not null default '{}'
);
create table content_link (
  from_id text not null references content_item(id) on delete cascade,
  to_id text not null references content_item(id) on delete cascade,
  rel text not null,
  primary key (from_id, to_id, rel)
);
create table search_index (
  item_id text not null references content_item(id) on delete cascade,
  locale text not null,
  tsv tsvector not null,
  primary key (item_id, locale)
);
create index search_index_tsv on search_index using gin (tsv);
