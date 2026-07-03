create table if not exists public.roles (
    id bigint generated always as identity primary key,
    name text not null unique,
    description text,
    created_at timestamptz not null default now()
);

insert into public.roles (name, description)
values
('Admin', 'System administrator'),
('Manager', 'Store manager'),
('Cashier', 'POS cashier')
on conflict (name) do nothing;