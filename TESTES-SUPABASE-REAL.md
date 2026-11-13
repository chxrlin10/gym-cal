# Gym.cal — roteiro de testes no Supabase real (v85)

Estes testes **não foram executados** pelo Claude nem pelo ChatGPT: dependem do projeto Supabase de verdade, de e-mail real e de aparelhos reais. Os mesmos fluxos de sincronização já passaram contra um servidor simulado (`tests/navegador/falhas_sync.py`), mas o simulado não prova RLS, formato real de datas, funções publicadas nem entrega de e-mail.

Marque cada item com ✅/❌ e guarde as respostas (prints ou texto). Se algo falhar, **pare** e mande o resultado antes de publicar.

---

## 0. Antes de começar (obrigatório)

1. Em cada aparelho que já usa o app: **Perfil › Backup e restauração › Gerar backup** e guarde o texto (bloco de notas, e-mail para você mesmo).
2. No Supabase: **Database › Backups** — confirme que existe backup recente (no plano grátis, baixe com `pg_dump` se não houver).
3. Ideal: criar um **segundo projeto Supabase só para teste** (homologação). Para usar o app com ele, faça uma cópia do `index.html` trocando a linha `const SB={u:"...",k:"..."}` pela URL e chave *publishable* do projeto de teste. Nunca coloque a chave `service_role` no HTML.
4. Crie duas contas de teste (A e B) com e-mails que você controla. Não use contas de outras pessoas.

Variáveis usadas nos comandos abaixo (terminal do computador):

```bash
export SBU="https://SEU-PROJETO.supabase.co"
export SBK="sb_publishable_..."          # chave pública (a mesma do index.html)
# token da conta A
export TA=$(curl -s "$SBU/auth/v1/token?grant_type=password" -H "apikey: $SBK" -H "Content-Type: application/json" \
  -d '{"email":"conta-a@exemplo.com","password":"SENHA_A"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
export UA=$(curl -s "$SBU/auth/v1/user" -H "apikey: $SBK" -H "Authorization: Bearer $TA" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
# repita para B: TB e UB
```

---

## 1. Migração e RLS

| # | Passo | Esperado |
|---|---|---|
| 1.1 | SQL Editor › colar `supabase/migration.sql` inteiro › Run | Termina sem erro. Rodar **de novo** também termina sem erro (é repetível). |
| 1.2 | Rodar `supabase/verify_rls.sql` | `relrowsecurity = true` nas 3 tabelas; `anon_rpc_must_be_false = false`; `user_rpc_must_be_false = false`; nenhum GRANT de escrita para `anon` em `entitlements`/`account_deletions`. |
| 1.3 | `curl "$SBU/rest/v1/user_data?user_id=eq.$UA" -H "apikey: $SBK" -H "Authorization: Bearer $TA"` | Só a linha de A (ou `[]` se A ainda não sincronizou). |
| 1.4 | Mesmo comando com `user_id=eq.$UB` e token de A | `[]` (A não vê B). |
| 1.5 | `curl -X PATCH "$SBU/rest/v1/user_data?user_id=eq.$UB" -H "apikey: $SBK" -H "Authorization: Bearer $TA" -H "Content-Type: application/json" -H "Prefer: return=representation" -d '{"data":{}}'` | `[]` — nada alterado em B. Confira no painel que os dados de B continuam iguais. |
| 1.6 | `curl -X POST "$SBU/rest/v1/user_data" ... -d "{\"user_id\":\"$UB\",\"data\":{}}"` com token de A | Erro 401/403 (`row-level security`). |
| 1.7 | `curl "$SBU/rest/v1/user_data" -H "apikey: $SBK"` (sem token) | `[]` ou 401. Nunca dados. |
| 1.8 | `curl -X POST "$SBU/rest/v1/entitlements" ... -d "{\"user_id\":\"$UA\",\"active\":true}"` com token de A | Erro de permissão. **Ninguém pode se dar Premium pelo app.** |
| 1.9 | `curl -X POST "$SBU/rest/v1/rpc/apply_rc_snapshot" ...` com token de A | Erro de permissão. |

## 2. Controle de conflito com datas reais

O app só grava se o `updated_at` da nuvem for exatamente o que ele viu por último. O servidor simulado imita isso; aqui confirmamos com o Postgres de verdade.

| # | Passo | Esperado |
|---|---|---|
| 2.1 | Entre com A no app, registre um alimento, espere "Sincronizado". Rode o GET do 1.3. | Volta `updated_at` com milissegundos, ex.: `2026-11-13T14:02:11.123+00:00`. |
| 2.2 | Copie esse valor em `OLD`. Registre outro alimento no app e espere sincronizar. Depois: `curl -X PATCH "$SBU/rest/v1/user_data?user_id=eq.$UA&updated_at=eq.$(python3 -c "import urllib.parse;print(urllib.parse.quote('$OLD'))")" -H "apikey: $SBK" -H "Authorization: Bearer $TA" -H "Content-Type: application/json" -H "Prefer: return=representation" -d '{"data":{}}'` | `[]` — gravação recusada porque a data mudou. **Os dados de A continuam intactos** (confira no app depois de "Sincronizar agora"). |
| 2.3 | Rode o GET de novo e copie o `updated_at` **atual** em `CUR`. Repita o PATCH com `updated_at=eq.<CUR codificado>` e corpo `-d "{\"updated_at\":\"$CUR\"}"` (não muda os dados) | Volta 1 linha. Mostra que a condição de data funciona com o formato real. |

> Não crie gatilho (trigger) que troque `updated_at` por `now()`: o app compara essa data com a data local para saber se houve mudança. Um gatilho faria todo envio parecer conflito. Se um dia quiser data do servidor, isso exige mudar o app junto.

