import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from comum import URL,SEED,lancar,html_pago
import json
from playwright.sync_api import sync_playwright
F=[]
def A(c,m):
    print(("OK   " if c else "FAIL ")+m)
    if not c:F.append(m)
PAGO=html_pago()
UID="11111111-2222-3333-4444-555555555555"
MOCK="""window._rc={calls:[],mode:'ok',get active(){return localStorage.getItem('_rcact')==='1'},set active(v){localStorage.setItem('_rcact',v?'1':'0')}};
const exp=new Date(Date.now()+30*864e5).toISOString();
const ci=()=>({entitlements:{active:window._rc.active?{premium:{identifier:'premium',expirationDate:exp}}:{}}});
window.Capacitor={isNativePlatform:()=>true,Plugins:{Purchases:{
 configure:async o=>{_rc.calls.push(['configure',o.appUserID])},
 logIn:async o=>{_rc.calls.push(['logIn',o.appUserID]);return{customerInfo:ci(),created:false}},
 getCustomerInfo:async()=>({customerInfo:ci()}),
 getOfferings:async()=>{_rc.calls.push(['offers']);if(_rc.mode==='nooffer')throw {code:'10'};return{current:{availablePackages:[
  {identifier:'$rc_monthly',packageType:'MONTHLY',product:{price:12.9,priceString:'R$ 12,90',title:'Mensal (Gym.cal)',introPrice:{price:0,periodNumberOfUnits:7,periodUnit:'DAY'}}},
  {identifier:'$rc_annual',packageType:'ANNUAL',product:{price:99.9,priceString:'R$ 99,90',title:'Anual (Gym.cal)'}}]}}},
 purchasePackage:async o=>{_rc.calls.push(['buy',o.aPackage.identifier]);if(_rc.mode==='cancel')throw {code:'1',userCancelled:true};if(_rc.mode==='fail')throw {code:'2',message:'store'};_rc.active=true;return{customerInfo:ci(),productIdentifier:'m'}},
 restorePurchases:async()=>{_rc.calls.push(['restore']);return{customerInfo:ci()}}
}}};"""
with sync_playwright() as p:
    b=lancar(p)
    def page(native=True):
        pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
        errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.route("**/*.supabase.co/**",lambda r:r.fulfill(status=200,content_type="application/json",body="[]"))
        if native: pg.add_init_script(MOCK)
        pg.goto(PAGO);pg.evaluate("localStorage.removeItem('_rcact')");pg.evaluate("S.seen=true;Object.assign(S.people[0],{name:'Ana',set:true,days:3,exp:1,loc:'gym',w:70,h:170,age:30,sex:'f'});save();render()")
        return pg,errs
    # 1) cobranca ativa, sem conta
    pg,errs=page()
    A(pg.evaluate("PREM_OPEN")==False and pg.evaluate("isPrem()")==False,"cobrança ativa: sem Premium por padrão")
    pg.evaluate("goPrem()");t=pg.inner_text("#app")
    A("Entrar ou criar conta" in t,"sem conta pede login")
    pg.click("text=Entrar ou criar conta");pg.wait_for_timeout(100)
    A(pg.evaluate("tab")=="perfil" and pg.locator("#cem").is_visible(),"botão leva ao login em Conta e sincronização")
    # 2) logado no app Android
    pg.evaluate(f"A={{at:'x',rt:'y',exp:Math.floor(Date.now()/1e3)+3600,uid:'{UID}',email:'ana@x.com'}};saveA();goPrem()");pg.wait_for_timeout(300)
    t=pg.inner_text("#app")
    A("Escolha seu plano" in t and "R$ 12,90" in t and "R$ 99,90" in t,"planos com preço da loja")
    A("7 dias grátis" in t,"mostra período grátis")
    A("renova automaticamente" in t and "Restaurar compras" in t and "Termos de uso" in t,"termos de renovação, restaurar e links")
    A(pg.evaluate("_rc.calls[0]")==["configure",UID],"RevenueCat configurado com o id da conta")
    pg.evaluate("_rc.mode='cancel'");pg.locator("text=Assinar").first.click();pg.wait_for_timeout(300)
    A(not pg.evaluate("isPrem()") and "Não deu" not in pg.inner_text("#app"),"cancelar a compra não libera e não mostra erro")
    pg.evaluate("_rc.mode='fail'");pg.locator("text=Assinar").first.click();pg.wait_for_timeout(300)
    A(not pg.evaluate("isPrem()") and "Não deu para concluir" in pg.inner_text("#app"),"falha avisa")
    pg.evaluate("_rc.mode='ok'");pg.locator("text=Assinar").nth(1).click();pg.wait_for_timeout(300)
    A(pg.evaluate("isPrem()") and "Premium ativo" in pg.inner_text("#app"),"compra libera o Premium")
    A(pg.evaluate("_rc.calls.filter(c=>c[0]=='buy').pop()[1]")=="$rc_annual","comprou o plano escolhido (anual)")
    A("Gerenciar na Google Play" in pg.inner_text("#app"),"mostra gerenciar assinatura")
    pg.evaluate("PFO.pln=true;tab='perfil';render()");A("Seu Premium está ativo" in pg.inner_text("#spn-pln"),"Meu plano mostra ativo")
    # persistencia offline e troca de conta
    pg.reload();pg.wait_for_timeout(200);A(pg.evaluate("isPrem()"),"Premium continua após reabrir")
    pg.evaluate("A=Object.assign({},A,{uid:'99999999-2222-3333-4444-555555555555'});render()");A(not pg.evaluate("isPrem()"),"outra conta não herda o Premium")
    pg.evaluate(f"A=Object.assign({{}},A,{{uid:'{UID}'}});entClear();render()");A(not pg.evaluate("isPrem()"),"sair da conta limpa o Premium local")
    # restaurar
    pg.evaluate("goPrem()");pg.wait_for_timeout(300);pg.click("text=Restaurar compras");pg.wait_for_timeout(300)
    A(pg.evaluate("isPrem()") and "Assinatura restaurada" in pg.inner_text("#app"),"restaurar compras recupera")
    A(not errs,"sem erros JS "+str(errs[:2]));pg.close()
    # 3) web (sem plugin), logado
    pg,errs=page(native=False)
    pg.evaluate(f"A={{at:'x',rt:'y',exp:Math.floor(Date.now()/1e3)+3600,uid:'{UID}',email:'ana@x.com'}};saveA();goPrem()")
    t=pg.inner_text("#app");A("app Gym.cal para Android" in t and "Verificar minha assinatura" in t,"web explica que assina no Android")
    pg.click("text=Verificar minha assinatura");pg.wait_for_timeout(300);A("Não foi possível confirmar uma assinatura ativa" in pg.inner_text("#app"),"verificação sem assinatura")
    pg.unroute("**/*.supabase.co/**");pg.route("**/*.supabase.co/**",lambda r:r.fulfill(status=200,content_type="application/json",body=json.dumps([{"active":True,"expires_at":"2099-01-01T00:00:00Z"}])))
    pg.click("text=Verificar minha assinatura");pg.wait_for_timeout(300);A(pg.evaluate("isPrem()") and "Premium ativo" in pg.inner_text("#app"),"web libera com assinatura do servidor")
    A(not errs,"sem erros JS web "+str(errs[:2]));pg.close()
    # 4) sem planos
    pg,errs=page();pg.evaluate("_rc.mode='nooffer'");pg.evaluate(f"A={{at:'x',rt:'y',exp:Math.floor(Date.now()/1e3)+3600,uid:'{UID}',email:'ana@x.com'}};saveA();goPrem()");pg.wait_for_timeout(300)
    A("Não consegui carregar os planos" in pg.inner_text("#app"),"falha ao carregar planos avisa")
    # 5) versão atual (sem chave) continua liberada
    q=b.new_page();q.goto(URL);A(q.evaluate("PREM_OPEN===true&&isPrem()"),"sem chave: tudo liberado como hoje")
print("FALHAS:",F)
