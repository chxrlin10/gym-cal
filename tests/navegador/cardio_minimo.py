# Cardio só conta como treino do dia a partir de 20 min (CDMIN); abaixo disso soma calorias, mas não treino/pontos.
import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from comum import URL,lancar
from playwright.sync_api import sync_playwright
F=[]
def A(c,m):
    print(("OK   " if c else "FAIL ")+m)
    if not c:F.append(m)
with sync_playwright() as p:
    b=lancar(p);pg=b.new_page(viewport={"width":390,"height":844});errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL);pg.evaluate("S.seen=true;Object.assign(S.people[0],{name:'Ana',set:true,sex:'f',w:60,h:163,age:24});S.wk[pid()]=[];save()")
    T="dk(new Date())"
    def cd(m):
        pg.evaluate("m=>{const id=pid(),t=dk(new Date());S.cardio[id]={[t]:[{n:'Caminhada',k:50,min:m}]};save()}",m)
        return pg.evaluate("()=>gmTrain(pid()).has(dk(new Date()))"),pg.evaluate("()=>burnDay(pid(),dk(new Date()),P())")
    for m,esp in [(10,False),(15,False),(19,False),(20,True),(30,True)]:
        tr,k=cd(m);A(tr==esp and k==50,f"cardio {m} min: conta como treino={tr} (esperado {esp}), calorias somam={k}")
    pg.evaluate("tab='hoje';render()");A(not errs,f"sem erro JS {errs}")
    b.close()
print("FALHAS:",F);sys.exit(1 if F else 0)
