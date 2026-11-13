# Falhas de armazenamento e rede, e dois aparelhos na mesma conta (servidor Supabase simulado).
import sys,os,json;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from comum import URL,lancar
from servidor_falso import Srv,install
from playwright.sync_api import sync_playwright
F=[]
def A(c,m):
    print(("OK   " if c else "FAIL ")+m)
    if not c:F.append(m)
# Simula armazenamento cheio: limite total de caracteres, ou falha só em uma chave.
QUOTA="""(()=>{const set=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){
  if(window._failKey&&k===window._failKey){const e=new Error('cheio');e.name='QuotaExceededError';throw e}
  if(window._quota){let t=0;for(let i=0;i<this.length;i++){const kk=this.key(i);if(kk!==k)t+=kk.length+(this.getItem(kk)||'').length}t+=k.length+String(v).length;if(t>window._quota){const e=new Error('cheio');e.name='QuotaExceededError';throw e}}
  return set.call(this,k,v)}})()"""
def dev(b,srv,novo=False):
    # novo=True: aparelho sem dados (só abriu o app); False: já tem perfil preenchido
    c=b.new_context(viewport={"width":390,"height":844});install(c,srv);pg=c.new_page();pg.add_init_script(QUOTA)
    pg.goto(URL);pg.evaluate("S.seen=true;save()" if novo else "S.seen=true;Object.assign(S.people[0],{name:'Ana',set:true});save()");return c,pg
def login(pg,em,up=False):
    pg.evaluate("PFO.cta=true;tab='perfil';render()");pg.fill("#cem",em);pg.fill("#cpw","senha1234")
    if up: pg.check("#ccn")
    pg.evaluate(f"cAuth({1 if up else 0})");pg.wait_for_timeout(800)
