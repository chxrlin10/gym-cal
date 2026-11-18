-- v93 (revisão da auditoria, 17/11/2026). Faça backup antes. Rode INTEIRO no SQL Editor, como dono do projeto.
-- Transacional: qualquer erro desfaz tudo, nada fica pela metade.
-- Repetível: rodar de novo não muda o que já estiver certo (FK e chave única corretas são mantidas).
-- Banco que já existe: a etapa 1 só lê. Se encontrar estrutura ou dados incompatíveis (coluna com tipo diferente,
-- user_id nulo ou repetido, linha de usuário que não existe mais), ABORTA com mensagem e não altera nada.
-- Nenhuma linha é apagada por esta migração.
begin;
-- Não fica esperando bloqueio: se o app estiver segurando uma tabela, falha em 5 s e você roda de novo.
set local lock_timeout = '5s';
set local statement_timeout = '120s';

-- Funções auxiliares temporárias: ficam em pg_temp e somem ao fim da sessão (não vão para o schema public).
create or replace function pg_temp.gc_col(t text, c text, typ text, required boolean) returns void language plpgsql as $$
declare cur text;
begin
 if to_regclass('public.'||t) is null then return; end if;
 select data_type into cur from information_schema.columns where table_schema='public' and table_name=t and column_name=c;
 if cur is null then
  if required then raise exception 'Gym.cal: public.% existe mas não tem a coluna %. Nada foi alterado.', t, c; end if;
 elsif cur <> typ then
  raise exception 'Gym.cal: public.%.% é do tipo % (esperado %). Nada foi alterado.', t, c, cur, typ;
 end if;
end $$;

create or replace function pg_temp.gc_nulls(t text, c text) returns void language plpgsql as $$
declare n bigint;
begin
 if to_regclass('public.'||t) is null then return; end if;
 if not exists (select 1 from information_schema.columns where table_schema='public' and table_name=t and column_name=c) then return; end if;
 execute format('select count(*) from public.%I where %I is null', t, c) into n;
 if n > 0 then raise exception 'Gym.cal: public.% tem % linha(s) com % vazio. Nada foi alterado.', t, n, c; end if;
end $$;

create or replace function pg_temp.gc_rows(t text) returns void language plpgsql as $$
declare n bigint;
begin
 if to_regclass('public.'||t) is null then return; end if;
 perform pg_temp.gc_nulls(t, 'user_id');
 execute format('select count(*) - count(distinct user_id) from public.%I', t) into n;
 if n > 0 then raise exception 'Gym.cal: public.% tem % user_id repetido(s). Nada foi alterado.', t, n; end if;
 execute format('select count(*) from public.%I x where not exists (select 1 from auth.users u where u.id = x.user_id)', t) into n;
 if n > 0 then raise exception 'Gym.cal: public.% tem % linha(s) de usuário que não existe mais em auth.users. Nada foi alterado.', t, n; end if;
end $$;

-- Garante UNIQUE em user_id. Reaproveita PK, constraint ou índice único que já cubra exatamente (user_id).
create or replace function pg_temp.gc_unique(t text, cname text) returns void language plpgsql as $$
declare rel regclass := ('public.'||t)::regclass; att int2;
begin
 select attnum into att from pg_attribute where attrelid=rel and attname='user_id' and not attisdropped;
 if exists (select 1 from pg_index i where i.indrelid=rel and i.indisunique and i.indisvalid and i.indpred is null
            and i.indexprs is null and string_to_array(i.indkey::text,' ')::int2[] = array[att]) then return; end if;
 execute format('alter table public.%I add constraint %I unique (user_id)', t, cname);
end $$;

-- Garante FK user_id -> auth.users(id) ON DELETE CASCADE. Só mexe em FKs da coluna user_id, e só se não estiverem certas.
create or replace function pg_temp.gc_fk(t text, cname text) returns void language plpgsql as $$
declare rel regclass := ('public.'||t)::regclass; att int2; uid int2; c record;
begin
 select attnum into att from pg_attribute where attrelid=rel and attname='user_id' and not attisdropped;
 select attnum into uid from pg_attribute where attrelid='auth.users'::regclass and attname='id';
 if exists (select 1 from pg_constraint where conrelid=rel and contype='f' and conkey=array[att]
            and confrelid='auth.users'::regclass and confkey=array[uid] and confdeltype='c') then return; end if;
 for c in select conname from pg_constraint where conrelid=rel and contype='f' and conkey=array[att] loop
  execute format('alter table public.%I drop constraint %I', t, c.conname);
 end loop;
 execute format('alter table public.%I add constraint %I foreign key (user_id) references auth.users(id) on delete cascade', t, cname);