## 3. Dois aparelhos reais (mesma conta A)

Use dois aparelhos (ex.: iPhone pelo Safari e um computador, ou dois celulares). Em cada passo, toque em **Perfil › Conta e sincronização › Sincronizar agora** nos dois ao final e compare o diário.

| # | Cenário | Esperado |
|---|---|---|
| 3.1 | Aparelho 1 registra "Arroz"; aparelho 2 sincroniza | Arroz aparece no 2. |
| 3.2 | Modo avião nos dois. 1 registra "Ovo", 2 registra "Pão". Tira o modo avião, sincroniza 1, depois 2, depois 1 | Os dois aparelhos com Ovo **e** Pão, sem repetir nada. |
| 3.3 | 1 apaga "Arroz"; 2 (em modo avião) registra "Café". Sincroniza | Arroz **não volta**; Café entra. |
| 3.4 | Modo avião nos dois; os dois registram "Banana 90 kcal" e o 2 também registra água. Sincroniza | Duas bananas (são duas porções de verdade). |
| 3.5 | Modo avião nos dois; editar o **mesmo** registro com valores diferentes (ex.: 200 e 300 kcal). Sincroniza | **Limitação conhecida:** ficam os dois registros (200 e 300). Nada se perde; apague o que não vale. |
| 3.6 | No 1, com internet desligada: Perfil › Conta e sincronização › Sair e limpar dados deste aparelho (toque duas vezes) | O app **não apaga** e avisa que não confirmou o envio. |
| 3.7 | No 1, Perfil › Conta e sincronização › Apagar da nuvem (toque duas vezes); depois sincronize o 2 | O 2 pergunta o que fazer (não reenvia sozinho). Os dados do 2 continuam no aparelho. |
| 3.8 | Internet ruim (3G fraco / sair do Wi‑Fi no meio do envio) | Mensagem "Sem conexão…", dados continuam no aparelho e saem na próxima alteração ou em "Sincronizar agora". |

Armazenamento cheio **não dá para reproduzir com segurança** num aparelho real; esse caso foi testado só no navegador com limite simulado.

## 4. Conta B no aparelho da conta A

| # | Passo | Esperado |
|---|---|---|
| 4.1 | No aparelho 1 (com dados de A), sair **sem apagar** e entrar com B | Aparece a pergunta sobre os dados do aparelho. Nada de A é enviado para B sem você escolher. |
| 4.2 | Antes de responder, registrar algo | Nada sobe para B (confira no GET de B). |
| 4.3 | Entrar de volta com A | Dados de A intactos. |

## 5. Exclusão de conta

Configurar antes (Edge Functions › Secrets): `RC_ENABLED=false` enquanto não houver RevenueCat. Publicar `delete-account` e `revenuecat-webhook` com a pasta `_shared`:

```bash
supabase functions deploy delete-account --project-ref SEU-PROJETO
supabase functions deploy revenuecat-webhook --project-ref SEU-PROJETO
```

| # | Passo | Esperado |
|---|---|---|
| 5.1 | Com uma conta descartável C: Perfil › Conta e sincronização › Excluir conta, seguindo a confirmação | Mensagem de sucesso; o app sai da conta. |
| 5.2 | Painel › Authentication | C não existe mais. |
| 5.3 | Table editor | Nenhuma linha de C em `user_data`, `entitlements`, `account_deletions`. |
| 5.4 | Tentar entrar com C | "E-mail ou senha incorretos." |
| 5.5 | Sem o secret `RC_ENABLED=false` (teste opcional) | A exclusão falha com aviso e **os dados continuam** — por isso o secret é obrigatório. |
| 5.6 | Página `excluir-conta.html` publicada | Abre no celular e explica como excluir sem o app (exigência da Google Play). |

## 6. Recuperação de senha

1. Authentication › URL Configuration › Redirect URLs: adicionar `https://chxrlin10.github.io/gym-cal/recuperar-senha.html`.
2. No app: Esqueci minha senha › e-mail da conta A.
3. Esperado: e-mail chega (confira spam), o link abre `recuperar-senha.html`, a nova senha funciona no app e a antiga não.

## 7. RevenueCat (só quando for ligar a cobrança)

Não fazer agora: `RC_KEY` continua vazio. Quando for ligar:
1. Secrets: `RC_WEBHOOK_SECRET`, `RC_SECRET_KEY`, `RC_APP_ID`, `RC_ENVIRONMENT=SANDBOX` (projeto de teste).
2. Webhook no RevenueCat apontando para a função, com o mesmo segredo. Botão "Send test event" → resposta 200.
3. Compra de teste por um testador de licença da Play: `entitlements` da conta passa a `active=true`; cancelar → continua até o fim do período; expirar → `active=false` e o app volta ao grátis sem perder dados.
4. Colocar a chave pública também no `index.html` do site (senão o site libera Premium para todos).

## 8. Android

- O APK de cada envio fica em GitHub › Actions › "Android" › Artifacts. A compilação é validada lá, não aqui (este ambiente bloqueia o Gradle).
- Ainda falta abrir num **Android real** (você não tem um): emprestar de alguém ou usar o teste interno da Play com um testador. Conferir: botão Voltar, teclado sobre os campos, fonte grande, modo escuro, câmera do código de barras, e sincronizar com o iPhone.

---

### O que já foi verificado sem ambiente real
- `npm test` (front com DOM simulado, funções com provedores simulados, migração em PostgreSQL WASM: isolamento A/B, anônimo, CASCADE, RPC).
- Navegador real contra Supabase simulado: armazenamento cheio, rede caindo, resposta perdida, edição durante envio, dois aparelhos, falta de cópia de base, saída sem internet.
- Compilação Android pelo GitHub Actions.