add=lambda pg,n,k=100:pg.evaluate(f"push({{m:'Almoço',n:'{n}',k:{k},p:1,c:1,f:1}})")
loc=lambda pg:sorted(x['n'] for d in pg.evaluate("S")['log'].values() for l in d.values() for x in l)
srvn=lambda srv,uid:sorted(x['n'] for d in srv.rows[uid]['data']['log'].values() for l in d.values() for x in l)
sync=lambda pg:(pg.evaluate("cPull(0)"),pg.wait_for_timeout(400))
used=lambda pg:pg.evaluate("(()=>{let t=0;for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);t+=k.length+localStorage.getItem(k).length}return t})()")
with sync_playwright() as p:
    b=lancar(p);srv=Srv()
    # ---------- armazenamento cheio ----------
    c1,d1=dev(b,srv);login(d1,"a@x.com",up=True);uid=srv.users["a@x.com"][0];add(d1,"Arroz");d1.wait_for_timeout(3600)
    A(srvn(srv,uid)==["Arroz"],"base: registro enviado")
    antes=d1.evaluate("localStorage.getItem('gymcal2')")
    d1.evaluate("window._failKey='gymcal2'");add(d1,"Feijão")
    A(d1.evaluate("lsErr") and d1.locator("text=Não consegui salvar neste aparelho").count()==1,"cheio: avisa na tela")
    A(d1.evaluate("localStorage.getItem('gymcal2')")==antes,"cheio: cópia salva continua íntegra (não corrompe)")
    A("Feijão" in loc(d1),"cheio: o registro continua na memória")
    d1.evaluate("window._failKey=null");add(d1,"Ovo")
    A(not d1.evaluate("lsErr") and sorted(x['n'] for d in json.loads(d1.evaluate("localStorage.getItem('gymcal2')"))['log'].values() for l in d.values() for x in l)==["Arroz","Feijão","Ovo"],"liberou espaço: tudo salvo junto")
    d1.wait_for_timeout(3600)
    # atualização vinda da nuvem com pouco espaço para cópias de segurança
    c2,d2=dev(b,srv,novo=True);login(d2,"a@x.com");d2.wait_for_timeout(500)
    A(loc(d2)==["Arroz","Feijão","Ovo"],"segundo aparelho recebe os dados")
    add(d1,"Banana");d1.wait_for_timeout(3600)
    d2.evaluate("localStorage.setItem('gymcal_stash',JSON.stringify([{t:1,why:'x',d:S},{t:2,why:'y',d:S}]))")
    d2.evaluate(f"window._quota={used(d2)+300}")  # cabe 1 cópia, não cabem 3
    sync(d2);    A(loc(d2)==["Arroz","Banana","Feijão","Ovo"] and d2.evaluate("JSON.parse(localStorage.getItem('gymcal_stash')).length")==1,"pouco espaço: atualiza guardando 1 cópia em vez de 3")
    add(d1,"Maçã");d1.wait_for_timeout(3600)
    d2.evaluate(f"window._quota={used(d2)-200}");antes2=loc(d2);sync(d2)
    A(loc(d2)==antes2 and "cópia de segurança" in d2.evaluate("cl.st"),"sem espaço nem para 1 cópia: não substitui e avisa")
    d2.evaluate("window._quota=0");sync(d2);A("Maçã" in loc(d2) and not d2.evaluate("lsErr"),"liberou espaço: atualização entra e o aviso some")
    # falha ao gravar a versão da nuvem: volta ao estado anterior
    add(d1,"Pera");d1.wait_for_timeout(3600)
    antes3=loc(d2);d2.evaluate("window._failKey='gymcal2'");sync(d2)
    A(loc(d2)==antes3 and "Armazenamento cheio" in d2.evaluate("cl.st"),"não conseguiu gravar a nuvem: mantém a versão local na tela")
    d2.evaluate("window._failKey=null");sync(d2);A("Pera" in loc(d2),"depois entra normalmente")
    # restaurar um backup desta conta sem espaço para guardar a cópia atual
    bk=d2.evaluate("(()=>{const c=JSON.parse(JSON.stringify(S)),l=c.log[pid()];(l[dayKey()]=l[dayKey()]||[]).push({m:'Almoço',n:'Do backup',k:10,p:1,c:1,f:1});c._bk={uid:A.uid};return JSON.stringify(c)})()");st0=d2.evaluate("JSON.stringify(S)");d2.evaluate("window._failKey='gymcal_stash';PFO.bak=true;tab='perfil';render()")
    d2.fill("#bk",bk);d2.click("button:text-is('Restaurar')");d2.wait_for_timeout(200)
    A(d2.evaluate("JSON.stringify(S)")==st0 and "Do backup" not in loc(d2),"restaurar sem espaço para cópia: não mexe em nada");d2.evaluate("window._failKey=null")
    d2.fill("#bk",bk);d2.click("button:text-is('Restaurar')");d2.wait_for_timeout(200);A("Do backup" in loc(d2),"com espaço: o backup é restaurado")
    # ---------- rede ----------
    srv.fail=True;add(d1,"Uva");d1.wait_for_timeout(3600)
    A("Uva" in loc(d1) and "Uva" not in srvn(srv,uid) and "Sem conexão" in d1.evaluate("cl.st"),"sem rede: fica no aparelho e avisa")
    srv.fail=False;d1.evaluate("cPushSafe()");d1.wait_for_timeout(500);A("Uva" in srvn(srv,uid),"rede voltou: envia")
    # resposta perdida: o servidor gravou, mas o aparelho não recebeu a confirmação
    srv.dropnext=1;add(d1,"Kiwi");d1.wait_for_timeout(3600);d1.evaluate("cPushSafe().catch(()=>{})");d1.wait_for_timeout(800)
    A(srvn(srv,uid).count("Kiwi")==1 and loc(d1).count("Kiwi")==1,"resposta perdida: sem duplicar")
    # editar durante o envio
    # editar enquanto o envio está a caminho (sem o agendamento normal do save, para testar só a correção nova)
    srv.delaypatch=0.8
    d1.evaluate("setTimeout(()=>{const l=S.log[pid()];(l[dayKey()]=l[dayKey()]||[]).push({m:'Almoço',n:'Durante',k:50,p:1,c:1,f:1});save(true)},150);cPush().catch(()=>{})")
    d1.wait_for_timeout(1200);srv.delaypatch=0
    A("Durante" not in srvn(srv,uid) and d1.evaluate("cl.confirmedPayload!==JSON.stringify(S)"),"envio lento: o servidor recebeu a versão anterior à edição")
    d1.wait_for_timeout(3800)
    A("Durante" in srvn(srv,uid) and d1.evaluate("cl.confirmedPayload===JSON.stringify(S)"),"alteração feita durante o envio é enviada logo depois")
    # ---------- dois aparelhos ----------
    sync(d2);base=loc(d2)
    srv.fail=True;add(d2,"Offline B");d2.wait_for_timeout(3600);srv.fail=False
    add(d1,"Online A");d1.wait_for_timeout(3600)
    sync(d2);d2.wait_for_timeout(3800);sync(d1)
    A(loc(d1)==loc(d2)==srvn(srv,uid) and loc(d1).count("Offline B")==1 and loc(d1).count("Online A")==1,"dois aparelhos com alterações diferentes: combina sem perder nem duplicar")
    # apagar em um aparelho e registrar no outro: o apagado não volta
    sync(d1);sync(d2)
    d1.evaluate("(()=>{const l=S.log[pid()];for(const d in l)l[d]=l[d].filter(x=>x.n!=='Uva');save()})()");d1.wait_for_timeout(3600)
    srv.fail=True;add(d2,"Pão");d2.wait_for_timeout(3600);srv.fail=False;sync(d2);d2.wait_for_timeout(3800);sync(d1)
    A("Uva" not in srvn(srv,uid) and "Pão" in srvn(srv,uid) and loc(d1)==loc(d2),"apagou em um, registrou no outro: o apagado não volta e o novo entra")
    # o mesmo alimento registrado nos dois aparelhos sem internet (duas porções de verdade)
    srvb=lambda:sum(1 for d in srv.rows[uid]['data']['log'].values() for l in d.values() for x in l if x['n']=='Banana' and x['k']==90)
    srv.fail=True;add(d1,"Banana",90);add(d2,"Banana",90);add(d2,"Café",5);d2.wait_for_timeout(3600);srv.fail=False
    d1.evaluate("cPushSafe().catch(()=>{})");d1.wait_for_timeout(600);sync(d2);d2.wait_for_timeout(3800);sync(d1)
    A(srvb()==2 and loc(d1)==loc(d2),"mesmo alimento registrado nos dois (e outra mudança): mantém os dois registros")
    # limitação: se os dois aparelhos ficarem com o conteúdo inteiro idêntico, o app trata como a mesma alteração
    srv.fail=True;add(d1,"Iogurte",80);add(d2,"Iogurte",80);d2.wait_for_timeout(3600);srv.fail=False
    d1.evaluate("cPushSafe().catch(()=>{})");d1.wait_for_timeout(600);sync(d2);d2.wait_for_timeout(500);sync(d1)
    print("     conteúdo idêntico nos dois aparelhos -> Iogurte na nuvem:",srvn(srv,uid).count("Iogurte"),"(limitação conhecida: igual ao caso de resposta perdida, fica 1)")
    # mesmo registro editado nos dois (limitação conhecida)
    d1.evaluate("(()=>{const x=Object.values(S.log[pid()]).flat().find(x=>x.n==='Arroz');x.k=200;save()})()");d1.wait_for_timeout(3600)
    d2.evaluate("(()=>{const x=Object.values(S.log[pid()]).flat().find(x=>x.n==='Arroz');x.k=300;save()})()")
    sync(d2);d2.wait_for_timeout(3800);ks=sorted(x['k'] for d in srv.rows[uid]['data']['log'].values() for l in d.values() for x in l if x['n']=='Arroz')
    print("     mesmo item editado nos dois aparelhos ->",ks,"(limitação conhecida: a soma por conteúdo mantém as duas versões)")
    # sem cópia de base: pede decisão em vez de combinar sozinho
    sync(d1);sync(d2);srv.fail=True;add(d2,"Sem base");d2.wait_for_timeout(3600);srv.fail=False;add(d1,"Outro");d1.wait_for_timeout(3600)
    d2.evaluate("localStorage.removeItem('gymcal_snap')");sync(d2)
    A(bool(d2.evaluate("cl.ask&&cl.ask.noBase")) and "Sem base" in loc(d2) and "Outro" not in loc(d2),"sem cópia de base: pergunta antes de combinar e não mexe em nada")
    d2.evaluate("cUse(2)");d2.wait_for_timeout(800)
    A("Sem base" in srvn(srv,uid) and "Outro" in srvn(srv,uid) and loc(d2)==srvn(srv,uid),"sem cópia de base, escolheu Combinar: fica com os dois lados")
    # sair e apagar sem internet não apaga
    srv.fail=True;add(d1,"Último");d1.evaluate("PFO.cta=true;tab='perfil';render()");d1.evaluate("cOut(true)");d1.evaluate("cOut(true)");d1.wait_for_timeout(1500)
    A("Último" in loc(d1) and d1.evaluate("!!localStorage.getItem('gymcal2')"),"sair e limpar sem internet: não apaga");srv.fail=False
print("FALHAS:",F)
