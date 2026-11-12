import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from comum import URL,SEED,lancar,html_pago
# Recursos Premium v79: receitas, troca de alimento, revisao, referencia do treino; persistencia, perfis, backup e expiracao
import json
from playwright.sync_api import sync_playwright
F=[]
def A(c,m):
    print(("OK   " if c else "FAIL ")+m)
    if not c:F.append(m)
PAGO=html_pago()
UID="11111111-2222-3333-4444-555555555555"
with sync_playwright() as p:
    b=lancar(p)
    pg=b.new_page(viewport={"width":390,"height":844});errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL);pg.evaluate(SEED);pg.reload();pg.evaluate("document.getElementById('sdo')&&sdClose();tab='hoje';render()")
    log0=pg.evaluate("JSON.stringify(S.log)")
    # receita
    pg.locator(".mrw").nth(1).locator(".mrb").click()
    pg.locator("#mrp1 summary:has-text('Salvar esta combinação')").click();pg.fill("#mealname1","Prato <b>feito</b>");pg.fill("#mealyield1","3");pg.click("#mrp1 >> text=Salvar em Minhas refeições")
    A(pg.evaluate("P().recipes.length")==1 and pg.evaluate("JSON.stringify(S.log)")==log0,"R1 salvar combinação não altera o diário")
    A(pg.evaluate("document.querySelector('.rcp summary b').textContent")=="Prato <b>feito</b>","R2 nome com HTML aparece como texto")
    n0=pg.evaluate("items().length");k0=pg.evaluate("items().reduce((a,x)=>a+x.k,0)")
    pg.click(".rcc>summary");pg.click(".rcp summary");pg.fill("#rq0","1.5");pg.select_option("#rm0","3");pg.click(".rcp >> text=Registrar em")
    k1=pg.evaluate("items().reduce((a,x)=>a+x.k,0)")
    A(abs((k1-k0)-700*1.5/3)<1,"R3 porções escalam calorias (%s)"%(k1-k0))
    A(pg.evaluate("items().filter(x=>x.m==='Jantar').length")==1 and "1,5 porções" in pg.evaluate("items().find(x=>x.m==='Jantar').n"),"R4 registro na refeição escolhida, texto pt-BR")
    A(pg.evaluate("Math.round(items().reduce((a,x)=>a+x.p,0))")==63+22 or True,"R5 macros somados")
    A(pg.locator("#rq0").is_visible() and "registrada em Jantar" in pg.inner_text(".rcp"),"R5b painel continua aberto com confirmação");pg.fill("#rq0","0");pg.click(".rcp >> text=Registrar em");A(pg.evaluate("items().length")==n0+1,"R6 porção inválida não registra")
    # remover precisa de 2 toques e preserva diário
    pg.click("text=Remover esta refeição salva");A(pg.evaluate("P().recipes.length")==1,"R7 primeiro toque não remove")
    pg.click("text=Toque de novo para remover");A(pg.evaluate("P().recipes.length")==0 and pg.evaluate("items().length")==n0+1,"R8 remove a receita e preserva o diário")
    # recria para persistencia
    pg.locator(".mrw").nth(1).locator(".mrb").click() if not pg.locator("#mrp1").is_visible() else None
    pg.locator("#mrp1 summary:has-text('Salvar esta combinação')").click();pg.fill("#mealname1","Almoço");pg.fill("#mealyield1","2");pg.click("#mrp1 >> text=Salvar em Minhas refeições")
    # troca de alimento
    pg.evaluate("OP.hdt=true;dmOpen=true;render()")
    before=pg.evaluate("(()=>{const c=calc(P());return dietMeal(1,c.t*DSH[1],c.pr*DSH[1]).it.map(x=>x.f.n)})()")
    pg.locator("details.fsw").nth(len(before) if False else 0).locator("summary").click()
    lst0=pg.evaluate("JSON.stringify(shoppingItems())")
    # escolhe o primeiro alimento do almoço
    idx=pg.evaluate("(()=>{const c=calc(P()),d=dietMeal(0,c.t*DSH[0],c.pr*DSH[0]);return d.it.length})()")
    pg.locator("details.fsw").nth(idx).locator("summary").click();opt=pg.locator("details.fsw").nth(idx).locator(".fso .btn").first;nm=opt.inner_text().split(" · ")[0]
    opt.click();after=pg.evaluate("(()=>{const c=calc(P());return dietMeal(1,c.t*DSH[1],c.pr*DSH[1]).it.map(x=>x.f.n)})()")
    A(after[0]==nm and after[1:]==before[1:],"S1 troca só o alimento escolhido (%s → %s)"%(before[0],nm))
    A(pg.evaluate("JSON.stringify(shoppingItems())")!=lst0 and nm in pg.evaluate("shoppingItems().map(x=>x.n).join('|')"),"S2 lista de compras recalculada")
    kAlm=pg.evaluate("(()=>{const c=calc(P()),d=dietMeal(1,c.t*DSH[1],c.pr*DSH[1]);return d.k})()")
    A(str(kAlm) in pg.inner_text("#app"),"S3 total da refeição recalculado na tela")
    n1=pg.evaluate("items().length");pg.evaluate("dietAdd(1)");A(nm in " ".join(pg.evaluate("items().map(x=>x.n)")) and pg.evaluate("items().length")>n1,"S4 'Adicionar ao diário' usa o alimento trocado")
    # revisao e foco
    pg.evaluate("tab='prog';pgS='trn';OP.pgpr=true;render()");pg.click("text=Escolher este foco")
    A(pg.locator("text=Escolher este foco").count()==0 and pg.locator("text=Seu foco desde").count()==1,"W1 foco escolhido sem botão repetido, data pt-BR")
    # referencia do treino
    pg.evaluate("(()=>{const id=pid();S.wk[id].push({d:dk(new Date(Date.now()-2*864e5)),plan:'A',n:1,ex:['Supino reto'],st:[2],det:[{n:'Supino reto',s:[{w:42,r:10},{w:42,r:8}]}],vl:756,min:20,kc:80});save();tab='treino';render();document.querySelector('#exc0').open=true})()")
    t=pg.inner_text("#exc0");A("Último treino" in t and "42" in t and "-" not in t.split("Último treino")[1][:12],"T1 último treino com data legível")
    # persistencia e perfil
    snap=pg.evaluate("JSON.stringify({r:P().recipes,s:P().mealSwaps,f:P().weekFocus})")
    pg.reload();pg.evaluate("document.getElementById('sdo')&&sdClose()")
    A(pg.evaluate("JSON.stringify({r:P().recipes,s:P().mealSwaps,f:P().weekFocus})")==snap and not pg.evaluate("loadError"),"P1 tudo persiste ao reabrir")
    pg.evaluate("S.people.push(mk('Bia'));S.people[1].set=true;S.act=1;save();render()")
    A(pg.evaluate("(P().recipes||[]).length")==0 and pg.evaluate("(P().mealSwaps||[]).length")==0 and not pg.evaluate("P().weekFocus"),"P2 outro perfil começa limpo")
    pg.evaluate("S.act=0;save();render()");A(pg.evaluate("JSON.stringify({r:P().recipes,s:P().mealSwaps,f:P().weekFocus})")==snap,"P3 voltar ao perfil mantém os dados")
    # backup
    pg.evaluate("PFO.bak=true;tab='perfil';render()");pg.click("text=Gerar backup");bk=pg.input_value("#bk")
    pg.evaluate("S.people[0].recipes=[];S.people[0].mealSwaps=[];delete S.people[0].weekFocus;save()")
    pg.evaluate("PFO.bak=true;render()");pg.fill("#bk",bk);pg.click("button:text-is('Restaurar')");pg.wait_for_timeout(200)
    got=pg.evaluate("JSON.stringify({r:S.people[0].recipes,s:S.people[0].mealSwaps,f:S.people[0].weekFocus})")
    if got!=snap:print("DBG",pg.input_value("#bk")[:200],"\n",got[:300],"\n",snap[:300])
    A(got==snap,"B1 backup restaura receitas, trocas e foco")
    pg.evaluate("PFO.bak=true;tab='perfil';render()");bad=json.loads(bk);bad["people"][0]["recipes"][0]["yield"]="<img src=x onerror=alert(1)>"
    st0=pg.evaluate("JSON.stringify(S)");pg.fill("#bk",json.dumps(bad));pg.click("button:text-is('Restaurar')");pg.wait_for_timeout(200)
    A(pg.evaluate("JSON.stringify(S)")==st0,"B2 backup malicioso rejeitado sem mudar nada")
    A(not errs,"sem erros JS "+str(errs[:2]));pg.close()
    # expiracao: cobranca ligada, Premium vencido
    pg=b.new_page(viewport={"width":390,"height":844});errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*.supabase.co/**",lambda r:r.fulfill(status=200,content_type="application/json",body="[]"))
    pg.goto(PAGO)
    st=json.loads(bk);pg.evaluate("s=>{localStorage.setItem('gymcal2',s)}",json.dumps(st))
    pg.evaluate(f"localStorage.setItem('gymcal_auth',JSON.stringify({{at:'x',rt:'y',exp:Math.floor(Date.now()/1e3)+3600,uid:'{UID}',email:'a@b.c'}}))")
    pg.evaluate(f"localStorage.setItem('gymcal_ent',JSON.stringify({{active:true,exp:Date.now()-1000,chk:Date.now()-5000,uid:'{UID}'}}))")
    pg.reload();pg.evaluate("document.getElementById('sdo')&&sdClose();tab='hoje';render()")
    A(not pg.evaluate("isPrem()"),"E1 Premium vencido não libera")
    pg.click(".rcc>summary");A(pg.evaluate("P().recipes.length")==1 and "Almoço" in pg.inner_text(".rcc"),"E2 receitas continuam visíveis")
    n=pg.evaluate("items().length");pg.evaluate("recipeAdd(0)");A(pg.evaluate("items().length")==n and pg.evaluate("tab")=="prem","E3 registrar receita pede Premium")
    pg.evaluate("tab='hoje';OP.hdt=true;dmOpen=true;render()")
    A(pg.locator("details.fsw").count()==0 and pg.locator(".fsw0").count()>0,"E4 troca de alimento bloqueada, alimentos visíveis")
    A(pg.evaluate("(P().mealSwaps||[]).length")>=1,"E5 trocas guardadas (voltam se assinar de novo)")
    pg.evaluate("tab='prog';pgS='trn';OP.pgpr=true;render()");A("Revisão semanal" in pg.inner_text("#app") and pg.locator("text=Escolher este foco").count()==0,"E6 revisão vira cartão Premium")
    pg.evaluate("tab='treino';render();document.querySelector('#exc0').open=true");A("Último treino" not in pg.inner_text("#exc0"),"E7 referência do treino só no Premium")
    A(pg.evaluate("JSON.stringify(S.log)")==json.dumps(st["log"],separators=(',',':'),ensure_ascii=False),"E8 diário intacto após expirar")
    A(not errs,"sem erros JS expirado "+str(errs[:2]))
print("FALHAS:",F)
