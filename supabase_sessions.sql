-- Ejecuta este archivo una vez en Supabase > SQL Editor > New query.
-- Si la tabla existe, conserva sus filas y la definición de sus columnas.
begin;

create table if not exists public.jarvis_messages (
    id uuid primary key default gen_random_uuid(),
    role text not null,
    content text not null,
    created_at timestamptz not null default now()
);

alter table public.jarvis_messages add column if not exists session_id uuid;

create index if not exists jarvis_messages_session_created_idx
    on public.jarvis_messages (session_id, created_at desc);

alter table public.jarvis_messages enable row level security;

-- La clave secreta se usa únicamente en el servidor de Streamlit.
grant select, insert on table public.jarvis_messages to service_role;

commit;
