# Supabase simulado para os testes de sincronização (auth, user_data com condição de updated_at, entitlements, exclusão).
# srv.fail: rede fora; srv.dropnext: servidor grava mas a resposta se perde; srv.delay/delaypatch: respostas lentas.
import json,re,time,urllib.parse
SB="https://ypudxlvlssvulbfuwdxu.supabase.co"
class Srv:
    def __init__(s):
        s.users={};s.rows={};s.n=0;s.fail=False;s.log=[];s.clock=0;s.delay=0;s.dropnext=0;s.delfail=False;s.ent={}
    def now(s):
        s.clock+=1;return time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(1.78e9+s.clock))+".%03d+00:00"%0
def install(ctx,srv):
    def h(route):
        r=route.request;u=urllib.parse.urlparse(r.url);path=u.path;q=urllib.parse.parse_qs(u.query)
        hd=r.headers;tk=(hd.get("authorization") or "").replace("Bearer ","")
        def js(code,obj,extra=None):
            hh={"access-control-allow-origin":"*","content-type":"application/json"}
            route.fulfill(status=code,headers=hh,body=json.dumps(obj))
        if r.method=="OPTIONS":
            route.fulfill(status=204,headers={"access-control-allow-origin":"*","access-control-allow-headers":"*","access-control-allow-methods":"*"});return
        if srv.fail: route.abort();return
        uid=tk[4:] if tk.startswith("tok:") else None
        srv.log.append((r.method,path,uid))
        if path=="/auth/v1/signup" or path=="/auth/v1/token":
            b=json.loads(r.post_data or "{}")
            if path.endswith("signup"):
                if b["email"] in srv.users: js(400,{"msg":"User already registered"});return
                srv.n+=1;srv.users[b["email"]]=(("u%d"%srv.n),b["password"])
            if b["email"] not in srv.users or srv.users[b["email"]][1]!=b["password"]: js(400,{"error_description":"Invalid login credentials"});return
            i=srv.users[b["email"]][0]
            js(200,{"access_token":"tok:"+i,"refresh_token":"r","expires_in":3600,"user":{"id":i,"email":b["email"]}});return
        if path=="/rest/v1/entitlements":
            if not uid: js(401,{});return
            e=getattr(srv,"ent",{}).get(uid);js(200,[e] if e else []);return
        if path=="/rest/v1/user_data":
            if not uid: js(401,{"message":"no"});return
            flt=q.get("user_id",[""])[0].replace("eq.","")
            if r.method=="GET":
                if srv.delay:
                    import time as _t;_t.sleep(srv.delay)
                row=srv.rows.get(uid) if flt==uid else None
                if getattr(srv,"hold",None)==uid:
                    srv.held=(route,[row] if row else []);srv.hold=None;return
                js(200,[row] if row else []);return
            if r.method=="DELETE":
                if flt==uid: srv.rows.pop(uid,None)
                js(204 if False else 200,[]);return
            prefer=hd.get("prefer","")
            if r.method=="POST":
                b=json.loads(r.post_data)
                if b["user_id"]!=uid: js(403,{"message":"rls"});return
                if "ignore-duplicates" in prefer and uid in srv.rows: js(200,[]);return
                row={"user_id":uid,"data":b["data"],"updated_at":b.get("updated_at") or srv.now()}
                srv.rows[uid]=row
                if srv.dropnext: srv.dropnext-=1;route.abort();return
                js(200,[row]);return
            if r.method=="PATCH":
                b=json.loads(r.post_data)
                if getattr(srv,"delaypatch",0): time.sleep(srv.delaypatch)  # envio lento: o app continua rodando enquanto espera
                if flt!=uid or uid not in srv.rows: js(200,[]);return
                cond=q.get("updated_at",[None])[0]
                if cond is not None and cond.replace("eq.","")!=srv.rows[uid]["updated_at"]: js(200,[]);return
                row=srv.rows[uid];row["data"]=b["data"];row["updated_at"]=b.get("updated_at") or srv.now()
                if srv.dropnext: srv.dropnext-=1;route.abort();return
                js(200,[row]);return
        if path=="/functions/v1/delete-account":
            if srv.delfail: js(500,{});return
            if uid:
                srv.rows.pop(uid,None)
                for e,(i,p) in list(srv.users.items()):
                    if i==uid: srv.users.pop(e)
                js(200,{"ok":1});return
            js(401,{});return
        route.continue_()
    ctx.route(SB+"/**",h)
