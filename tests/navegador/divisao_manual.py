# v92: avaliação + divisão escolhida à mão (PPL, Superior/Inferior, Corpo inteiro...), casos Rafaela e Charles,
# catálogo novo, troca por equivalência, ciclo entre semanas, Premium com e sem assinatura, compatibilidade com a v89.
import sys,os,json,hashlib;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from comum import URL,SEED,lancar,html_pago,AQUI
from playwright.sync_api import sync_playwright
F=[]
def A(c,m):
    print(("OK   " if c else "FAIL ")+m)
    if not c:F.append(m)
# frequência semanal e séries diretas medidas FORA do motor, só a partir dos treinos entregues: percorre 12 semanas do ciclo
MED="""(c)=>{const p=P();Object.assign(p,{loc:'gym',days:c.d,exp:c.e,focus:'',split:c.st,vr:0,rtOn:false,sex:c.sex||p.sex});delete p.sub;p.av=Object.assign({on:true,g:'hip',pr:[],dur:60,ex:[],lim:[],hy:''},c.av||{});
 const PP=plansFor(p),keys=PP.keys,sem=12,seq=[];for(let i=0;i<sem*c.d;i++)seq.push(keys[i%keys.length]);
 const out={keys:keys.length,nomes:keys.map(k=>PP.P[k][0]),freq:{},dir:{},hy:PP.hy||null,hyOn:!!PP.hyOn,ex:keys.flatMap(k=>PP.P[k][1].map(x=>x[0])),sets:keys.map(k=>PP.P[k][1].reduce((a,x)=>a+x[1],0)),min:Math.min(...keys.map(k=>PP.P[k][1].length)),
  json:JSON.stringify(keys.map(k=>PP.P[k])),vazio:!!PP.vazio,why:PP.why||[]};
 for(const m of MAIN){let s=0,d=0;seq.forEach(k=>{const dm=PP.P[k][1].filter(x=>EX[x[0]].p[0]===m).reduce((a,x)=>a+x[1],0);if(PP.P[k][1].some(x=>EX[x[0]].p.includes(m)&&x[1]>=2))s++;d+=dm});out.freq[m]=s/sem;out.dir[m]=d/sem;let tc=0;seq.forEach(k=>PP.P[k][1].forEach(x=>{const e=EX[x[0]];if(e.p.includes(m))tc+=x[1];else if(e.s.includes(m))tc+=x[1]*.5}));out.touch=out.touch||{};out.touch[m]=tc/sem}
 return out}"""
