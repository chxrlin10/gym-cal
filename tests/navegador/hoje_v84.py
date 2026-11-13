import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from comum import URL,SEED,lancar
from playwright.sync_api import sync_playwright
F=[]
def A(c,m):
    print(("OK   " if c else "FAIL ")+m)
    if not c:F.append(m)
with sync_playwright() as p:
    b=lancar(p)
    for hora,ref in [(8,"Café da manhã"),(12,"Almoço"),(16,"Lanche"),(21,"Jantar")]:
        ctx=b.new_context(viewport={"width":390,"height":844});pg=ctx.new_page()
        pg.add_init_script("(()=>{const D=Date;const fix=new D();fix.setHours(%d,30,0,0);const off=fix-D.now();window.Date=class extends D{constructor(...a){if(a.length)super(...a);else super(D.now()+off)}static now(){return D.now()+off}};})()"%hora)
        pg.goto(URL);pg.evaluate(SEED);pg.reload();pg.evaluate("document.getElementById('sdo')&&sdClose();tab='hoje';render()")
        pg.click(".gc-quickadd");A(pg.evaluate("am")==ref and pg.locator("#fsq").is_visible(),f"às {hora}h abre {ref}")
        ctx.close()
    pg=b.new_page(viewport={"width":390,"height":844});errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL);pg.evaluate(SEED);pg.reload();pg.evaluate("document.getElementById('sdo')&&sdClose();tab='hoje';render()")
    ordem=pg.evaluate("""(()=>{const y=e=>e?e.getBoundingClientRect().top+scrollY:-1;const q=s=>document.querySelector(s);const cx=[...document.querySelectorAll('summary')].find(x=>x.textContent.includes('Ver cálculo do dia'));
      return {macr:y(q('.macr')),tcard:y(q('.tcard')),calc:y(cx),ref:y([...document.querySelectorAll('.sech h2')].find(h=>h.textContent==='Refeições')),add:y(q('.gc-quickadd')),meals:y(q('.msf')),scr:y(q('.scr'))}})()""")
    A(ordem["macr"]<ordem["tcard"]<ordem["calc"],"treino logo depois dos macros "+str(ordem))
    A(ordem["ref"]<ordem["add"]<ordem["meals"],"Registrar alimento entre o título e as refeições")
    A(ordem["scr"]>0 and pg.locator(".scr").is_visible(),"resumo da semana e rank continua visível")
    A(pg.locator("text=Guarde seus dados na nuvem").is_visible(),"convite de conta visível para quem não tem conta")
    pg.evaluate("A={at:'x',rt:'y',exp:Math.floor(Date.now()/1e3)+3600,uid:'11111111-2222-3333-4444-555555555555',email:'a@b.c'};render()")
    A(pg.locator("summary:has-text('Conta e sincronização')").count()==0 and pg.locator("text=Guarde seus dados na nuvem").count()==0,"logado: nenhuma seção vazia de conta")
    pg.evaluate("A=null;render()")
    pg.click(".tcard");A(pg.evaluate("tab")=="treino","card de treino abre o Treino")
    pg.evaluate("tab='hoje';off=-1;render()");pg.click(".gc-quickadd");pg.fill("#fsq","banana");pg.wait_for_timeout(200);pg.locator("#fres .fr").first.click();pg.click("text=Adicionar ao diário")
    A(pg.evaluate("(()=>{const d=new Date();d.setDate(d.getDate()-1);return (S.log[pid()][dk(d)]||[]).some(x=>/Banana/.test(x.n))})()"),"registrar em Ontem grava no dia certo")
    pg.evaluate("off=0;tab='hoje';render()");pg.focus(".gc-quickadd");pg.keyboard.press("Shift+Tab");pg.keyboard.press("Tab")
    A(pg.evaluate("getComputedStyle(document.activeElement).outlineStyle")!="none","foco visível no botão pelo teclado")
    A(not errs,"sem erros JS "+str(errs[:2]))
print("FALHAS:",F)
