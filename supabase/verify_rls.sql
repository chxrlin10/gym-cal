-- Inspection only. Run AFTER migration.sql; then test real JWTs for A, B and anonymous.
select n.nspname,c.relname,c.relrowsecurity from pg_class c join pg_namespace n on n.oid=c.relnamespace
 where n.nspname='public' and c.relname in ('user_data','entitlements','account_deletions');
select tablename,policyname,cmd,roles,qual,with_check from pg_policies
 where schemaname='public' and tablename in ('user_data','entitlements','account_deletions') order by tablename,cmd;
select table_name,grantee,privilege_type from information_schema.role_table_grants
 where table_schema='public' and table_name in ('user_data','entitlements','account_deletions')
 and grantee in ('anon','PUBLIC','authenticated') order by table_name,grantee;
select conrelid::regclass,conname,pg_get_constraintdef(oid) from pg_constraint
 where conrelid in ('public.user_data'::regclass,'public.entitlements'::regclass,'public.account_deletions'::regclass) and contype in ('p','u','f');
select has_function_privilege('anon','public.apply_rc_snapshot(uuid,boolean,text,timestamptz,timestamptz)','EXECUTE') as anon_rpc_must_be_false,
 has_function_privilege('authenticated','public.apply_rc_snapshot(uuid,boolean,text,timestamptz,timestamptz)','EXECUTE') as user_rpc_must_be_false;