with sync_playwright() as p:
    b=lancar(p);pg=b.new_page(viewport={"width":390,"height":844});errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL);pg.evaluate("S.seen=true;Object.assign(S.people[0],{name:'Ana',set:true,sex:'f',w:60,h:163,age:23,exp:0,days:4,loc:'gym'});save()")
    med=lambda c:pg.evaluate(MED,c)
    # 1. avaliação desligada: estilos manuais idênticos aos da v89 (1080 impressões geradas com o arquivo da v89)
    snap=json.load(open(os.path.join(AQUI,"planos_estilos_v89.json")))
    r=pg.evaluate("""()=>{const o={},p=P();for(const loc of ['gym','cond','home','cal'])for(const d of [2,3,4,5,6])for(const e of [0,1,2])for(const st of ['fb','ul','ppl','five','arnold','ulf'])for(const v of [0,1,2]){Object.assign(p,{loc,days:d,exp:e,focus:'',vr:v,split:st,rtOn:false});delete p.av;const PP=plansFor(p);o[[loc,d,e,st,v].join('|')]=JSON.stringify(PP.keys.map(k=>[PP.P[k][0],PP.P[k][1].map(x=>x.slice(0)),PP.P[k][2]]))}return o}""")
    dif=[k for k,v in r.items() if hashlib.sha1(v.encode()).hexdigest()[:12]!=snap.get(k)]
    A(len(r)==len(snap)==1080 and not dif,f"avaliação desligada: 1080 planos de estilos Premium (PPL, UL, FB, ABCDE, Arnold, ULF) idênticos aos da v89 {dif[:3]}")
    # 1b. avaliação ligada porém inválida/desligada com PPL continua igual
    r=pg.evaluate("""()=>{const p=P();Object.assign(p,{loc:'gym',days:5,exp:1,focus:'',vr:0,split:'ppl',rtOn:false});delete p.av;const a=JSON.stringify(plansFor(p).P);const bad=[];for(const v of [null,1,'x',[],{on:false,pr:['Glúteos']},{on:'true'}]){p.av=v;if(JSON.stringify(plansFor(p).P)!==a)bad.push(JSON.stringify(v))}return bad}""")
    A(r==[],f"PPL com avaliação desligada ou inválida não muda nada {r}")
    # 2. Rafaela: iniciante, academia, glúteos e quadríceps, PPL
    R={}
    for d in (3,4,5):
        R[d]=med({"d":d,"e":0,"st":"ppl","av":{"pr":["Glúteos","Quadríceps"],"dur":60},"sex":"f"})
    base={d:med({"d":d,"e":0,"st":"ppl","av":{"pr":[],"dur":60},"sex":"f"}) for d in (3,4,5)}
    for d in (3,4,5):
        r=R[d];b0=base[d]
        A(r["keys"]==6 and r["nomes"][:3]==["Empurrar A","Puxar A","Pernas A"],f"Rafaela {d} dias: a escolha PPL foi mantida ({r['nomes']})")
        A(r["dir"]["Glúteos"]>b0["dir"]["Glúteos"] and r["dir"]["Quadríceps"]>b0["dir"]["Quadríceps"],f"Rafaela {d} dias: séries diretas semanais de glúteos {b0['dir']['Glúteos']:.1f}→{r['dir']['Glúteos']:.1f} e quadríceps {b0['dir']['Quadríceps']:.1f}→{r['dir']['Quadríceps']:.1f}")
        tot=lambda x:sum(x["dir"].values());A(tot(r)<=tot(b0)*1.2+1,f"Rafaela {d} dias: total de séries diretas {tot(b0):.1f}→{tot(r):.1f} (prioridade não infla o volume)")
        A(r["min"]>=2 and max(r["sets"])<=26,f"Rafaela {d} dias: nenhuma sessão vazia e no máximo 26 séries por treino {r['sets']}")
        mn={"Peitoral":6,"Costas":6,"Ombros":4,"Bíceps":3,"Tríceps":3}
        A(all(r["touch"][m]>=mn[m] for m in mn),f"Rafaela {d} dias: parte de cima não é esquecida (séries semanais com participação direta ou de apoio, medidas nos treinos entregues) {({m:round(r['touch'][m],1) for m in mn})}")
    A(R[3]["hy"] is None and any("1 vez" in x for x in R[3]["why"]),"Rafaela 3 dias: mantém PPL sem oferecer híbrida e explica que alguns grupos treinam 1 vez por semana")
    for d in (4,5):
        r=R[d]
        A(r["hy"] and r["hy"]["rz"]=="prio" and not r["hyOn"] and r["freq"]["Glúteos"]<2 and r["freq"]["Quadríceps"]<2 and any("Sugestão" in x and "não foi aplicada" in x for x in r["why"]),f"Rafaela {d} dias: PPL puro treina prioridades {r['freq']['Glúteos']:.2f}x/semana; o app só sugere a híbrida, sem aplicar ({r['hy']})")
    # 2b. aceitar a híbrida é ação do usuário; o estilo guardado não é trocado e dá para desfazer
    pg.evaluate("Object.assign(P(),{loc:'gym',days:4,exp:0,focus:'',split:'ppl',rtOn:false});P().av={on:true,g:'hip',pr:['Glúteos','Quadríceps'],dur:60};delete P().sub;save();PFO.trn=true;tab='perfil';render()")
    A(pg.evaluate("avOf(P()).hy")=="" and "Usar divisão híbrida" in pg.inner_text("#avbox"),"a tela oferece 'Usar divisão híbrida' e nada foi aplicado")
    antes=pg.evaluate("JSON.stringify(plansFor(P()).P)")
    pg.click("button:text-is('Usar divisão híbrida')")
    h=med({"d":4,"e":0,"st":"ppl","av":{"pr":["Glúteos","Quadríceps"],"dur":60,"hy":"ppl|4"}})
    A(pg.evaluate("avOf(P()).hy")=="ppl|4" and pg.evaluate("P().split")=="ppl" and pg.evaluate("plansFor(P()).keys.length")==4 and pg.evaluate("plansFor(P()).hyOn"),"ao aceitar: 4 treinos, estilo guardado continua PPL, híbrida marcada como aceita")
    A(h["freq"]["Glúteos"]>=2 and h["freq"]["Quadríceps"]>=2 and h["dir"]["Glúteos"]>=R[4]["dir"]["Glúteos"]*.8,f"híbrida: prioridades {h['freq']['Glúteos']:.1f}x/semana, glúteos {h['dir']['Glúteos']:.1f} séries diretas")
    pg.reload();A(pg.evaluate("plansFor(P()).hyOn")==True and pg.evaluate("plansFor(P()).keys.length")==4,"a híbrida aceita sobrevive ao recarregar")
    pg.evaluate("PFO.trn=true;tab='perfil';render()");pg.click("button:has-text('Voltar para Push')")
    A(pg.evaluate("avOf(P()).hy")=="" and pg.evaluate("JSON.stringify(plansFor(P()).P)")==antes,"desfazer volta exatamente ao PPL anterior")
    pg.evaluate("P().days=5;save()");A(pg.evaluate("avOf(P()).hy")=="" and not pg.evaluate("plansFor(P()).hyOn"),"aceite vale só para a combinação (estilo e dias) em que foi dado")
    # 3. Charles: PPL equilibrado, sem supino reto/halteres
    EXC=["Supino reto","Supino com halteres"]
    C={d:med({"d":d,"e":1,"st":"ppl","av":{"pr":[],"dur":60,"ex":EXC},"sex":"m"}) for d in (4,5)}
    for d in (4,5):
        c=C[d]
        A(not any(n in EXC for n in c["ex"]) and c["keys"]==6,f"Charles {d} dias: PPL mantido e sem supino reto nem com halteres")
        ok=all(c["freq"][m]>=1.2 for m in ["Peitoral","Costas","Ombros","Quadríceps","Posterior de coxa","Glúteos"])
        A(ok and c["hy"] is None,f"Charles {d} dias: sem prioridade, nenhum grande grupo abaixo de 1,2x/semana e sem oferta de híbrida {({m:round(v,1) for m,v in c['freq'].items()})}")
        vol=c["dir"];A(max(vol[m] for m in ["Peitoral","Ombros","Quadríceps"])<=2.2*min(vol[m] for m in ["Peitoral","Ombros","Quadríceps"]),f"Charles {d} dias: volume direto equilibrado {({m:round(vol[m],1) for m in vol})}")
    A(R[4]["json"]!=C[4]["json"] and R[5]["json"]!=C[5]["json"],"Charles e Rafaela escolhem PPL e recebem treinos diferentes")
    fem=med({"d":4,"e":1,"st":"ppl","av":{"pr":[],"dur":60,"ex":EXC},"sex":"f"})
    A(fem["json"]==C[4]["json"],"o sexo não muda o treino: mesma avaliação com sexo diferente gera o mesmo plano")
    r=pg.evaluate("""()=>{const p=P();Object.assign(p,{loc:'gym',days:4,exp:1,split:'ppl',focus:''});p.av={on:true,g:'hip',pr:[],dur:60,ex:[]};const a=PLN(p);p.av.pr=['Glúteos'];const b=PLN(p);return{g:a.res.find(x=>x[0]==='Glúteos')[2],g2:b.res.find(x=>x[0]==='Glúteos')[2]}}""")
    A(r["g2"]>r["g"],f"só a prioridade escolhida aumenta o glúteo ({r['g']}→{r['g2']}), não o sexo")
    # 4. Superior/Inferior e Corpo inteiro personalizados
    u0=med({"d":4,"e":1,"st":"ul","av":{"pr":[],"dur":60}});u1=med({"d":4,"e":1,"st":"ul","av":{"pr":["Ombros","Bíceps"],"dur":60}})
    A(u1["nomes"]==["Superior A","Inferior A","Superior B","Inferior B"] and u1["freq"]["Ombros"]>=2 and u1["dir"]["Ombros"]>u0["dir"]["Ombros"] and u1["dir"]["Bíceps"]>u0["dir"]["Bíceps"],f"Superior/Inferior com prioridade: ombros {u0['dir']['Ombros']:.1f}→{u1['dir']['Ombros']:.1f}, bíceps {u0['dir']['Bíceps']:.1f}→{u1['dir']['Bíceps']:.1f}")
    f0=med({"d":3,"e":1,"st":"fb","av":{"pr":[],"dur":60}});f1=med({"d":3,"e":1,"st":"fb","av":{"pr":["Glúteos"],"dur":60}})
    A(f1["nomes"]==["Corpo inteiro A","Corpo inteiro B","Corpo inteiro C"] and f1["freq"]["Glúteos"]>=3 and f1["dir"]["Glúteos"]>f0["dir"]["Glúteos"] and f1["min"]>=3,f"Corpo inteiro com prioridade: glúteos {f0['dir']['Glúteos']:.1f}→{f1['dir']['Glúteos']:.1f} séries diretas, 3x/semana")
    f6=med({"d":6,"e":1,"st":"fb","av":{"pr":[],"dur":60}})
    A(f6["nomes"][0].startswith("Corpo inteiro") and f6["hy"] and not f6["hyOn"] and any("fora do ideal" in x for x in f6["why"]) and all(f6["freq"][m]>=4 for m in ["Peitoral","Quadríceps"]),f"Corpo inteiro com 6 dias: mantém a escolha, avisa que fica fora do ideal (mesmos grupos em dias seguidos: {f6['freq']['Peitoral']:.0f}x/semana) e só oferece alternativa ({f6['hy']})")
    d2=med({"d":2,"e":1,"st":"ppl","av":{"pr":[],"dur":60}})
    A(d2["nomes"][0]=="Empurrar A" and d2["hy"] and d2["hy"]["rz"]=="dias" and any("fora do ideal" in x for x in d2["why"]),"PPL com 2 dias: mantém a escolha, avisa que fica fora do ideal e oferece alternativa")
    for st,dd in [("five",5),("arnold",3),("ulf",3),("arnold",6),("five",4)]:
        z=med({"d":dd,"e":1,"st":st,"av":{"pr":[],"dur":60}});A(not z["vazio"] and z["min"]>=2 and z["keys"]>=3,f"{st} {dd} dias com avaliação monta sessões completas {z['nomes']}")
    # 5. Premium sem e com assinatura
    pg2=b.new_page(viewport={"width":390,"height":844});e2=[];pg2.on("pageerror",lambda e:e2.append(str(e)));pg2.route("**/*.supabase.co/**",lambda r:r.fulfill(status=200,content_type="application/json",body="[]"))
    pg2.goto(html_pago());pg2.evaluate(SEED);pg2.evaluate("Object.assign(P(),{loc:'gym',days:5,exp:0,split:'ppl',focus:'',rtOn:false});P().av={on:true,g:'hip',pr:['Glúteos'],dur:60};save()");pg2.reload()
    g=pg2.evaluate("""()=>{const p=P(),a=JSON.stringify(plansFor(p).P);p.split='auto';const b=JSON.stringify(plansFor(p).P);p.split='ppl';return{free:styOf(p)==='auto',igual:a===b,split:p.split,prem:isPrem()}}""")
    A(g["free"] and g["igual"] and g["split"]=="ppl" and not g["prem"],f"sem assinatura: o estilo PPL não vale (usa o Automático) e o estilo guardado não é apagado {g}")
    pg2.evaluate("PFO.trn=true;tab='perfil';render()");pg2.select_option("#psplit","ul");pg2.click("#spn-trn >> text=Salvar e calcular")
    A(pg2.evaluate("P().split")=="ppl","sem assinatura: salvar não troca o estilo")
    pg2.evaluate("""localStorage.setItem('gymcal_auth',JSON.stringify({at:'x',rt:'y',exp:Math.floor(Date.now()/1e3)+3600,uid:'u92',email:'a@b.c'}));localStorage.setItem('gymcal_ent',JSON.stringify({active:true,exp:0,chk:Date.now()-5000,uid:'u92'}))""");pg2.reload();pg2.evaluate("document.getElementById('sdo')&&sdClose()")
    g=pg2.evaluate("""()=>{const p=P(),R=plansFor(p);return{prem:isPrem(),sty:styOf(p),n:R.P[R.keys[0]][0],k:R.keys.length,why:(R.why||[])[0]||''}}""")
    A(g["prem"] and g["sty"]=="ppl" and g["n"]=="Empurrar A" and g["k"]==6 and "Divisão escolhida por você" in g["why"],f"com assinatura: o PPL escolhido entra na avaliação {g}")
    A(not e2,f"sem erro de JS nas telas pagas {e2[:2]}");pg2.close()
    # 6. Minha rotina continua com prioridade
    r=pg.evaluate("""()=>{const p=P();Object.assign(p,{loc:'gym',days:4,exp:1,split:'ppl',focus:'',rtOn:true});p.rt=[{id:'x1',n:'Minha',ex:[['Supino reto',3,'10',0]]}];p.av={on:true,g:'hip',pr:['Glúteos'],dur:60};const R=plansFor(p);const o={n:R.P.A[0],k:R.keys.length};p.rtOn=false;return o}""")
    A(r["n"]=="Minha" and r["k"]==1,f"Minha rotina ativa vence estilo e avaliação {r}")
    # 7. exclusões, equipamentos e limitações com divisão manual
    r=pg.evaluate("""()=>{const bad=[],p=P(),all=PP=>PP.keys.flatMap(k=>PP.P[k][1].map(x=>x[0]));const ORCj=/agachamento|leg press|afundo|passada|extensora|búlgaro|panturrilha|flexora|hack squat/i,ORCl=/terra|stiff|remada curvada|remada baixa|cavalinho|desenvolvimento|agachamento|leg press|ponte|elevação pélvica|glute drive|coice|prancha|abdominal|superman|elevação de pernas|afundo|passada|búlgaro|remada unilateral|hack squat/i;
     for(const st of ['ppl','ul','fb','five','arnold','ulf'])for(const d of [3,4,5]){Object.assign(p,{loc:'gym',days:d,exp:2,split:st,focus:'',rtOn:false});delete p.sub;
      p.av={on:true,g:'hip',pr:[],dur:60,ex:['Agachamento','Leg press','Rosca direta']};let n=all(plansFor(p));if(n.some(x=>['Agachamento','Leg press','Rosca direta'].includes(x)))bad.push(st+d+' excluído');
      p.av={on:true,g:'hip',pr:[],dur:60,eq:['H']};n=all(plansFor(p));if(n.some(x=>EXM[x].eq.split('').some(c=>c!=='W'&&c!=='H')))bad.push(st+d+' equipamento');
      p.av={on:true,g:'hip',pr:[],dur:60,lim:['j']};n=all(plansFor(p));if(n.some(x=>ORCj.test(x)))bad.push(st+d+' joelho '+n.find(x=>ORCj.test(x)));
      p.av={on:true,g:'hip',pr:[],dur:60,lim:['l']};n=all(plansFor(p));if(n.some(x=>ORCl.test(x)))bad.push(st+d+' lombar '+n.find(x=>ORCl.test(x)));
      const R=PLN(p);if(!R.why.some(x=>x.includes('não é garantia')||x.includes('Exercício sem marcação')))bad.push(st+d+' sem aviso')}return bad.slice(0,8)}""")
    A(r==[],f"divisão manual respeita exclusões, equipamento e limitações (oráculo independente), com aviso {r}")
    # 8. catálogo: 19 novos, sem duplicata, metadados completos, antigos intactos
    old=json.load(open(os.path.join(AQUI,"catalogo_v91.json")))
    r=pg.evaluate("""old=>{const bad=[],novos=Object.keys(EX).filter(n=>!old[n]),nm=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]/g,'');
     for(const [n,o] of Object.entries(old)){if(!EX[n])bad.push('sumiu '+n);else{if(JSON.stringify(EX[n].p)!==JSON.stringify(o.p)||JSON.stringify(EX[n].s)!==JSON.stringify(o.s)||JSON.stringify(EXM[n])!==JSON.stringify(o.m))bad.push('mudou '+n)}}
     const seen=new Set();Object.keys(EX).forEach(n=>{const k=nm(n);if(seen.has(k))bad.push('duplicado '+n);seen.add(k)});
     novos.forEach(n=>{const x=EX[n];if(!EXM[n])bad.push('sem EXM '+n);if(!Array.isArray(x.how)||x.how.length<3||!x.t||!x.equipment||!x.p.length||!x.pin||!x.A||!x.B)bad.push('incompleto '+n);if(gi(n)<0)bad.push('sem grupo de variação '+n)});
     return{bad,novos:novos.length,total:Object.keys(EX).length}}""",old)
    A(r["bad"]==[] and r["novos"]==19 and r["total"]==87,f"catálogo: {r['novos']} exercícios novos (total {r['total']}), nenhum nome duplicado, antigos intactos {r['bad'][:4]}")
    r=pg.evaluate("""()=>{const bad=[],p=P();Object.assign(p,{loc:'gym',split:'auto',focus:'',rtOn:false});delete p.av;delete p.sub;
      const novos=['Chest Press na máquina','Supino inclinado na máquina','Supino articulado','Peck Deck','Crucifixo na polia','Remada articulada com apoio','Puxada articulada','Desenvolvimento na máquina','Elevação lateral na máquina','Rosca Scott na máquina','Rosca bíceps na máquina','Tríceps na máquina','Glute Drive','Cadeira abdutora','Cadeira adutora','Coice de glúteos na polia','Coice de glúteos na máquina','Hack Squat','Panturrilha na máquina'];
      for(const d of [2,3,4,5,6])for(const e of [0,1,2])for(const v of [0,1,2]){Object.assign(p,{days:d,exp:e,vr:v});const PP=plansFor(p);PP.keys.forEach(k=>PP.P[k][1].forEach(x=>{if(novos.includes(x[0]))bad.push(d+'/'+e+'/'+v+' '+x[0])}))}
      const p2=P();Object.assign(p2,{loc:'gym',days:4,exp:1,vr:0});p2.av={on:true,g:'hip',pr:[],dur:90};const q=PLN(p2).sess.flatMap(s=>s.ex.map(x=>x[0])).filter(n=>novos.includes(n));return{bad:bad.slice(0,3),novosNoPlano:q.length}}""")
    A(r["bad"]==[],f"os exercícios novos não aparecem nos planos sem avaliação {r}")
    # 9. troca por equivalência: Supino reto -> Chest Press
    r=pg.evaluate("""()=>{const o={},p=P();Object.assign(p,{loc:'gym',days:3,exp:0,focus:'',split:'ppl',vr:0,rtOn:false});delete p.sub;p.av={on:true,g:'hip',pr:[],dur:60,ex:[]};
      const PP=plansFor(p),ex=PP.P.A[1],e=ex[0];o.e0=e[0];const T=swAltT(e,ex.filter(x=>x[0]!=='Peck Deck')),pos=n=>T.findIndex(z=>z[0]===n),tier=n=>(T.find(z=>z[0]===n)||[0,0])[1];
      o.cp=pos('Chest Press na máquina');o.cpT=tier('Chest Press na máquina');o.pd=tier('Peck Deck');o.pdPos=pos('Peck Deck');o.incl=tier('Supino inclinado com halteres');o.n=T.length;
      o.ordem=T.every((z,i)=>i===0||T[i-1][1]<=z[1]);return o}""")
    A(r["e0"]=="Supino reto" and r["cp"]==0 and r["cpT"]==1,f"Supino reto: Chest Press na máquina é a 1ª alternativa e de alta equivalência {r}")
    A(r["pd"]==3 and r["pdPos"]>r["cp"] and r["incl"]==2 and r["ordem"],f"Peck Deck aparece como 'menos equivalente' (movimento diferente), depois dos equivalentes e parecidos {r}")
    r=pg.evaluate("""()=>{const o={},p=P();Object.assign(p,{loc:'gym',days:3,exp:0,focus:'',split:'ppl',vr:0,rtOn:false});delete p.sub;const eq=ex=>{const PP=plansFor(p);return swAltT(PP.P.A[1][0],PP.P.A[1]).map(z=>z[0])};
      p.av={on:true,g:'hip',pr:[],dur:60,ex:['Chest Press na máquina']};o.excl=!eq().includes('Chest Press na máquina');
      p.av={on:true,g:'hip',pr:[],dur:60,eq:['H','N']};o.sem=!eq().some(n=>EXM[n].eq.includes('M')||EXM[n].eq.includes('P'))&&eq().includes('Supino com halteres');
      p.av={on:true,g:'hip',pr:[],dur:60,lim:['o']};o.lim=eq().length===0||!eq().some(n=>EXM[n].rg.includes('o'));
      p.av={on:true,g:'hip',pr:[],dur:60};const PP=plansFor(p),ex=PP.P.A[1];return Object.assign(o,{ok:true})}""")
    A(r["excl"] and r["sem"] and r["lim"],f"alternativas respeitam exclusão, equipamento e limitação {r}")
    r=pg.evaluate("""()=>{const o={},p=P();Object.assign(p,{loc:'gym',days:3,exp:0,focus:'',split:'ppl',vr:0,rtOn:false});delete p.sub;p.av={on:true,g:'hip',pr:[],dur:60,ex:[]};
      let PP=plansFor(p);const antes=PP.P.A[1].map(x=>[x[0],x[1],x[2],x[3]]),n0=PP.P.A[1].length;plan='A';swDo(0,'Chest Press na máquina');PP=plansFor(p);const dep=PP.P.A[1];
      o.troca=dep[0][0]==='Chest Press na máquina'&&dep[0].o==='Supino reto'&&dep[0][1]===antes[0][1]&&dep.length===n0&&dep.slice(1).every((x,i)=>x[0]===antes[i+1][0]);
      o.semDup=new Set(dep.map(x=>x[0])).size===dep.length;o.sub=JSON.stringify(p.sub);
      const S0=dep.map(x=>x[0]);plan='A';swUndo(0);PP=plansFor(p);o.undo=PP.P.A[1][0][0]==='Supino reto'&&!p.sub['A|Supino reto'];
      p.sub={'A|Supino reto':'Chest Press na máquina','A|Puxada frontal':'Chest Press na máquina'};PP=plansFor(p);o.dupInv=PP.P.A[1].filter(x=>x[0]==='Chest Press na máquina').length<=1;
      p.sub={'A|Supino reto':'Peck Deck'};PP=plansFor(p);o.mesmoMusculo=EX[PP.P.A[1][0][0]].p[0]==='Peitoral';delete p.sub;return o}""")
    A(r["troca"] and r["semDup"] and r["undo"] and r["dupInv"] and r["mesmoMusculo"],f"troca aplicada mantém a estrutura (séries e demais exercícios), não duplica e pode ser desfeita {r}")
    # 10. ciclo entre semanas: continua de onde parou
    r=pg.evaluate("""()=>{const p=P(),id=pid();Object.assign(p,{loc:'gym',days:5,exp:1,focus:'',split:'ppl',vr:0,rtOn:false});delete p.sub;delete p.splitFrom;p.av={on:true,g:'hip',pr:[],dur:60};S.wk[id]=[];const PP=plansFor(p),seq=[];
      const t0=new Date();t0.setDate(t0.getDate()-60);for(let i=0;i<14;i++){const k=nextKey(id,PP.keys,PP);seq.push(k);const d=new Date(t0);d.setDate(t0.getDate()+Math.floor(i/5)*7+(i%5));S.wk[id].push({d:dk(d),plan:k,n:3,ex:PP.P[k][1].map(x=>x[0]),st:[3,3,3],det:[]})}
      return{seq:seq.join(''),keys:PP.keys.join('')}}""")
    cyc=(r["keys"]*3)[:14]
    A(r["seq"]==cyc,f"PPL de 5 dias: o ciclo A–F continua entre as semanas sem reiniciar na segunda ({r['seq']})")
    r=pg.evaluate("""()=>{const p=P(),id=pid();const x=S.wk[id].length;p.av.hy='';p.av.pr=['Glúteos'];const a=nextKey(id,plansFor(p).keys,plansFor(p));return{a,last:S.wk[id][x-1].plan}}""")
    A(r["a"]!=None,"nextKey continua válido depois de mudar a avaliação")
    # 11. persistência
    pg.evaluate("Object.assign(P(),{loc:'gym',days:5,exp:0,split:'ppl',focus:'',rtOn:false});P().av={on:true,g:'hip',pr:['Glúteos','Quadríceps'],dur:60,hy:'ppl|5',ex:['Supino reto']};delete P().sub;save();localStorage.setItem('__d',JSON.stringify(plansFor(P()).P))")
    pg.reload();A(pg.evaluate("JSON.stringify(plansFor(P()).P)===localStorage.getItem('__d')")and pg.evaluate("plansFor(P()).hyOn"),"salvar e recarregar: mesmo plano com divisão manual, híbrida aceita e exclusão")
    # 12. sessões vazias nunca aparecem como treino completo
    r=pg.evaluate("""()=>{const p=P(),bad=[];Object.assign(p,{loc:'home',days:5,exp:0,split:'ppl',focus:'',rtOn:false});delete p.sub;
      for(const av of [{eq:[],ex:Object.keys(EX)},{eq:[],ex:Object.keys(EX).filter(n=>EX[n].p.includes('Peitoral')||EX[n].p.includes('Costas')||EX[n].p.includes('Ombros'))},{lim:['o','l','j','q','c'],eq:['H']}])for(const st of ['ppl','ul','fb','five','arnold','ulf'])for(const d of [3,5]){Object.assign(p,{split:st,days:d});p.av=Object.assign({on:true,g:'hip',pr:[],dur:30},av);
        try{const PP=plansFor(p);if(PP.vazio&&PP.keys.length)bad.push('vazio com chaves');PP.keys.forEach(k=>{if(PP.P[k][1].length<2)bad.push(st+d+' sessão com '+PP.P[k][1].length)});if(!PP.vazio&&PP.keys.some(k=>PP.P[k][1].length<3)&&!PP.why.some(x=>x.includes('curto')||x.includes('Não foi possível')))bad.push(st+d+' curta sem aviso')}catch(e){bad.push(st+d+' '+e.message)}}
      tab='treino';render();return bad.slice(0,6)}""")
    A(r==[],f"nenhuma sessão vazia ou curta sem aviso, com todos os estilos e restrições extremas {r}")
    r=pg.evaluate("""()=>{const p=P();Object.assign(p,{loc:'home',days:4,exp:0,split:'ppl',focus:'',rtOn:false});p.av={on:true,g:'hip',pr:[],dur:60,eq:[],ex:Object.keys(EX)};tab='treino';render();return document.querySelector('#app').innerText.includes('Não foi possível montar seu treino')}""")
    A(r,"aba Treino explica quando nada pode ser montado com o estilo escolhido")
    # 13. entradas corrompidas
    r=pg.evaluate("""()=>{const bad=[],p=P();const V=[undefined,null,NaN,-1,0,99,'x',[],{},true,'__proto__','constructor','toString'];
      for(const sv of V)for(const dv of [undefined,NaN,'4',9,[3]])for(const hv of [undefined,null,1,{},'ppl|9','__proto__|4','ppl|4']){Object.assign(p,{loc:'gym',days:dv,exp:0,split:sv,focus:'',rtOn:false,vr:0});p.sub=sv;p.av={on:true,g:'hip',pr:['Glúteos'],dur:60,hy:hv};
        try{const PP=plansFor(p);if(!PP||!PP.keys.length||PP.keys.length>6)bad.push('keys '+String(sv)+'|'+String(dv));tab='perfil';PFO.trn=true;render();tab='treino';render()}catch(e){bad.push(String(sv)+'|'+String(dv)+'|'+String(hv)+' '+e.message)}}return[...new Set(bad)].slice(0,6)}""")
    A(r==[],f"estilo, dias, substituições e aceite corrompidos não geram exceção {r}")
    # 14. determinismo
    r=pg.evaluate("""()=>{const p=P(),bad=[];for(const st of ['ppl','ul','fb','five','arnold','ulf'])for(const d of [3,4,5,6]){Object.assign(p,{loc:'gym',days:d,exp:1,split:st,focus:'',rtOn:false});delete p.sub;p.av={on:true,g:'for',pr:['Costas'],dur:45};if(JSON.stringify(PLN(p))!==JSON.stringify(PLN(p)))bad.push(st+d)}return bad}""")
    A(r==[],f"mesma entrada, mesmo plano em todos os estilos {r}")
    A(not errs,f"sem erro de JS {errs[:2]}")
    b.close()
print("FALHAS:",F);sys.exit(1 if F else 0)
