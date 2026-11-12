import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from comum import URL,SEED,lancar
from playwright.sync_api import sync_playwright
import json
F=[]
def A(c,m):
    print(("OK   " if c else "FAIL ")+m)
    if not c:F.append(m)
with sync_playwright() as p:
    b=lancar(p);pg=b.new_page(viewport={"width":390,"height":844})
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL);pg.evaluate(SEED);base=pg.evaluate("localStorage.getItem('gymcal2')")
    cases=[("peso 20","d.people[0].w=20"),("kcal como texto","d.log[d.people[0].id][Object.keys(d.log[d.people[0].id])[0]][0].k='350'"),
      ("exercício com aspas","d.last[d.people[0].id]={\"Farmer's walk\":{s:[{w:10,r:10}]}}"),("cardio 400 min","d.cardio[d.people[0].id]={[Object.keys(d.log[d.people[0].id])[0]]:[{n:'Corrida',min:400,k:900}]}"),
      ("peso salvo como texto","d.wt[d.people[0].id][Object.keys(d.wt[d.people[0].id])[0]]='77.5'"),("série com 10 séries","d.people[0].rt=[{id:'r1',n:'A',ex:[['Supino reto',10,'8-10']]}]"),
      ("idade como texto","d.people[0].age='28'"),("data inválida","(d.water[d.people[0].id]=d.water[d.people[0].id]||{})['ontem']=3"),("NaN no treino","d.wk[d.people[0].id][0].vl=null;d.wk[d.people[0].id][0].min='abc'")]
    for name,mut in cases:
        raw=pg.evaluate("s=>{const d=JSON.parse(s);%s;const r=JSON.stringify(d);localStorage.clear();localStorage.setItem('gymcal2',r);return r}"%mut,base)
        pg.reload();pg.wait_for_timeout(600)
        le=pg.evaluate("loadError");nlog=pg.evaluate("Object.values(S.log[S.people[0].id]||{}).flat().length");copy=pg.evaluate("localStorage.getItem('gymcal2_copia')")==raw
        ok=pg.evaluate("(()=>{try{validateState(JSON.parse(localStorage.getItem('gymcal2')));return true}catch(e){return false}})()")
        A(not le and nlog>=14 and copy and ok and pg.evaluate("S.people[0].name")=="Charles","%s: abre, diário mantido (%d itens), cópia guardada, salvo válido"%(name,nlog))
    # JSON quebrado continua indo para a recuperação sem apagar
    pg.evaluate("localStorage.clear();localStorage.setItem('gymcal2','{quebrado')");pg.reload();pg.wait_for_timeout(300)
    A(pg.evaluate("loadError") and pg.evaluate("localStorage.getItem('gymcal2')")=="{quebrado","JSON quebrado: tela de recuperação, original intacto")
    # backup antigo com cardio 400 min é aceito; malicioso continua recusado
    pg.evaluate("s=>{localStorage.clear();localStorage.setItem('gymcal2',s)}",base);pg.reload();pg.evaluate("document.getElementById('sdo')&&sdClose();PFO.bak=true;tab='perfil';render()")
    old=json.loads(base);pid=old["people"][0]["id"];old["cardio"][pid]={list(old["log"][pid].keys())[0]:[{"n":"Corrida","min":400,"k":900}]};old["people"][0]["name"]="Antigo"
    pg.fill("#bk",json.dumps(old));pg.click("button:text-is('Restaurar')");pg.wait_for_timeout(200)
    A(pg.evaluate("S.people[0].name")=="Antigo","backup antigo fora do padrão é restaurado")
    bad=json.loads(base);bad["people"][0]["w"]="<img src=x onerror=alert(1)>";pg.evaluate("PFO.bak=true;render()");st=pg.evaluate("JSON.stringify(S)")
    pg.fill("#bk",json.dumps(bad));pg.click("button:text-is('Restaurar')");pg.wait_for_timeout(200)
    A(pg.evaluate("JSON.stringify(S)")==st,"backup malicioso continua recusado")
    A(not errs,"sem erros JS "+str(errs[:2]))
print("FALHAS:",F)
