# Foco do treino "Mais pernas e glúteo": planos válidos em todos os locais e dias, mais volume de inferiores, tela e regras.
import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from comum import URL,lancar
from playwright.sync_api import sync_playwright
F=[]
def A(c,m):
    print(("OK   " if c else "FAIL ")+m)
    if not c:F.append(m)
INF="['Quadríceps','Glúteos','Posterior de coxa','Panturrilha']"
with sync_playwright() as p:
    b=lancar(p);pg=b.new_page(viewport={"width":390,"height":844});errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL);pg.evaluate("S.seen=true;Object.assign(S.people[0],{name:'Ana',set:true,sex:'f',w:60,h:163,age:24});save()")
    # 1. todos os locais e dias
    for loc in ["gym","cond","home","cal"]:
        for d in range(2,7):
            r=pg.evaluate("""([loc,d])=>{const p=P();Object.assign(p,{loc,days:d,split:'auto',rtOn:false,focus:'glu'});const PP=plansFor(p),hm=isCal(p)?2:isHm(p)?1:0;
              const bad=[],dup=[],nomes=PP.keys.map(k=>PP.P[k][0]);PP.keys.forEach(k=>{const ex=PP.P[k][1].map(e=>e[0]);if(new Set(ex).size!==ex.length)dup.push(k);ex.forEach(n=>{if(!EX[n]||(hm===2&&!calOk(n))||(hm===1&&!(BW.has(n)||HOMEOK.has(n))))bad.push(n)})});
              const frac=PP2=>{let t=0,l=0,g=0;PP2.keys.forEach(k=>PP2.P[k][1].forEach(e=>{const x=EX[e[0]];t+=e[1];if(%s.includes(x.p[0]))l+=e[1];if(x.p.includes('Glúteos'))g+=e[1]}));return [l/t,g/t]};
              const f1=frac(PP);p.focus='';const f0=frac(plansFor(p));p.focus='glu';return {n:PP.keys.length,nomes,bad,dup,f1,f0}}"""%INF,[loc,d])
            A(r["n"]==d and not r["bad"] and not r["dup"] and r["f1"][0]>r["f0"][0] and r["f1"][1]>r["f0"][1],
              f"{loc} {d} dias: {r['n']} treinos {r['nomes']} · inferiores {round(r['f0'][0]*100)}% → {round(r['f1'][0]*100)}%, glúteo {round(r['f0'][1]*100)}% → {round(r['f1'][1]*100)}% {r['bad']}{r['dup']}")
    # 2. tela: escolher o foco no Perfil
    pg.evaluate("Object.assign(P(),{loc:'gym',days:5,focus:'',split:'auto'});S.wk[pid()]=[{d:'2026-11-01',plan:'C',n:1,st:[3],ex:['Agachamento'],det:[]}];save();PFO.trn=true;tab='perfil';render()")
    A(pg.input_value("#pfoc")=="" and "mesma medida" in pg.inner_text("#pfoch"),"padrão: corpo todo por igual")
    pg.select_option("#pfoc","glu");A("pernas e glúteo, sem largar a parte de cima" in pg.inner_text("#pfoch"),"ao escolher, o texto explica o foco")
    pg.click("#spn-trn >> text=Salvar e calcular");pg.wait_for_timeout(200)
    A(pg.evaluate("P().focus")=="glu" and pg.evaluate("P().splitFrom")==pg.evaluate("dk(new Date())"),"salvou o foco e recomeça a sequência")
    pg.evaluate("tab='treino';plan='';render();scrollTo(0,0)");pg.wait_for_timeout(200);t=pg.inner_text("#app")
    A("Foco pernas e glúteo" in t and "Pernas e glúteo" in t,"Treino mostra o foco e começa por Pernas e glúteo")
    A("Sequência de 5 treinos" in t,"a linha da sequência continua certa")
    pg.evaluate("tab='perfil';render()");A("Pernas e glúteo" in pg.inner_text(".srw:has-text('Preferências de treino')"),"resumo do Perfil mostra o foco")
    # 3. com estilo Premium escolhido, o foco não muda os treinos e avisa
    pg.evaluate("P().split='ppl';save();PFO.trn=true;render()")
    A("vale no estilo Automático" in pg.inner_text("#pfoch") and pg.evaluate("plansFor(P()).P.A[0]")=="Empurrar A","com Push/Pull/Legs o foco não muda os treinos e avisa")
    # 4. "Minha rotina" continua com prioridade
    pg.evaluate("P().split='auto';reStart();RE[0].n='Meu treino';reSave()");A(pg.evaluate("P().rtOn") and pg.evaluate("plansFor(P()).P.A[0]")=="Meu treino" and bool(pg.evaluate("plansFor(P()).P.A[3]")),"Minha rotina continua tendo prioridade (começa como cópia do plano com foco)")
    pg.evaluate("P().rtOn=false;save()")
    # 5. voltar para corpo todo
    pg.evaluate("PFO.trn=true;tab='perfil';render()");pg.select_option("#pfoc","");pg.click("#spn-trn >> text=Salvar e calcular");pg.wait_for_timeout(200)
    A(pg.evaluate("P().focus")=="" and pg.evaluate("plansFor(P()).P.A[0]")=="Peito e tríceps","voltar para corpo todo restaura o plano de antes")
    # 6. dados com o campo novo passam na validação, na combinação e no backup
    A(pg.evaluate("(()=>{P().focus='glu';save();try{validateState(JSON.parse(localStorage.getItem('gymcal2')));return true}catch(e){return false}})()"),"dados com foco são válidos")
    pg.reload();pg.wait_for_timeout(300);A(pg.evaluate("P().focus")=="glu" and not pg.evaluate("loadError"),"foco continua ao reabrir")
    A(pg.evaluate("(()=>{const b=JSON.parse(JSON.stringify(S));b.people[0].focus='';const l=JSON.parse(JSON.stringify(b)),r=JSON.parse(JSON.stringify(b));l.people[0].focus='glu';l.ts=5;r.ts=6;r.people[0].days=3;const m=mergeS(l,r,b);return m.people[0].focus==='glu'&&m.people[0].days===3})()"),"foco mudado num aparelho e dias no outro: os dois ficam")
    # 7. primeiro cadastro também oferece o foco
    q=b.new_page(viewport={"width":390,"height":844});q.goto(URL);q.click("text=Começar");q.wait_for_timeout(200)
    A(q.locator("#pfoc").is_visible(),"primeiro cadastro oferece o foco");q.close()
    A(not errs,"sem erros JS "+str(errs[:2]))
    b.close()
print("FALHAS:",F)
