# Gym.cal v85 (1.0.6) — 13/11/2026

**Base para qualquer mudança futura: este ZIP (v85).** Integra o pacote "v84-corrigido" do ChatGPT (correções de segurança de dados, descritas em `CORRECOES-SEGURANCA-V84.md`). Ele partiu da v84 certa, então nada posterior foi perdido. Nenhuma funcionalidade nova, nenhuma tela nova; Free e Premium iguais à v84.

## O que entrou
| Correção do ChatGPT | Decisão |
|---|---|
| `save()`, `stash()` e `snapSet()` dizem se conseguiram gravar | **Mantida** |
| Cópia de segurança obrigatória antes de trocar de conta, combinar, atualizar pela nuvem, restaurar backup e nas escolhas da tela "Dados diferentes" | **Mantida** |
| Versão da nuvem que não cabe no aparelho não substitui a da tela ("Armazenamento cheio…") | **Mantida** |
| Os dois lados mudaram e não há cópia de base: pergunta em vez de combinar sozinho | **Mantida** |
| Edição feita enquanto um envio estava a caminho é enviada logo depois | **Mantida** |
| "Sair e limpar" só apaga depois de confirmar que a última versão chegou na nuvem | **Mantida** |
| Texto da loja: "mais de 950 alimentos" | **Mantida** |
| Cópia de segurança com o armazenamento quase cheio | **Ajustada**: a do ChatGPT exigia espaço para 3 cópias; se não coubesse, bloqueava a sincronização mesmo havendo espaço para 1. Agora tenta 3 e, se não couber, guarda só a mais recente. Só bloqueia quando nem 1 cabe. |

## Testado aqui (com resultado)
- `npm test`: 32 de front, 10 de servidor (provedores simulados), 9 de banco (PostgreSQL WASM). Todos passam.
- Todos os testes de navegador em `tests/navegador` (Chrome real): `FALHAS: []`.
- Teste novo `tests/navegador/falhas_sync.py`, com Supabase simulado (`servidor_falso.py`) e dois aparelhos (dois navegadores separados na mesma conta). Cobre:
  - armazenamento cheio (falha total, falha só numa chave e limite de espaço): aviso na tela, cópia salva intacta, 1 cópia em vez de 3, bloqueio quando nem 1 cabe, versão da nuvem que não cabe, restaurar backup sem espaço;
  - rede: sem conexão, volta da conexão, resposta perdida depois de o servidor gravar (sem duplicar), edição durante envio lento;
  - dois aparelhos: alterações diferentes, apagar num e registrar no outro, mesmo alimento registrado nos dois, falta de cópia de base (pergunta; "Combinar" junta os dois lados), sair e limpar sem internet.
  - **Rodado contra a v84 antiga, o mesmo teste falha em 7 pontos** (os que as correções resolvem). Contra o index do pacote do ChatGPT, falha só em "guardar 1 cópia em vez de 3" (o ajuste acima). Na v85 passa inteiro.
- Bateria antiga de 31 testes de interface: passa (só o `t4`, desatualizado desde a v67, falha como antes).
- 7 rodadas de ~340 toques aleatórios: nenhum erro de JavaScript, dados válidos ao reabrir.
- Dados salvos pelas versões v41, v51, v60, v67, v70, v77 e v84 abrem na v85 sem a tela de erro e com o diário idêntico.
- Login em aparelho limpo traz os dados da nuvem; layout em 320, 390 e 1280 px, claro e escuro, sem rolagem lateral; contraste conferido.
- Dados corrompidos de propósito: 9 de 11 casos abrem consertados. Os outros 2 já eram assim desde a v81 e **nenhuma versão do app grava dados nesse formato** (perfil sem `id`; rotina salva como texto). No primeiro, o diário fica guardado mas não aparece; no segundo, abre a tela de recuperação com o original intacto. Não mexi nisso agora para não arriscar a abertura de dados reais.
- Compilação Android no GitHub Actions com o código da v85: `npm ci`, `npm test`, montagem do projeto Android e APK de teste passaram (artefato `gymcal-android`). O APK não foi aberto em celular.

