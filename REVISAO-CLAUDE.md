# Gym.cal v80 — revisão do Claude sobre a v79 (12/11/2026)

Base: o ZIP v79. Nada foi publicado (GitHub, site ou app) e a cobrança continua desligada (`RC_KEY=""`).

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
