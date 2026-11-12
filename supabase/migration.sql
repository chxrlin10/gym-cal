-- v77. Backup first; run in SQL Editor as project owner. Transactional and repeatable.
-- Existing orphan rows/duplicate user_id deliberately abort this migration: inspect, don't delete blindly.
begin;
create table if not exists public.user_data (
 user_id uuid primary key references auth.users(id) on delete cascade,
 data jsonb not null, updated_at timestamptz not null default now()
);
create unique index if not exists gymcal_user_data_uid on public.user_data(user_id);
do $$ declare c record; begin
 for c in select conname from pg_constraint where conrelid='public.user_data'::regclass and contype='f'
 and confrelid='auth.users'::regclass loop
 execute format('alter table public.user_data drop constraint %I',c.conname); end loop;
 alter table public.user_data add constraint gymcal_user_data_user_fk foreign key(user_id) references auth.users(id) on delete cascade;
end $$;
create table if not exists public.account_deletions (
 user_id uuid primary key references auth.users(id) on delete cascade,
 requested_at timestamptz not null default now()
);
create table if not exists public.entitlements (
 user_id uuid primary key references auth.users(id) on delete cascade,
 active boolean not null default false, product text, expires_at timestamptz,
 source text default 'revenuecat', updated_at timestamptz not null default now()
);
alter table public.entitlements add column if not exists checked_at timestamptz;
-- Remove any permissive old policies for these app-owned tables.
do $$ declare p record; begin
 for p in select tablename,policyname from pg_policies where schemaname='public' and tablename in ('user_data','entitlements','account_deletions') loop
 execute format('drop policy %I on public.%I',p.policyname,p.tablename); end loop;
end $$;
alter table public.user_data enable row level security;
alter table public.entitlements enable row level security;
alter table public.account_deletions enable row level security;
revoke all on public.user_data,public.entitlements,public.account_deletions from public,anon,authenticated;
grant select,insert,update,delete on public.user_data to authenticated;
grant select on public.entitlements,public.account_deletions to authenticated;
grant all on public.user_data,public.entitlements,public.account_deletions to service_role;
create policy deletion_own_read on public.account_deletions for select to authenticated using(auth.uid()=user_id);
create policy data_own_read on public.user_data for select to authenticated using(auth.uid()=user_id);
create policy data_own_insert on public.user_data for insert to authenticated with check(auth.uid()=user_id and not exists(select 1 from public.account_deletions where user_id=auth.uid()));
create policy data_own_update on public.user_data for update to authenticated using(auth.uid()=user_id) with check(auth.uid()=user_id and not exists(select 1 from public.account_deletions where user_id=auth.uid()));
create policy data_own_delete on public.user_data for delete to authenticated using(auth.uid()=user_id);
create policy entitlements_select_own on public.entitlements for select to authenticated using(auth.uid()=user_id);
create or replace function public.apply_rc_snapshot(p_user_id uuid,p_active boolean,p_product text,p_expires_at timestamptz,p_checked_at timestamptz)
returns void language plpgsql security definer set search_path='' as $$
begin
 if p_checked_at is null or p_checked_at > now()+interval '5 minutes' then raise exception 'Invalid snapshot time'; end if;
 if not exists(select 1 from auth.users where id=p_user_id) or exists(select 1 from public.account_deletions where user_id=p_user_id) then return; end if;
 insert into public.entitlements(user_id,active,product,expires_at,source,updated_at,checked_at)
 values(p_user_id,p_active,p_product,p_expires_at,'revenuecat',now(),p_checked_at)
 on conflict(user_id) do update set active=excluded.active,product=excluded.product,expires_at=excluded.expires_at,source=excluded.source,updated_at=now(),checked_at=excluded.checked_at
 where public.entitlements.checked_at is null or public.entitlements.checked_at < excluded.checked_at;
end $$;
revoke all on function public.apply_rc_snapshot(uuid,boolean,text,timestamptz,timestamptz) from public,anon,authenticated;
grant execute on function public.apply_rc_snapshot(uuid,boolean,text,timestamptz,timestamptz) to service_role;
commit;
