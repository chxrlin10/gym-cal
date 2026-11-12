import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from comum import URL,SEED,lancar
from playwright.sync_api import sync_playwright
F=[]
def A(c,m):
    print(("OK   " if c else "FAIL ")+m)
    if not c:F.append(m)
with sync_playwright() as p:
    b=lancar(p);pg=b.new_page(viewport={"width":390,"height":844})
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL);pg.evaluate("S.seen=true;Object.assign(S.people[0],{name:'Ana',set:true});save()");pg.reload()
    top=lambda q:pg.evaluate("q=>foodMatches(q).slice(0,3).map(f=>f.n)",q)
    # o preparo do dia a dia vem antes do cru (cru de arroz/carne/feijão engana nas calorias)
    for q,esp in [("arroz","Arroz branco cozido"),("feijao","Feijão carioca cozido"),("ovo","Ovo cozido"),("leite","Leite integral"),("frango grelhado","Peito de frango grelhado"),("aipim","Mandioca cozida")]:
        t=top(q);A(t and t[0]==esp,f"'{q}' começa por {esp} ({t})")
    A(all(not ("cru" in n) for n in top("arroz")),"arroz cru fora do topo")
    A(len(pg.evaluate("foodMatches('espetinho')"))==5,"5 espetinhos")
    ms=pg.evaluate("(()=>{const t=performance.now();for(let i=0;i<20;i++)foodMatches('frango');return (performance.now()-t)/20})()");A(ms<40,"busca rápida (%.1f ms)"%ms)
    pg.evaluate("tab='hoje';render();amSet(1)");pg.fill("#fsq","arroz");pg.wait_for_timeout(200)
    row=pg.locator("#fres .fr:has-text('Tabela TACO')").first;bx=row.bounding_box();kc=row.locator("span.mut").last.bounding_box();nm=row.locator("small").bounding_box()
    A(nm["x"]+nm["width"]<=kc["x"]+1,"linha TACO sem sobrepor as calorias")
    row.click();A("Tabela TACO" in pg.inner_text("#fsel"),"mostra a fonte ao escolher")
    A(not errs,"sem erros JS "+str(errs[:2]))
print("FALHAS:",F)