## Conflitos que continuam (investigados, sem migração)
A combinação de dois aparelhos compara registros pelo **conteúdo** (não há ID por refeição/treino). Com a cópia de base, isso resolve corretamente: alterações diferentes, apagar num e registrar no outro, e o mesmo alimento registrado duas vezes. Ficam três limitações, todas sem perda de dados:
1. **Mesmo registro editado nos dois aparelhos antes de sincronizar** (ex.: 100 kcal virou 200 num e 300 no outro): ficam os dois registros. A pessoa apaga o que não vale. Corrigir exige ID por registro em todos os dados salvos (migração), adiado de propósito.
2. **Os dois aparelhos ficam com o conteúdo inteiro idêntico** (fizeram exatamente as mesmas alterações sem internet): o app entende como uma alteração só. É a mesma regra que evita duplicar quando a resposta do servidor se perde, caso bem mais comum.
3. **Sem cópia de base e escolhendo "Combinar"**: um registro apagado num aparelho pode voltar. Por isso o app agora pergunta antes. "Usar os dados da conta" guarda uma cópia dos dados do aparelho antes de trocar. "Manter os deste aparelho" substitui a versão da nuvem; o outro aparelho guarda a versão dele numa cópia de segurança quando atualizar.

`updated_at` vem do relógio do aparelho, mas o servidor só aceita a gravação se a data for **igual** à que o aparelho viu por último. Relógio errado não faz perder dados; no máximo, num conflito do mesmo campo do perfil, vence o aparelho com relógio adiantado. **Não** colocar gatilho que troque `updated_at` por `now()` sem mudar o app junto (ver `TESTES-SUPABASE-REAL.md`).

## Depende de ambiente externo (não testado)
- Supabase real: migração, RLS com tokens reais, condição de data com o Postgres real, funções publicadas, exclusão de conta, e-mail de recuperação. Roteiro passo a passo em **`TESTES-SUPABASE-REAL.md`**.
- Celular real: armazenamento cheio de verdade (só simulado no navegador), modo avião, Android (Voltar, teclado, fonte grande, câmera), iPhone pela tela inicial.
- Google Play e RevenueCat: compra, renovação, cancelamento, expiração, restauração. A cobrança continua desligada (`RC_KEY=""`).

# Gym.cal v84 — 13/11/2026

**Base para qualquer mudança futura: este ZIP (v84).** Integra a proposta `ALTERACOES-UX-V84-PROPOSTA.md` (feita sobre a v83) depois de comparar o código item a item. Só a aba Hoje mudou; nenhuma regra, cálculo, treino, alimentação, ponto, rank ou sincronização.

| Proposta | Decisão | Motivo |
|---|---|---|
| Card "Seu treino de hoje" logo depois dos macros | **Mantido** | Acha o treino sem rolar as refeições. |
| Botão de alimento antes da lista, 52 px | **Ajustado** | Ficou logo abaixo do título "Refeições" (na proposta vinha acima do título). Texto "Registrar alimento" com ícone de + desenhado, em vez do caractere "+". Abre a refeição do horário, como antes. |
| Foco visível (teclado) no botão, no card de treino e no resumo da semana | **Mantido** | Acessibilidade. |
| Resumo "X de Y treinos nesta semana · rank" dentro de seção fechada | **Rejeitado** | A seção fechada ocupa a mesma linha que o resumo e esconde a informação atrás de mais um toque. O layout aprovado pede esse resumo discreto e visível. |
| Convite "Guarde seus dados na nuvem" dentro de seção fechada | **Rejeitado** | É o que protege contra perder dados (já aconteceu com usuário sem conta). Continua no fim da tela e some por 7 dias com "Agora não". |
| `.trhero .wk` com fonte 13 px em telas até 430 px | **Rejeitado** | Não havia corte nessas larguras; reduzir fonte piora a leitura. |

Teste novo: `tests/navegador/hoje_v84.py` (ordem dos blocos, refeição certa por horário 8h/12h/16h/21h, registro em "Ontem", card de treino, convite e resumo visíveis, foco pelo teclado).

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
