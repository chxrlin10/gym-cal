# Gym.cal v83 — 13/11/2026

**Base para qualquer mudança futura: este ZIP (v83).**

## Estilo de divisão do treino (novo)
- No Perfil › Preferências de treino, campo "Estilo de divisão": Automático (pelos dias, como antes), Corpo inteiro, Superior / Inferior, Push / Pull / Legs, ABCDE (um grupo por dia), Arnold (peito e costas / ombros e braços / pernas) e Superior / Inferior / Corpo inteiro.
- **Grátis:** Automático, que já monta corpo inteiro, superior/inferior, ABCDE ou Push/Pull/Legs conforme os dias. **Premium:** escolher o estilo, independente dos dias. No grátis, os outros estilos aparecem com ★ e um convite, sem sair da tela.
- Os dias por semana viram só a frequência; o app roda a sequência do estilo e, ao trocar de estilo, recomeça do primeiro dia.
- Versões para academia, condomínio, casa e calistenia, só com exercícios que servem para o local. "Minha rotina" continua tendo prioridade.
- Se o Premium vencer, volta ao Automático; o estilo fica guardado e volta se assinar de novo.
- Sequência, pontos, rank e cálculo de calorias não mudam.
- Teste: `tests/navegador/estilos_treino.py`.

# Gym.cal v82 — 12/11/2026

**Base para qualquer mudança futura: este ZIP (v82).** Junta a v81 do Claude com o pacote "v81 — alimentos e busca" do ChatGPT, que tinha partido da "v80" dele e não tinha as correções v80.1/v81.

## v82 (agora)
- Catálogo com 951 alimentos: base anterior + 574 da Tabela TACO (Unicamp, 2011) + 5 espetinhos estimados. Valores conferidos por amostragem com a TACO e por coerência entre calorias e macros (nenhuma divergência).
- Busca nova do ChatGPT (palavras em qualquer ordem, acentos, sinônimos como aipim/macaxeira, 20 resultados e "Mostrar mais").
- **Corrigido:** a busca nova punha alimentos crus e itens raros no topo ("arroz" mostrava "Arroz carreteiro" e arroz cru antes do cozido; "ovo" mostrava ovo de codorna cru). Arroz cru tem quase 3× as calorias do cozido, então era fácil registrar errado. Agora vêm primeiro os alimentos que a pessoa já usou, depois o catálogo do dia a dia, depois a TACO; cru de grão, carne e feijão vai para baixo.
- **Corrigido:** a linha de resultado da TACO sobrepunha o texto da fonte às calorias.
- Textos encurtados: "Tabela TACO" na lista; ao escolher, uma linha com a fonte em vez de um bloco longo; medida "porção (≈ 100 g)".
- Teste: `tests/navegador/busca_alimentos.py`.

# Gym.cal v81 — 12/11/2026

**Base para qualquer mudança futura: este ZIP (v81).** Ele junta:
- a v80 do Claude (revisão da v79 + ajustes de uso no celular),
- a v80.1 (correção de dados antigos que travavam o app),
- os 16 exercícios novos do ZIP "v80 catálogo ampliado" do ChatGPT, que tinha partido da v79 e não tinha a v80.1.

## v81 (agora)
- 16 exercícios novos do ChatGPT aplicados sobre a v80.1, sem perder nenhuma correção anterior. Testes do ChatGPT para eles incluídos (28 testes de front).
- Carga e repetições das séries limitadas a 0–1000 kg e 0–200 reps ao concluir o treino. Antes, um número absurdo ou negativo digitado gerava dados que o app novo recusava ao abrir e que travavam a sincronização.
- Meta de peso fora de 25–400 kg é ignorada ao salvar o Perfil.
- O conserto automático de dados antigos agora também cobre números acima de 1 bilhão e meta de peso negativa.

## v80.1
- A v80 recusava dados salvos por versões anteriores fora do formato novo (ex.: cardio acima de 300 min, número salvo como texto) e mostrava "Não consegui ler os dados", com o botão de apagar como ação principal. Um usuário perdeu os dados locais assim.
- Agora o app corrige esses formatos ao abrir, guarda o original em `gymcal2_copia` e, em último caso, abre como as versões anteriores. A mesma correção vale para dados vindos da nuvem e de backups antigos; backups maliciosos continuam recusados.
- A tela de erro mostra "Copiar meus dados" e esconde o apagar dentro de "Apagar e começar do zero".
- Teste: `tests/navegador/dados_antigos.py`.