end $$;

-- 1. Conferência do que já existe (só leitura; aborta se algo não bater).
do $$ begin
 perform pg_temp.gc_col('user_data','user_id','uuid',true);
 perform pg_temp.gc_col('user_data','data','jsonb',true);
 perform pg_temp.gc_col('user_data','updated_at','timestamp with time zone',false);
 perform pg_temp.gc_rows('user_data');
 perform pg_temp.gc_nulls('user_data','data');
 perform pg_temp.gc_col('entitlements','user_id','uuid',true);
 perform pg_temp.gc_col('entitlements','active','boolean',false);
 perform pg_temp.gc_col('entitlements','product','text',false);
 perform pg_temp.gc_col('entitlements','expires_at','timestamp with time zone',false);
 perform pg_temp.gc_col('entitlements','source','text',false);
 perform pg_temp.gc_col('entitlements','updated_at','timestamp with time zone',false);
 perform pg_temp.gc_col('entitlements','checked_at','timestamp with time zone',false);
 perform pg_temp.gc_rows('entitlements');
 perform pg_temp.gc_nulls('entitlements','active');
 perform pg_temp.gc_col('account_deletions','user_id','uuid',true);
 perform pg_temp.gc_col('account_deletions','requested_at','timestamp with time zone',false);
 perform pg_temp.gc_rows('account_deletions');
end $$;

-- 2. Tabelas que faltam (as que já existem ficam como estão e são ajustadas abaixo).
create table if not exists public.user_data (
 user_id uuid primary key references auth.users(id) on delete cascade,
 data jsonb not null, updated_at timestamptz not null default now()
);
create table if not exists public.account_deletions (
 user_id uuid primary key references auth.users(id) on delete cascade,
 requested_at timestamptz not null default now()
);
create table if not exists public.entitlements (
 user_id uuid primary key references auth.users(id) on delete cascade,
 active boolean not null default false, product text, expires_at timestamptz,
 source text default 'revenuecat', updated_at timestamptz not null default now(), checked_at timestamptz
);

-- 3. Colunas que faltam em tabelas antigas (adicionar coluna não mexe nos dados existentes).
alter table public.user_data add column if not exists updated_at timestamptz not null default now();
alter table public.entitlements add column if not exists active boolean not null default false;
alter table public.entitlements add column if not exists product text;
alter table public.entitlements add column if not exists expires_at timestamptz;
alter table public.entitlements add column if not exists source text default 'revenuecat';
alter table public.entitlements add column if not exists updated_at timestamptz not null default now();
alter table public.entitlements add column if not exists checked_at timestamptz;
alter table public.account_deletions add column if not exists requested_at timestamptz not null default now();
alter table public.user_data alter column user_id set not null, alter column data set not null;
alter table public.entitlements alter column user_id set not null, alter column active set not null, alter column active set default false;
alter table public.account_deletions alter column user_id set not null;

-- 4. Um registro por usuário e exclusão em cascata a partir de auth.users (o apply_rc_snapshot depende do UNIQUE).
do $$ begin
 perform pg_temp.gc_unique('user_data','gymcal_user_data_user_key');
 perform pg_temp.gc_unique('entitlements','gymcal_entitlements_user_key');
 perform pg_temp.gc_unique('account_deletions','gymcal_account_deletions_user_key');
 perform pg_temp.gc_fk('user_data','gymcal_user_data_user_fk');
 perform pg_temp.gc_fk('entitlements','gymcal_entitlements_user_fk');
 perform pg_temp.gc_fk('account_deletions','gymcal_account_deletions_user_fk');
end $$;

-- 5. Políticas: remove as antigas dessas três tabelas (inclusive permissivas feitas à mão) e cria as do app.
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

-- 6. Reconciliação de assinatura: só o service_role (Edge Function) chama.
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
