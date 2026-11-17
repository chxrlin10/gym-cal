# Planejador de treino (v90): motor determinístico por avaliação. Propriedades em todas as combinações, objetivos, níveis,
# frequências, exercícios/equipamentos indisponíveis, limitações, modo cuidadoso, volume por recuperação,
# compatibilidade (sem avaliação = plano idêntico ao da v89) e tela do Perfil.
import sys,os,json,hashlib;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from comum import URL,lancar,AQUI
from playwright.sync_api import sync_playwright
F=[]
def A(c,m):
    print(("OK   " if c else "FAIL ")+m)
    if not c:F.append(m)
with sync_playwright() as p:
    b=lancar(p);pg=b.new_page(viewport={"width":390,"height":844});errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL);pg.evaluate("S.seen=true;Object.assign(S.people[0],{name:'Ana',set:true,sex:'f',w:60,h:163,age:24,exp:1,days:4,loc:'gym'});save()")
    # 1. tabela de metadados cobre o catálogo inteiro
    r=pg.evaluate("Object.keys(EX).filter(n=>!EXM[n]||!['ph','pv','lh','lv','sq','hg','lg','iso','core','calf'].includes(EXM[n].pt)||![0,1,2].includes(EXM[n].lv)||!/^[BHMPNFW]+$/.test(EXM[n].eq)||!/^[ocljq]*$/.test(EXM[n].rg))")
    A(r==[],f"todo exercício do catálogo tem padrão, equipamento, nível e região {r}")
    # 2. varredura: local x dias x nível x objetivo x duração (valores padrão de equipamento)
    r=pg.evaluate("""()=>{const bad=[],OKR=/^(\\d+( a \\d+)?|\\d+ s)$/,tot={n:0};const p=P();
     for(const loc of ['gym','cond','home','cal'])for(const d of [2,3,4,5,6])for(const e of [0,1,2])for(const g of ['hip','for','sau'])for(const dur of [30,45,60,90]){
      Object.assign(p,{loc,days:d,exp:e,focus:'',split:'auto',vr:0,rtOn:false});p.av={on:true,g,pr:[],dur};tot.n++;
      const R=PLN(p),R2=PLN(p),eq=eqOf(p),id=loc+d+e+g+dur;
      if(JSON.stringify(R)!==JSON.stringify(R2))bad.push(id+' não determinístico');
      if(R.sess.length!==d)bad.push(id+' sessões '+R.sess.length);
      const PP=plansFor(p);if(PP.keys.length!==d||!PP.why)bad.push(id+' plansFor');
      R.sess.forEach(s=>{const ns=s.ex.map(x=>x[0]);if(new Set(ns).size!==ns.length)bad.push(id+' repetido');
        const gs=ns.map(n=>VG.findIndex(G=>G.includes(n))).filter(i=>i>=0);if(new Set(gs).size!==gs.length)bad.push(id+' variantes do mesmo exercício em '+s.n);
        let t=5;s.ex.forEach(([n,k,r,rs])=>{const m=EXM[n];t+=k*(.75+rs/60);
          if(!EX[n]||m.lv>e||m.eq.split('').some(c=>c!=='W'&&!eq.includes(c)))bad.push(id+' indisponível '+n);
          if((loc==='home'||loc==='cal')&&!(isCal(p)?calOk(n):(BW.has(n)||HOMEOK.has(n))))bad.push(id+' fora do local '+n);
          if(!(k>=2&&k<=4)||!OKR.test(r)||![0,45,60,90,120,180].includes(rs))bad.push(id+' formato '+n+' '+k+' '+r+' '+rs)});
        if(t>dur+.01&&s.ex.length>2)bad.push(id+' passa de '+dur+' min: '+Math.round(t)+' em '+s.n)});
      if(loc==='gym'&&dur>=60){R.res.forEach(([m,meta,feito])=>{if(!R.trim&&feito<meta*.6||feito>meta*1.6+1)bad.push(id+' volume '+m+' '+feito+'/'+meta)});
        let pu=0,pl=0;R.sess.forEach(s=>s.ex.forEach(([n,k])=>{const t=EXM[n].pt;if(t==='ph'||t==='pv')pu+=k;if(t==='lh'||t==='lv')pl+=k}));if(R.trim&&!R.why.some(x=>x.includes('Para caber')))bad.push(id+' corte sem aviso');if(pl<pu*.8)bad.push(id+' puxar '+pl+' < empurrar '+pu)}}
     return{bad:bad.slice(0,12),n:bad.length,tot:tot.n}}""")
    A(r["n"]==0,f"{r['tot']} combinações: determinístico, só exercícios disponíveis, sem repetição, cabe no tempo, volume e puxar/empurrar equilibrados {r['bad']}")
    # 3. objetivos
    r=pg.evaluate("""()=>{const p=P();Object.assign(p,{loc:'gym',days:4,exp:1,focus:'',split:'auto',vr:0});const o={};for(const g of ['hip','for','sau']){p.av={on:true,g,pr:[],dur:60};const R=PLN(p),sp=R.sess[0].ex[0];o[g]={reps:sp[2],rest:sp[3],meta:R.res.reduce((s,x)=>s+x[1],0),n:sp[0]}}return o}""")
    A(r["for"]["rest"]>r["hip"]["rest"]>=r["sau"]["rest"]>=60 and r["for"]["reps"]!=r["hip"]["reps"] and r["sau"]["meta"]<r["hip"]["meta"] and r["for"]["meta"]<r["hip"]["meta"],f"objetivos: força descansa mais e usa menos repetições; saúde e força têm menos volume que massa {r}")
    # 4. frequências e divisões
    r=pg.evaluate("""()=>{const p=P();Object.assign(p,{loc:'gym',exp:1,focus:'',split:'auto',vr:0});const o={};for(const d of [2,3,4,5,6]){p.days=d;p.av={on:true,g:'hip',pr:[],dur:60};o[d]=PLN(p).sess.map(s=>s.n).join(',')}p.av.g='sau';p.days=3;o.sau3=PLN(p).sess.map(s=>s.n).join(',');return o}""")
    A(r["2"]=="Corpo inteiro A,Corpo inteiro B" and r["3"]=="Superior,Inferior,Corpo inteiro" and r["4"]=="Superior A,Inferior A,Superior B,Inferior B" and r["5"]=="Empurrar,Puxar,Pernas A,Superior,Pernas B" and r["6"]=="Empurrar A,Puxar A,Pernas A,Empurrar B,Puxar B,Pernas B" and r["sau3"]=="Corpo inteiro A,Corpo inteiro B,Corpo inteiro C",f"divisão conforme dias, nível e objetivo {r}")
    # 5. níveis: iniciante não recebe exercício avançado; volume cresce com a experiência; muitos dias para iniciante avisa
    r=pg.evaluate("""()=>{const p=P();Object.assign(p,{loc:'gym',days:4,focus:'',split:'auto',vr:0});p.av={on:true,g:'hip',pr:[],dur:90};const o={};for(const e of [0,1,2]){p.exp=e;const R=PLN(p);o['m'+e]=R.res.reduce((s,x)=>s+x[1],0);o['lv'+e]=Math.max(...R.sess.flatMap(s=>s.ex.map(x=>EXM[x[0]].lv)))}p.exp=0;p.days=6;o.av6=PLN(p).why.some(x=>x.includes('Iniciantes costumam'));p.days=3;o.av3=PLN(p).why.some(x=>x.includes('Iniciantes costumam'));return o}""")
    A(r["lv0"]==0 and r["lv1"]<=1 and r["m0"]<r["m1"]<r["m2"] and r["av6"] and not r["av3"],f"níveis: iniciante só nível 0, volume sobe com a experiência, aviso com 5+ dias {r}")
    # 6. exercícios e equipamentos indisponíveis, limitações, modo cuidadoso
    r=pg.evaluate("""()=>{const p=P();Object.assign(p,{loc:'gym',days:4,exp:2,focus:'',split:'auto',vr:0});const o={},all=R=>R.sess.flatMap(s=>s.ex.map(x=>x[0]));
     p.av={on:true,g:'hip',pr:[],dur:60,ex:['Supino reto','Agachamento']};let R=PLN(p);o.evita=!all(R).includes('Supino reto')&&!all(R).includes('Agachamento')&&R.res[0][2]>=R.res[0][1]*.6&&R.why.some(x=>x.includes('evitar 2'));
     p.av={on:true,g:'hip',pr:[],dur:60,ex:Object.keys(EX).filter(n=>EX[n].p.includes('Peitoral'))};R=PLN(p);o.semPeito=R.faltam.includes('Peitoral')&&R.why.some(x=>x.includes('Sem exercício disponível'))&&!all(R).some(n=>EX[n].p[0]==='Peitoral');
     p.av={on:true,g:'hip',pr:[],dur:60,eq:['H']};R=PLN(p);o.soHalter=all(R).every(n=>!EXM[n].eq.split('').some(c=>c!=='W'&&c!=='H'))&&all(R).length>8;
     p.av={on:true,g:'hip',pr:[],dur:60,eq:[]};R=PLN(p);o.soCorpo=all(R).every(n=>EXM[n].eq==='W')&&all(R).length>5;
     for(const l of ['o','c','l','j','q']){p.av={on:true,g:'hip',pr:[],dur:60,lim:[l]};R=PLN(p);o['lim'+l]=all(R).every(n=>!EXM[n].rg.includes(l))&&R.why.some(x=>x.includes('Limitações marcadas'))&&R.sess.every(s=>s.ex.length>=3)}
     p.av={on:true,g:'for',pr:[],dur:60,cu:true};R=PLN(p);const Rn=(p.av.cu=false,PLN(p));o.cuidado=all(R).every(n=>EXM[n].lv<=1)&&R.sess.every(s=>s.ex.every(x=>x[1]<=3))&&R.why.some(x=>x.includes('Modo cuidadoso'))&&R.res.reduce((s,x)=>s+x[1],0)<Rn.res.reduce((s,x)=>s+x[1],0)&&R.sess[0].ex[0][2]===PLN({...p,av:{on:true,g:'hip',dur:60}}).sess[0].ex[0][2];
     return o}""")
    A(all(r.values()),f"indisponíveis e limitações: evitar exercício, sem peitoral possível, só halter, só peso do corpo, cada região, modo cuidadoso {r}")
    # 7. prioridade e duração
    r=pg.evaluate("""()=>{const p=P();Object.assign(p,{loc:'gym',days:4,exp:1,focus:'',split:'auto',vr:0});const o={};p.av={on:true,g:'hip',pr:[],dur:60};const R0=PLN(p);p.av={on:true,g:'hip',pr:['Ombros','Bíceps'],dur:60};const R1=PLN(p);const g=(R,m)=>R.res.find(x=>x[0]===m);
     o.pri=g(R1,'Ombros')[1]>g(R0,'Ombros')[1]&&g(R1,'Bíceps')[1]>g(R0,'Bíceps')[1]&&g(R1,'Ombros')[2]>g(R0,'Ombros')[2];p.av={on:true,g:'hip',pr:['Ombros','Bíceps','Costas','Peitoral'],dur:60};o.max2=PLN(p).pr.length===2;
     p.av={on:true,g:'hip',pr:[],dur:30};const Rs=PLN(p);p.av={on:true,g:'hip',pr:[],dur:90};const Rl=PLN(p);o.dur=Rs.sess.every(s=>s.ex.length<=4)&&Rl.sess[0].ex.length>Rs.sess[0].ex.length&&Rs.why.some(x=>x.includes('Para caber em 30'));
     p.av={on:true,g:'hip',pr:[],dur:60};p.focus='glu';o.focoGlu=PLN(p).pr.join()==='Glúteos,Quadríceps';return o}""")
    A(all(r.values()),f"prioridades dão mais séries (máx. 2), duração limita a sessão, foco em glúteo vira prioridade {r}")
    # 8. recuperação por volume: muitos dias para iniciante reduz séries por sessão
    r=pg.evaluate("""()=>{const p=P();Object.assign(p,{loc:'gym',exp:0,focus:'',split:'auto',vr:0});p.av={on:true,g:'hip',pr:[],dur:60};const o={};for(const d of [3,6]){p.days=d;const R=PLN(p);o[d]=R.sess.reduce((s,x)=>s+x.ex.reduce((a,e)=>a+e[1],0),0)/d}return o}""")
    A(r["6"]<r["3"],f"iniciante com 6 dias faz menos séries por sessão que com 3 (recuperação) {r}")
    # 9. compatibilidade: sem avaliação, o plano é idêntico ao da v89
    snap=json.load(open(os.path.join(AQUI,"planos_v89.json")))
    r=pg.evaluate("""()=>{const o={},p=P();for(const loc of ['gym','cond','home','cal'])for(const d of [2,3,4,5,6])for(const e of [0,1,2])for(const f of ['','glu'])for(const v of [0,1,2]){Object.assign(p,{loc,days:d,exp:e,focus:f,vr:v,split:'auto'});p.av=[undefined,{on:false,g:'for',pr:['Costas']},'lixo',null,[1],{on:'true'}][(d+e+v)%6];if(p.av===undefined)delete p.av;const R=plansFor(p);o[[loc,d,e,f,v].join('|')]=JSON.stringify(R.keys.map(k=>[R.P[k][0],R.P[k][1].map(x=>[...x]),R.P[k][2]]))}return o}""")
    import hashlib
    dif=[k for k,v in r.items() if hashlib.sha1(v.encode()).hexdigest()[:12]!=snap.get(k)]
    A(len(r)==len(snap)==360 and not dif,f"sem avaliação (ou com dados inválidos), 360 planos idênticos aos da v89 {dif[:3]}")
    # 10. dados inválidos nunca quebram
    r=pg.evaluate("""()=>{const p=P(),o=[];for(const v of [null,1,'x',[],{on:true,g:'zz',pr:'a',dur:'9',eq:'B',ex:[1,{}],lim:{}},{on:true,pr:['Peitoral','Peitoral','nada'],ex:['Supino reto','Supino reto','inexistente'],lim:['o','x']}]){p.av=v;try{const a=avOf(p);if(a.on){const R=PLN(p);if(!R.sess.length)o.push('vazio')}if(!AVD.includes(a.dur)||a.pr.length>2||new Set(a.ex).size!==a.ex.length)o.push(JSON.stringify(v))}catch(e){o.push(String(e))}}return o}""")
    A(r==[],f"avaliação corrompida é normalizada sem erro {r}")
    # 11. minha rotina e estilo têm prioridade; troca de exercício continua valendo
    r=pg.evaluate("""()=>{const p=P();Object.assign(p,{loc:'gym',days:4,exp:1,focus:'',split:'auto',vr:0,rtOn:false});p.av={on:true,g:'hip',pr:[],dur:60};const base=plansFor(p),n0=base.P.A[1][0][0];
     p.sub={['A|'+n0]:'Supino com halteres'};const sw=plansFor(p);const okSub=sw.P.A[1][0][0]==='Supino com halteres'&&sw.P.A[1][0].o===n0&&sw.P.A[1][0][1]===base.P.A[1][0][1];delete p.sub;
     p.rtOn=true;p.rt=[{id:'x',n:'Minha',ex:[['Supino reto',3,'10',0]]}];const rt=plansFor(p);const okRt=rt.keys.length===1&&rt.P.A[0]==='Minha';p.rtOn=false;return{n0,okSub,okRt,pla:plansFor(p).keys.length}}""")
    A(r["okSub"] and r["okRt"] and r["pla"]==4,f"troca de exercício e 'Minha rotina' continuam funcionando com a avaliação {r}")
    # 12. tela do Perfil
    pg.evaluate("Object.assign(P(),{loc:'gym',days:4,exp:1,focus:'',split:'auto',vr:0,rtOn:false});delete P().av;delete P().sub;save();PFO.trn=true;tab='perfil';render()")
    A(pg.is_hidden("#avbox") and pg.input_value("#pavon")=="0","padrão: avaliação desligada e escondida")
    pg.select_option("#pavon","1");A(pg.is_visible("#avbox"),"ao escolher 'Pela minha avaliação', os campos aparecem")
    A(pg.eval_on_selector_all(".aveq:checked","e=>e.map(x=>x.value).sort().join('')")=="BFHMNP","equipamentos já vêm marcados conforme o local (academia)")
    for m in ["Ombros","Bíceps"]:pg.check(f".avpr[value='{m}']")
    pg.click(".avpr[value='Costas']")  # o terceiro é desmarcado pelo app
    A(pg.eval_on_selector_all(".avpr:checked","e=>e.length")==2,"no máximo 2 músculos prioritários")
    pg.select_option("#pavg","for");pg.select_option("#pavd","45");pg.check(".avlm[value='o']");pg.evaluate("document.querySelectorAll('#avbox details').forEach(d=>d.open=true)");pg.check(".avex[value='Barra fixa']")
    pg.select_option("#ploc","home");A(pg.eval_on_selector_all(".aveq:checked","e=>e.map(x=>x.value).join('')")=="H","trocar o local refaz os equipamentos padrão")
    pg.select_option("#ploc","gym")
    pg.evaluate("saveP()")
    r=pg.evaluate("()=>({av:avOf(P()),sf:!!P().splitFrom,on:avOn(P())})")
    A(r["on"] and r["av"]["g"]=="for" and r["av"]["pr"]==["Ombros","Bíceps"] and r["av"]["dur"]==45 and r["av"]["lim"]==["o"] and r["av"]["ex"]==["Barra fixa"] and r["av"]["eq"] is None and r["sf"],f"salvar guarda a avaliação (equipamento padrão fica 'null') {r['av']}")
    pg.evaluate("tab='perfil';PFO.trn=true;render()")
    A("Por que este plano?" in pg.inner_text("#app") and "Séries por semana" in pg.text_content("#app"),"mostra 'Por que este plano?' com o volume por músculo")
    pg.evaluate("tab='treino';render()");A(pg.evaluate("(()=>{const R=plansFor(P());return document.querySelector('#app').innerText.includes(R.P[R.keys[0]][1][0][0])})()") and not errs,f"aba Treino abre com o plano da avaliação {errs}")
    pg.reload();pg.evaluate("tab='perfil';PFO.trn=true;render()")
    A(pg.evaluate("avOn(P())")==True and pg.input_value("#pavg")=="for" and pg.eval_on_selector_all(".avpr:checked","e=>e.map(x=>x.value).join()")=="Ombros,Bíceps","a avaliação sobrevive ao recarregar o app")
    pg.select_option("#pavon","0");pg.evaluate("saveP()")
    A(pg.evaluate("plansFor(P()).keys.length")==4 and not pg.evaluate("plansFor(P()).why"),"voltar para 'Padrão do Gym.cal' restaura o plano de sempre")
    A(not errs,f"sem erro de JS {errs}")
    b.close()
print("FALHAS:",F);sys.exit(1 if F else 0)
