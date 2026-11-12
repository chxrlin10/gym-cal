import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from comum import URL,SEED,lancar,html_pago
from playwright.sync_api import sync_playwright
F=[]
def A(c,m):
    print(("OK   " if c else "FAIL ")+m)
    if not c:F.append(m)
with sync_playwright() as p:
    b=lancar(p);pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL);pg.evaluate(SEED)
    pg.evaluate("localStorage.setItem('gymcal_sdforce','1');localStorage.removeItem('gymcal_sd')");pg.reload();pg.wait_for_timeout(300)
    t=pg.inner_text("#sdo");r=pg.evaluate("stkCalc(P().id)")
    A(pg.locator("#sdo").count()==1,"card diário abre")
    A("descanso não quebra" in t and "pontos pro rank" in t,"texto explica sequência semanal e pontos")
    A(("semanas seguidas" in t or "semana seguida" in t) if r['cur']>0 else "Comece" in t,"título coerente com cur=%d"%r['cur'])
    A(str(r['pts'])+" pts" in t,"mostra pontos")
    pg.click("#sdok")
    # gasto alto
    pg.evaluate("window.burnDay=()=>1797;tab='hoje';render()")
    A(pg.locator(".hz-w").count()==1 and "duas vezes" in pg.inner_text(".hz-w"),"aviso de gasto alto")
    pg.evaluate("window.burnDay=()=>500;render()");A(pg.locator(".hz-w").count()==0,"sem aviso com gasto normal")
    # cardio limite
    pg.evaluate("tab='treino';render()")
    n0=pg.evaluate("((S.cardio[pid()]||{})[dk(new Date())]||[]).length")
    if pg.locator("#cmin").count():
        pg.evaluate("document.getElementById('cmin').closest('details')&&(document.getElementById('cmin').closest('details').open=true)")
        pg.evaluate("cmin=600;addCd()")
        A(pg.evaluate("((S.cardio[pid()]||{})[dk(new Date())]||[]).length")==n0,"cardio de 600 min bloqueado")
        pg.evaluate("cmin=30;addCd()")
        A(pg.evaluate("((S.cardio[pid()]||{})[dk(new Date())]||[]).length")==n0+1,"cardio de 30 min registra")
    else: A(False,"campo de cardio encontrado")
    # perfil meta card verde
    pg.evaluate("PFO.obj=true;tab='perfil';render()")
    A(pg.evaluate("getComputedStyle(document.querySelector('#spn-obj .card.hero')).backgroundColor")!="rgb(255, 255, 255)","card da meta no Perfil verde")
    A(not errs,"sem erros JS "+str(errs[:2]))
print("FALHAS:",F)
