# Supabase — implantação v77 (ainda não executada no projeto real)

1. Faça backup do banco e exporte os dados do app. Teste primeiro em projeto de homologação.
2. Execute **migration.sql inteiro**. Ele cria/configura user_data, entitlements, account_deletions, RLS e a RPC de reconciliação. Substitui as políticas anteriores dessas três tabelas; não remove registros. Duplicatas/órfãos fazem a transação falhar: inspecione, não apague automaticamente.
3. Execute verify_rls.sql e guarde o resultado. user_data: apenas próprio UUID; entitlements: leitura própria, escrita só service_role; account_deletions: leitura própria, escrita só service_role; RPC não executável por anon/authenticated.
4. Publique as duas funções, incluindo a pasta `_shared`. `config.toml` define verify_jwt=false; ambas fazem sua própria autenticação.
5. Configure secrets do servidor:
   - RC_WEBHOOK_SECRET: segredo longo, igual ao Authorization `Bearer ...` do webhook.
   - RC_SECRET_KEY: chave **secreta de API v1** do projeto RevenueCat, com acesso de leitura/exclusão de clientes. Nunca colar no HTML/GitHub.
   - RC_APP_ID: identificador do aplicativo no RevenueCat (não é o package Android).
   - RC_ENVIRONMENT: PRODUCTION; para homologação isolada, SANDBOX. Não misture testes e produção na mesma base.
   - RC_ENABLED: true quando cobrança estiver habilitada. Enquanto não houver RevenueCat/cobrança, defina explicitamente false para permitir exclusão sem esse fornecedor. Quando há RC_SECRET_KEY, a exclusão o consulta mesmo com RC_ENABLED=false.
6. Publique recuperar-senha.html no GitHub Pages. Adicione `https://chxrlin10.github.io/gym-cal/recuperar-senha.html` à lista de Redirect URLs do Supabase. O template padrão com ConfirmationURL deve preservar redirect_to; alternativamente use link token_hash/type=recovery para essa página. Teste em um e-mail real e confira SMTP/entrega.
7. Configure webhook no RevenueCat com a URL da função e o segredo do item 5. TEST retorna 200 sem gravar assinatura; testar compras reais de licença é necessário para confirmar todo o caminho.

## Testes obrigatórios com duas contas
- JWT de A: ler/escrever apenas A. GET de B não retorna dados; POST/PATCH com UUID B é negado. Anônimo não acessa as tabelas. Authenticated não escreve entitlements nem chama apply_rc_snapshot.
- A em dois aparelhos: alterações independentes; exclusão de refeição versus nova refeição; conflito simultâneo; modo avião; retomada.
- B sem backup no aparelho de A: editar antes de responder à pergunta NÃO pode enviar dados. Só confirmar explicitamente autoriza.
- Exclusão: tentar upload durante/depois da exclusão; nada deve reaparecer. Excluir usuário deve fazer CASCADE nas três tabelas.
- Simular falha do RevenueCat durante exclusão: registro account_deletions bloqueia novos uploads; dados Supabase permanecem até concluir. Usuário deve repetir a exclusão; suporte deve acompanhar pendências, não esquecê-las.
- Repetir webhook e inverter ordem de eventos. A função consulta o estado atual; a RPC só aceita snapshot posterior ao já gravado.
- Restaurar em outra conta: testar a política de transferência escolhida no RevenueCat. Nenhum UUID recebe assinatura só por aparecer em TRANSFER.

Excluir cliente no RevenueCat não cancela a assinatura na Play. A função não solicita cancelamento automático.
