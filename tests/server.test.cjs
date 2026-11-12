const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),{transformSync}=require('esbuild'),path=require('node:path');
const root=path.join(__dirname,'../supabase/functions');
const compile=s=>transformSync(s,{loader:'ts',format:'cjs',target:'es2022'}).code;
let passed=0;const test=async(n,f)=>{await f();passed++;console.log('PASS',n)};
function shared(){const c={module:{exports:{}},exports:{},Date,Number,Math,Deno:{env:{get:()=>''}},AbortSignal,fetch};vm.createContext(c);vm.runInContext(compile(fs.readFileSync(root+'/_shared/revenuecat.ts','utf8')),c);return c.module.exports}
const snap=shared().entitlementSnapshot,now=Date.now();const body=(patch={})=>({request_date_ms:now,subscriber:{entitlements:{premium:{product_identifier:'monthly',expires_date:new Date(now+3600000).toISOString()}},subscriptions:{monthly:{store:'play_store',is_sandbox:false,...patch}}}});
function webhook(){let handler;const calls=[];const env={RC_WEBHOOK_SECRET:'secret',RC_APP_ID:'app',RC_ENVIRONMENT:'PRODUCTION'};
const client={auth:{admin:{getUserById:async()=>({data:{user:{}}})}},from:()=>({select:()=>({eq:()=>({maybeSingle:async()=>({data:null})})})}),rpc:async(n,p)=>{calls.push(p);return {error:null}}};
const c={Deno:{env:{get:k=>env[k]},serve:f=>handler=f},Response,Request,JSON,Set,UUID:shared().UUID,rcRequest:async()=>new Response(JSON.stringify(body())),entitlementSnapshot:snap,createClient:()=>client};vm.createContext(c);vm.runInContext(compile(fs.readFileSync(root+'/revenuecat-webhook/index.ts','utf8').replace(/^import .*;\n/gm,'')),c);return {handler,calls,env,c}}
(async()=>{
await test('Active recurring entitlement',()=>assert.equal(snap(body(),false).active,true));
await test('Sandbox cannot grant production',()=>assert.equal(snap(body({is_sandbox:true}),false).active,false));
await test('Refunded purchase inactive',()=>assert.equal(snap(body({refunded_at:new Date().toISOString()}),false).active,false));
await test('Null expiry cannot grant recurring lifetime',()=>{const b=body();b.subscriber.entitlements.premium.expires_date=null;assert.equal(snap(b,false).active,false)});
await test('Grace period preserved',()=>{const b=body({grace_period_expires_date:new Date(now+10000).toISOString()});b.subscriber.entitlements.premium.expires_date=new Date(now-10000).toISOString();assert.equal(snap(b,false).active,true)});
await test('Expired entitlement revoked',()=>{const b=body();b.subscriber.entitlements.premium.expires_date=new Date(now-10000).toISOString();assert.equal(snap(b,false).active,false)});
await test('Webhook rejects missing secret',async()=>{const w=webhook(),r=await w.handler(new Request('https://example.test',{method:'POST',body:'{}'}));assert.equal(r.status,401);assert.equal(w.calls.length,0)});
await test('Wrong app is ignored',async()=>{const w=webhook(),r=await w.handler(new Request('https://example.test',{method:'POST',headers:{Authorization:'Bearer secret'},body:JSON.stringify({event:{id:'e',type:'RENEWAL',app_id:'wrong'}})}));assert.equal(r.status,200);assert.equal(w.calls.length,0)});
await test('Transfer reconciles both accounts',async()=>{const w=webhook(),ids=['11111111-1111-4111-8111-111111111111','22222222-2222-4222-8222-222222222222'];const r=await w.handler(new Request('https://example.test',{method:'POST',headers:{Authorization:'Bearer secret'},body:JSON.stringify({event:{id:'e',type:'TRANSFER',app_id:'app',transferred_from:[ids[0]],transferred_to:[ids[1]]}})}));assert.equal(r.status,200);assert.equal(w.calls.length,2);assert.equal(w.calls[1].p_user_id,ids[1]);assert.ok(w.calls[1].p_expires_at)});
await test('Provider failure returns retryable status',async()=>{const w=webhook();w.c.rcRequest=async()=>new Response('error',{status:500});const r=await w.handler(new Request('https://example.test',{method:'POST',headers:{Authorization:'Bearer secret'},body:JSON.stringify({event:{id:'e',type:'RENEWAL',app_id:'app',app_user_id:'11111111-1111-4111-8111-111111111111'}})}));assert.equal(r.status,503);assert.equal(w.calls.length,0)});
console.log(`${passed} server tests passed (providers mocked; deploy/RLS require real project tests).`);
})().catch(e=>{console.error(e);process.exitCode=1});
