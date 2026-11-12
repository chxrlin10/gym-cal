# Utilidades dos testes de navegador (Playwright + Chrome). Uso: python3 tests/navegador/<teste>.py
import os,tempfile,shutil
AQUI=os.path.dirname(os.path.abspath(__file__))
HTML=os.environ.get("GYMCAL_HTML",os.path.normpath(os.path.join(AQUI,"..","..","index.html")))
URL="file://"+HTML
CHROME=os.environ.get("CHROME") or shutil.which("google-chrome") or shutil.which("chromium")
def lancar(p):
    return p.chromium.launch(executable_path=CHROME,args=["--no-sandbox"]) if CHROME else p.chromium.launch()
def html_pago():
    """Cópia do app com uma chave fictícia: liga a cobrança só para teste."""
    d=tempfile.mkdtemp(prefix="gymcal-");f=os.path.join(d,"pago.html")
    open(f,"w").write(open(HTML).read().replace('const RC_KEY="";','const RC_KEY="goog_test";'))
    return "file://"+f
SEED="""S.seen=true;Object.assign(S.people[0],{name:'Charles',set:true,days:4,exp:1,loc:'gym',w:78,h:175,age:28,sex:'m',lvl:1.55,obj:'bulk'});
const t=new Date(),id=S.people[0].id;for(let i=0;i<40;i++){const d=new Date(t);d.setDate(t.getDate()-i);const k=dk(d);
 if(i%2==0)(S.wk[id]=S.wk[id]||[]).push({d:k,plan:'A',pn:'Superior',n:3,ex:['Supino reto','Puxada frontal','Desenvolvimento'],st:[3,3,3],det:[],vl:3000,min:50,kc:300});
 S.wt[id]=S.wt[id]||{};if(i%3==0)S.wt[id][k]=78-i*0.05;
 S.log[id]=S.log[id]||{};S.log[id][k]=[{m:'Café da manhã',n:'Pão com ovo',k:350,p:18,c:30,f:14,g:150,fb:2,cat:'G'},{m:'Almoço',n:'Arroz, feijão e frango',k:700,p:45,c:80,f:15,g:450,fb:8,cat:'P'}]}
save();"""
