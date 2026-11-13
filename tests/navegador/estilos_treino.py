import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from comum import URL,SEED,lancar,html_pago
from playwright.sync_api import sync_playwright
F=[]
def A(c,m):
    print(("OK   " if c else "FAIL ")+m)
    if not c:F.append(m)
with sync_playwright() as p:
    b=lancar(p);pg=b.new_page(viewport={"width":390,"height":844})
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL);pg.evaluate(SEED);pg.reload();pg.evaluate("document.getElementById('sdo')&&sdClose()")
    nomes=lambda:pg.evaluate("(()=>{const PP=plansFor(P());return PP.keys.map(k=>PP.P[k][0])})()")
    # todos os modelos usam exercícios que existem e servem para o local
    bad=pg.evaluate("""(()=>{const out=[];for(const loc of ['gym','cond','home','cal'])for(const st of Object.keys(STY)){if(st==='auto')continue;const p={...P(),loc};const sp=styPlan(p,st);if(!sp||!sp.length){out.push(loc+'/'+st+' vazio');continue}
      sp.forEach(([n,ex])=>ex.forEach(x=>{if(!EX[x])out.push(loc+'/'+st+': '+x+' não existe');else if(loc==='cal'&&!calOk(x))out.push('cal/'+st+': '+x);else if((loc==='home'||loc==='cond')&&!(BW.has(x)||HOMEOK.has(x)))out.push(loc+'/'+st+': '+x)}))}return out})()""")
    A(not bad,"modelos válidos para academia, condomínio, casa e calistenia "+str(bad[:4]))
    auto=nomes();A(pg.evaluate("styOf(P())")=="auto","padrão automático")
    # Premium (liberado no teste): escolher Push/Pull/Legs com 4 dias
    pg.evaluate("P().days=4;save();PFO.trn=true;tab='perfil';render()")
    pg.select_option("#psplit","ppl");A("Empurrar" in pg.inner_text("#psplith") or "puxar" in pg.inner_text("#psplith"),"descrição do estilo aparece")
    pg.click("#spn-trn >> text=Salvar e calcular")
    n=nomes();A(n[:3]==["Empurrar A","Puxar A","Pernas A"] and len(n)==6,"Push/Pull/Legs mesmo com 4 dias: "+str(n))
    A(pg.evaluate("(()=>{const PP=plansFor(P());return nextKey(pid(),PP.keys,PP)})()")=="A","depois de trocar, começa no primeiro dia")
    pg.evaluate("tab='treino';render()");A("Push / Pull / Legs" in pg.inner_text("#app"),"estilo aparece no Treino")
    for st,exp0 in [("arnold","Peito e costas"),("ulf","Superior"),("fb","Corpo inteiro A"),("five","Peito e tríceps"),("ul","Superior A")]:
        pg.evaluate("tab='perfil';PFO.trn=true;render()");pg.select_option("#psplit",st);pg.click("#spn-trn >> text=Salvar e calcular");A(nomes()[0]==exp0,f"{st} começa por {exp0}")
    pg.evaluate("tab='perfil';PFO.trn=true;render()");pg.select_option("#psplit","ppl");pg.click("#spn-trn >> text=Salvar e calcular")
    pg.reload();pg.evaluate("document.getElementById('sdo')&&sdClose()");A(nomes()[0]=="Empurrar A","estilo continua após reabrir")
    pg.evaluate("P().loc='home';save()");A(nomes()==["Empurrar","Puxar","Pernas"],"Push/Pull/Legs em casa com exercícios de casa")
    pg.evaluate("P().rtOn=true;P().rt=[{id:'r1',n:'Meu dia',ex:[['Supino reto',3,'10']]}];save()");A(nomes()==["Meu dia"],"Minha rotina continua tendo prioridade")
    pg.close()
    # Plano grátis (cobrança ligada): só automático; estilo guardado volta se assinar
    pg=b.new_page(viewport={"width":390,"height":844});pg.goto(html_pago());pg.evaluate(SEED);pg.evaluate("P().split='ppl';P().days=4;save()");pg.reload();pg.evaluate("document.getElementById('sdo')&&sdClose()")
    A(pg.evaluate("styOf(P())")=="auto" and nomes()[0]=="Superior A","grátis usa o automático (estilo guardado não vale)")
    pg.evaluate("PFO.trn=true;tab='perfil';render()");pg.select_option("#psplit","arnold")
    A("Disponível no Premium" in pg.inner_text("#psplith"),"grátis vê convite ao escolher outro estilo")
    pg.click("#spn-trn >> text=Salvar e calcular");A(pg.evaluate("P().split")=="ppl","salvar no grátis não troca o estilo guardado")
    A(not errs,"sem erros JS "+str(errs[:2]))
print("FALHAS:",F)
