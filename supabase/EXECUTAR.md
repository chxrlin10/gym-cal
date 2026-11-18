# Supabase — implantação v93 (ainda não executada no projeto real)

O app publicado no GitHub Pages já usa esta estrutura. Faça tudo numa sequência só, num horário de pouco uso.
Se possível, teste antes num projeto de homologação.

## 1. Backup
1. Table Editor → `user_data` → Export → CSV. Repita com `entitlements`. Guarde em lugar privado: são dados de saúde.
2. SQL Editor → cópia dentro do banco, num schema que a API não expõe:
   ```sql
   create schema if not exists backup;
   create table backup.user_data_AAAAMMDD as table public.user_data;
   create table backup.entitlements_AAAAMMDD as table public.entitlements;
   ```
   **Apague o schema `backup` depois que a migração for validada** (item 8): `drop schema backup cascade;`

## 2. Diagnóstico (só leitura)
Rode a consulta de diagnóstico do AUDITORIA.md e confira a estrutura atual antes de seguir.
A migração já aborta sozinha se encontrar algo incompatível, mas é melhor saber antes.

## 3. Secrets ANTES de publicar as funções
Edge Functions → Secrets. `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` já existem por padrão.
- `RC_ENABLED`: **`false` enquanto não houver cobrança**. Sem isso e sem `RC_SECRET_KEY`, a exclusão de conta responde 503 sem mudar nada.
- Só quando a cobrança for ligada:
  - `RC_SECRET_KEY`: chave **secreta de API v1** do RevenueCat (leitura e exclusão de clientes). Nunca no HTML nem no GitHub. Com ela, a exclusão também remove o cliente no RevenueCat.
  - `RC_WEBHOOK_SECRET`: segredo longo, igual ao `Authorization: Bearer ...` configurado no webhook.
  - `RC_APP_ID`: identificador do app no RevenueCat (não é o package Android).
  - `RC_ENVIRONMENT`: `PRODUCTION`, ou `SANDBOX` num projeto de homologação isolado. Não misture os dois na mesma base.

## 4. Migração
SQL Editor → cole **migration.sql inteiro** → Run.
- Ela confere a estrutura e os dados existentes antes de mudar qualquer coisa. Se algo não bater (user_id repetido ou nulo, linha de usuário que não existe mais, coluna com outro tipo), aborta com uma mensagem começando por `Gym.cal:`.
- **Se der qualquer erro:** rode `rollback;`, copie a mensagem e pare. Nada foi alterado (é tudo uma transação só).
- Se aparecer erro de `lock_timeout`, algum acesso estava usando a tabela: espere alguns segundos, rode `rollback;` e tente de novo.
- Não apaga linhas. Troca as policies dessas três tabelas pelas do app (inclusive as permissivas feitas à mão).

## 5. Conferência
Rode `verify_rls.sql` e guarde o resultado. Esperado:
- `user_data`: só o próprio UUID;
- `entitlements` e `account_deletions`: leitura própria, escrita só pelo service_role;
- `apply_rc_snapshot`: `false` para anon e authenticated.

## 6. Publicar as funções, logo depois da migração
Publique `delete-account` e `revenuecat-webhook` com a pasta `_shared`. O `config.toml` define `verify_jwt=false`, porque as duas fazem a própria autenticação.
Até este passo, continua no ar a versão antiga e desconhecida de `delete-account`, por isso não deixe intervalo entre os itens 4 e 6.

## 7. Recuperação de senha
Adicione `https://chxrlin10.github.io/gym-cal/recuperar-senha.html` às Redirect URLs (Authentication → URL Configuration).
O template de e-mail com ConfirmationURL precisa preservar `redirect_to`; outra opção é um link `token_hash`/`type=recovery` para essa página. Teste com um e-mail real e confira a entrega (SMTP).

## 8. Testes obrigatórios com duas contas (validação)
- JWT de A lê e escreve apenas A. GET de B não retorna dados; POST/PATCH com o UUID de B é negado. Anônimo não acessa as tabelas. Authenticated não escreve entitlements nem chama apply_rc_snapshot.
- A em dois aparelhos: alterações independentes; exclusão de refeição versus nova refeição; conflito simultâneo; modo avião; retomada.
- B sem backup no aparelho de A: editar antes de responder à pergunta NÃO pode enviar dados. Só a confirmação explícita autoriza.
- Exclusão de conta pelo app: precisa responder ok e apagar em CASCADE as três tabelas. Tentar enviar dados durante e depois da exclusão: nada pode reaparecer.
- Com cobrança ligada, simular falha do RevenueCat durante a exclusão: o registro em account_deletions bloqueia novos envios e os dados ficam até concluir. O usuário repete a exclusão; o suporte acompanha as pendências.

Tudo certo? **Apague o schema `backup`** (item 1).

## 9. Webhook do RevenueCat (só quando a cobrança for ligada)
Configure o webhook **depois** que a função estiver publicada e o item 8 passar: URL da função + o segredo do item 3.
O evento TEST retorna 200 sem gravar assinatura. Para confirmar o caminho completo, teste compras reais de licença.
- Repetir o webhook e inverter a ordem dos eventos: a função consulta o estado atual, e a RPC só aceita um snapshot mais novo que o gravado.
- Restaurar em outra conta: testar a política de transferência escolhida no RevenueCat. Nenhum UUID recebe assinatura só por aparecer em TRANSFER.

Excluir o cliente no RevenueCat não cancela a assinatura na loja. A função não pede cancelamento automático.