# Gym.cal v80 — revisão do Claude sobre a v79 (12/11/2026)

Base: o ZIP v79. Naquela etapa nada foi publicado; a cobrança continua desligada (`RC_KEY=""`).

## O que foi corrigido
1. **Minhas refeições** fechava o painel ao registrar ou ao tocar em remover; a confirmação de remoção ficava escondida. Agora o painel continua aberto e mostra "1 porção registrada em Jantar ✓".
2. Textos das receitas: "0.5 porção(ões)" virou "0,5 porção"; "rende 1 porções" virou "rende 1 porção". A lista ficou compacta: uma linha por refeição salva, com porções e refeição lado a lado ao abrir; a refeição já vem marcada pelo horário.
3. **Troca de alimento** dobrava a altura do cardápio (uma linha "Substituir alimento" para cada item). Agora o "Substituir" fica na mesma linha do alimento. O botão da refeição inteira, que também se chamava "Trocar", virou "Outra opção".
4. **Último treino** mostrava data no formato 2026-11-10; agora "10 de nov", com texto mais curto.
5. **Revisão semanal**: "Escolher este foco" continuava aparecendo depois de escolhido, e a data vinha em formato técnico. Corrigido; textos encurtados. O título da seção no Progresso ainda dizia "Relatório"; agora "Revisão da semana e meta inteligente".
6. Perfis antigos não sabiam da nova "Atividade fora da academia": agora aparece um aviso no editor de Objetivos até a pessoa escolher e salvar.
7. "Apagar backup da nuvem" desconectava a conta sem dizer; a mensagem agora explica.
8. "Esqueci minha senha" tinha área de toque de 32 px; agora 44 px.

## O que foi verificado aqui
- `npm ci`, `npm test` (44 testes do pacote) e `npm run android:prepare` (Capacitor 8.6.0 + RevenueCat 14.1.0; plugin encontrado). Dois textos de teste foram mantidos compatíveis.
- APK **não** compilado: o ambiente bloqueia o download do Gradle/Google Maven. Quem compila é o GitHub Actions.
- Testes no Chrome real (tests/navegador): receitas com rendimento e porções, troca individual (calorias, macros, lista e "Adicionar ao diário"), revisão semanal e foco, último treino junto do exercício, persistência ao reabrir, perfis isolados, backup completo e backup malicioso rejeitado, Premium vencido (receitas visíveis, adicionar/trocar pedem Premium, diário intacto), assinatura simulada.
- Bateria anterior de 31 testes de interface: passa (o `t4`, desatualizado desde a v67, continua falhando).
- Atualização: dados criados pelas versões v41, v51, v60, v67, v70 e v77 abrem na v80 sem a tela "Não consegui ler os dados" e com o diário idêntico.
- 7 rodadas de ~340 toques aleatórios: sem erro de JavaScript e estado válido após reabrir.
- Layout em 320, 390 e 1280 px, claro e escuro: sem rolagem lateral; contraste de texto conferido.
- Revisão de leitura: migração SQL, RLS, funções de exclusão e webhook, página de recuperação de senha, build Android.

## O que depende de ambiente real (não verificado)
- Celular Android de verdade (visual, botão Voltar, teclado, fonte grande, TalkBack, desempenho com meses de dados).
- Supabase de produção: migração, RLS com JWT reais, funções publicadas, e-mail de recuperação, exclusão de conta.
- Compra, renovação, cancelamento, expiração e restauração pela Google Play / RevenueCat.

## Atenção antes de publicar
- **Site web libera tudo**: com `RC_KEY` vazio no index.html do GitHub Pages, o site deixa o Premium aberto para qualquer pessoa, mesmo quando o Android estiver cobrando. Ao ligar a cobrança, coloque a chave pública também no index.html do site.
- **Exclusão de conta**: a função nova exige o secret `RC_ENABLED=false` (enquanto não houver RevenueCat) ou `RC_SECRET_KEY`. Sem isso, a exclusão falha — e a Play exige exclusão funcionando.
- **Compras de teste** só liberam com `RC_ENVIRONMENT=SANDBOX`.
- **Dados reais**: o app novo valida os dados salvos ao abrir. Antes de instalar no seu celular e no da sua namorada, gere um backup no app atual.
