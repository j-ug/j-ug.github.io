create schema if not exists safelink_private;
revoke all on schema safelink_private from public, anon, authenticated;
create table safelink_private.circles (
 invite text primary key check (invite ~ '^[a-f0-9]{32}$'),
 area text not null check (area in ('Central Trichy','Woraiyur','Manapparai','Srirangam','Thillai Nagar'))
);
create table safelink_private.members (
 invite text references safelink_private.circles on delete cascade,
 uid uuid references auth.users on delete cascade,
 alias text not null check (char_length(alias) between 1 and 25),
 primary key(invite,uid)
);
create table safelink_private.messages (
 id bigint generated always as identity primary key,
 invite text not null,
 uid uuid not null,
 message text not null check (message in ('Available for a public group walk','Looking for a walking buddy','Available for a check-in')),
 posted timestamptz not null default now(),
 foreign key(invite,uid) references safelink_private.members on delete cascade
);
alter table safelink_private.circles enable row level security;
alter table safelink_private.members enable row level security;
alter table safelink_private.messages enable row level security;
create or replace function safelink_private.safelink_circle_join(p_invite text,p_area text,p_alias text,p_create boolean)
returns text language plpgsql security definer set search_path='' as $$
declare u uuid := auth.uid();
begin
 if u is null then raise exception 'Sign in first'; end if;
 perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(u::text,0));
 if (select count(*) from safelink_private.members where uid=u)>=8
 and not exists(select 1 from safelink_private.members where uid=u and invite=p_invite) then
  raise exception 'Leave another circle before opening a new one';
 end if;
 if p_create then insert into safelink_private.circles values(p_invite,p_area); end if;
 if not exists (select 1 from safelink_private.circles where invite=p_invite and area=p_area) then raise exception 'Invite does not match this locality'; end if;
 insert into safelink_private.members values(p_invite,u,trim(p_alias)) on conflict (invite,uid) do update set alias=excluded.alias;
 return p_invite;
end $$;
create or replace function safelink_private.safelink_circle_read(p_invite text)
returns table(alias text,message text) language sql security definer set search_path='' as $$
 select m.alias,p.message from safelink_private.messages p join safelink_private.members m using(invite,uid)
 where p.invite=p_invite and p.posted>now()-interval '24 hours'
 and exists(select 1 from safelink_private.members s where s.invite=p_invite and s.uid=auth.uid())
 order by p.id desc limit 40
$$;
create or replace function safelink_private.safelink_circle_post(p_invite text,p_message text)
returns void language plpgsql security definer set search_path='' as $$
declare u uuid := auth.uid();
begin
 if u is null or not exists(select 1 from safelink_private.members where invite=p_invite and uid=u) then raise exception 'Join the circle first'; end if;
 perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(u::text,0));
 if exists(select 1 from safelink_private.messages where uid=u and posted>now()-interval '30 seconds') then raise exception 'Wait 30 seconds between messages'; end if;
 delete from safelink_private.messages where uid=u and posted<now()-interval '24 hours';
 insert into safelink_private.messages(invite,uid,message) values(p_invite,u,p_message);
end $$;
create or replace function safelink_private.safelink_circle_leave(p_invite text)
returns void language sql security definer set search_path='' as $$
 delete from safelink_private.members where uid=auth.uid() and invite=p_invite
$$;
grant usage on schema safelink_private to authenticated;
create function public.safelink_circle_join(p_invite text,p_area text,p_alias text,p_create boolean) returns text language sql security invoker set search_path='' as $$ select safelink_private.safelink_circle_join(p_invite,p_area,p_alias,p_create) $$;
revoke all on function public.safelink_circle_join(text,text,text,boolean), safelink_private.safelink_circle_join(text,text,text,boolean) from public, anon, authenticated;
grant execute on function public.safelink_circle_join(text,text,text,boolean), safelink_private.safelink_circle_join(text,text,text,boolean) to authenticated;
create function public.safelink_circle_read(p_invite text) returns table(alias text,message text) language sql security invoker set search_path='' as $$ select * from safelink_private.safelink_circle_read(p_invite) $$;
revoke all on function public.safelink_circle_read(text), safelink_private.safelink_circle_read(text) from public, anon, authenticated;
grant execute on function public.safelink_circle_read(text), safelink_private.safelink_circle_read(text) to authenticated;
create function public.safelink_circle_post(p_invite text,p_message text) returns void language sql security invoker set search_path='' as $$ select safelink_private.safelink_circle_post(p_invite,p_message) $$;
revoke all on function public.safelink_circle_post(text,text), safelink_private.safelink_circle_post(text,text) from public, anon, authenticated;
grant execute on function public.safelink_circle_post(text,text), safelink_private.safelink_circle_post(text,text) to authenticated;
create function public.safelink_circle_leave(p_invite text) returns void language sql security invoker set search_path='' as $$ select safelink_private.safelink_circle_leave(p_invite) $$;
revoke all on function public.safelink_circle_leave(text), safelink_private.safelink_circle_leave(text) from public, anon, authenticated;
grant execute on function public.safelink_circle_leave(text), safelink_private.safelink_circle_leave(text) to authenticated;
create table public.safelink_family (
 id uuid primary key default gen_random_uuid(),
 owner uuid not null default auth.uid() references auth.users on delete cascade,
 label text not null check (char_length(trim(label)) between 1 and 50),
 phone text not null check (phone ~ '^\+?[0-9]{7,15}$')
);
alter table public.safelink_family enable row level security;
revoke all on table public.safelink_family from public, anon, authenticated;
grant select, insert, delete on table public.safelink_family to authenticated;
create policy family_private on public.safelink_family for all to authenticated using ((select auth.uid())=owner) with check ((select auth.uid())=owner);
