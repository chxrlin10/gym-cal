# Gym.cal — histórico das versões do ChatGPT

> Versão atual: **v85 / 1.0.6** (Claude, 13/11/2026). Leia primeiro `REVISAO-CLAUDE.md` e, antes de publicar, siga `TESTES-SUPABASE-REAL.md`.
> **Use SEMPRE o ZIP mais recente que o Claude devolveu como base.** Os pacotes "v80" e "v81" do ChatGPT partiram de versões antigas e não tinham as correções do Claude (dados antigos que travavam o app, limites de carga, ajustes de tela). A v82 junta tudo.

## "v81" do ChatGPT (alimentos e busca), incorporada na v82
- Catálogo total 951 entradas: base antiga preservada + TACO com preparo/corte + 5 estimativas explícitas de espetinhos. Não são 951 ingredientes únicos; diferentes preparos contam separadamente.
- 574 linhas da publicação foram extraídas com energia/macros completos. Deduplicação por nome normalizado contra a base existente. Consulte ALIMENTOS-FONTES.md para fonte, licença e limites.
- Corrigida busca literal limitada a 8: palavras em qualquer ordem, prefixos, acentos e sinônimos de carne bovina/grelhados, aipim/macaxeira e pão de sal. 20 resultados por página e Mostrar mais.
- Seleção de alimento TACO exibe fonte e preparo. Espetinhos não têm peso inventado por unidade: referência 100 g, para ajustar conforme peso comestível pronto, sem palito.
- 51 testes locais passam; preparação Android funciona. Validação visual em aparelho real e implantação continuam pendentes.

## "v80" do ChatGPT (16 exercícios), incorporada na v81 do Claude
- 16 exercícios adicionais: supinos inclinado com barra, neutro e fechado; crucifixo inclinado; puxada supinada; remada baixa com barra; elevações lateral na polia e frontal com anilha; roscas inversa e na polia; tríceps unilateral na polia; extensora/flexoras unilaterais; terra romeno com halteres; agachamento no Smith.
- Cada entrada tem músculos, equipamento, três passos, dica e esquema animado lateral no formato existente. As variantes compartilham geometria esquemática compatível; pegada, máquina e bilateralidade não são reproduções anatômicas detalhadas. Validar visualmente em Android.
- Integradas ao editor, trocas por músculo e grupos de variação. Máquinas/polias ficam fora das trocas de casa e calistenia. Rotinas salvas e nomes anteriores preservados.
- Referências gerais consultadas: https://www.nasm.org/workout-exercise-guidance e https://www.acefitness.org/resources/everyone/exercise-library/equipment/ . Textos próprios; não são endosso ou certificação.
- Testes incluem renderização das 16 rotinas, coordenadas finitas e filtros de ambiente.

## Novidades v79
- Minhas refeições: salve uma combinação registrada no diário, nome e rendimento. Adicione frações/múltiplos de porção em qualquer refeição e na data selecionada. Ingredientes e macros são snapshots, preservando o registro original. Limite de 60 combinações por perfil.
- Receitas ficam legíveis e removíveis após expiração; criação e adição rápida exigem Premium. Histórico do diário continua acessível. Sem editor separado: para atualizar, registre a combinação alterada e salve com outro nome, removendo a anterior se desejar.
- Substituição individual no cardápio: alternativas da mesma categoria, porção aproximada pelas calorias e comparação de proteína. Recalcula macros, lista e lançamento no diário; respeita alimentos evitados e despensa. Não equivale a substituição nutricional completa ou filtro de alergênicos.
- Trocas são guardadas por perfil e assinatura do cardápio-base. Novo cardápio ou mudança de meta/alimentos pode invalidar a troca. A sequência de variações existente continua temporária.
- Último treino visível junto às séries; histórico básico gratuito preservado. Sugestão de progressão preexistente permanece opcional.
- 44 testes locais passam (25 front DOM simulado, 10 funções com provedores simulados e 9 PostgreSQL/WASM). Projeto Android preparado; não equivale a APK testado ou certificação visual.
- Sem telemetry nova, sem publicação, sem ativação de cobrança. Próximo passo: uso real em Android e compra de teste Google Play.

## Novidades v78
- Preferências de alimentos por perfil, persistidas no backup e sincronização; aplicadas somente ao cardápio da despensa. Não é filtro de alergênicos.
- Lista agregada de alimentos do cardápio de 1 dia, com quantidades conforme preparo indicado e cópia; não estima estoque nem converte pesos cozidos em pesos crus.
- Revisão dos últimos 7 dias substitui a nota visual: cobertura dos registros, dias distintos de treino, pesagens recentes e um foco que a pessoa escolhe salvar. Não altera calorias, ranking ou pontos.
- Oferta contextual com três benefícios e exemplo explicitamente ilustrativo. Corrigido texto que prometia ajuste automático das metas.
- Preparação por tempo, troca de item individual, receitas e analytics de conversão NÃO foram implementados nesta etapa. Troca por refeição já existente foi preservada.
- Novos testes de regressão: preferências isoladas por perfil, backup, lista sem mutação do diário, revisão com poucos dados, treinos duplicados, foco persistido e escape de contexto.

## Estado da entrega
- Código corrigido, não implantado. Cobrança continua desligada no arquivo (`RC_KEY=""`).
- O front continua em um único index.html, sem framework. No Android há um bundle separado gerado somente para carregar o wrapper oficial do RevenueCat.
- Pacote 1.0.1; Capacitor 8.6.0, RevenueCat 14.1.0, Node22+, Java21, API36. As versões são travadas em package-lock.json.
- Os arquivos gerados android/, www/ e node_modules/ não fazem parte do ZIP; os scripts os recriam. Não há keystore nem credenciais secretas.

## Corrigido
1. Gate explícito de sincronização: nenhuma gravação automática com decisão de conta pendente ou dono local diferente; renovação do token e respostas de compra vinculadas ao UUID/geração da sessão. Uploads enfileirados e consultas de sincronização compartilhadas.
2. Mesclagem de perfis por campo usando snapshot-base: mudar peso em A e registrar refeição em B não descarta mais o peso. Se ambos mudarem o MESMO campo, prevalece o estado mais recente; o stash mantém a cópia anterior quando possível. Rotinas são tratadas como unidade em conflito simultâneo.
3. Limpeza explícita encerra a sessão local e remove stash, snapshots, rascunhos e timers. Apagar local não pretende apagar backup remoto; ao entrar novamente, o backup pode voltar — comportamento intencional. Exclusão de conta é uma ação separada.
4. Importação/nuvem validadas antes da troca de estado. Campos numéricos não aceitam HTML; chaves de prototype pollution são rejeitadas. Campos sensíveis renderizados passam por escape. Backup inválido não substitui o estado. Falha na leitura inicial preserva o texto original e abre recuperação.
5. Formulários preservam valores/selects/checkboxes em renderizações da mesma sessão; dados carregados de outra conta não recuperam esses rascunhos anteriores.
6. Alimento manual rejeita zero/negativo e quantidades inválidas; dados nutricionais externos são limitados a números finitos.
7. Meta inteligente usa cut/keep/bulk corretamente. Macros incompatíveis com o orçamento calórico recebem distribuição limitada (30% proteína/30% gordura/restante carboidratos), com aviso para orientação individual. Isso é fallback, não prescrição clínica individual.
8. Atividade fora da academia agora é selecionável. Novos perfis começam em 1,2; existentes conservam a meta antiga até revisar/salvar o Perfil. Percentuais de exercício 50%/75% permanecem como preferências, com texto sem garantia de precisão. Macros usam meta-base, informado na tela.
9. Gordura corporal fora da faixa estimável deixa de aparecer como percentual impossível; retirada margem fixa de erro de cardio. Estimativas de musculação continuam baseadas no número de séries, explicitamente aproximadas.
10. Assinatura atualizada ao retomar/reconectar e por listener; respostas antigas descartadas; cache offline usa requestDate do SDK. Gerenciamento de assinatura acessível também sem confirmação de Premium.
11. Webhook reconcilia estado atual via API v1 RevenueCat, inclusive transferências, ambiente, validade, grace period e reembolso. RPC só aplica snapshot mais recente. Eventos repetidos não concedem acesso extra. Não há trilha de auditoria por event.id: idempotência é pelo snapshot atual.
12. Migração SQL completa, repetível, com RLS/GRANTs e CASCADE. Função de exclusão marca pendência, solicita remoção do RevenueCat e exclui auth.users; falha mantém dados Supabase e impede novos uploads até concluir.
13. Recuperação de senha via página hospedada independente, sem enviar dados locais automaticamente. Requer publicar página e autorizar redirect URL.
14. Build com AAB assinado opcional, ícones vetoriais derivados do favicon existente e exclusão de backup Android. Removida dependência antiga de geração de assets; não usa arquivo icon.b64 ausente.
15. Fontes externas removidas (fallback system-ui); botões pequenos ampliados, contraste do aviso laranja aumentado e Tab contido no diálogo inicial.
16. Ranking: mantidas pontuações, penalidades, ranks, calendário de ativação e pausas. Corrigido descarte de metas/pausas históricas e limite de 1.200 dias que podia mudar pontuação antiga. Dados já descartados pela versão antiga não são inventados/reconstruídos.

## Validação feita
- `npm test`: testes de JavaScript com DOM simulado, webhooks/RevenueCat simulados e PostgreSQL/WASM isolado.
- Testes de banco executam a migração duas vezes; comprovam isolamento A/B, bloqueio de anônimo, proibição de escrever entitlements/chamar RPC com authenticated, precedência de snapshot e CASCADE.
- Build web/native bridge gerado com esbuild; `cap add` e `cap sync` concluídos; plugin nativo encontrado; XML Android validado.
- Não foram executadas compras reais, funções no Supabase real, teste visual/TalkBack ou benchmark em celular simples.
- Tentativa de APK parou antes da compilação: ambiente não conseguiu baixar a distribuição do Gradle (rede). Não existe APK/AAB aprovado nesta entrega.

## Próximos passos do Claude (sem reescrever o app)
1. Revisar diff e executar `npm ci`, `npm test`, `npm run android:prepare`. Conferir Actions e compilar APK; testar visualmente todas as abas com teclado, fonte ampliada, modo escuro, botão Voltar e edge-to-edge.
2. Fazer backup e aplicar `supabase/migration.sql` em homologação. Ler `supabase/EXECUTAR.md`, configurar secrets e publicar as duas funções com `_shared`. Repetir testes A/B por REST com JWTs reais.
3. Publicar as páginas legais e recuperar-senha.html. Testar SMTP/recuperação e exclusão sem acesso ao app. Conferir nome/contato do responsável e retenção real dos fornecedores antes de afirmar conformidade.
4. Configurar assinaturas/ofertas e transferência no RevenueCat, ativar chave pública SOMENTE após testar. Chave secreta fica só no Supabase. Usar ambientes separados para sandbox e produção.
5. Testar compra pendente, confirmação, cancelamento, renovação, expiração, carência, account hold, reembolso, restauração entre contas/dispositivos e operação offline. Verificar SDK/servidor e cache em conjunto.
6. Gerar keystore seguro, guardar cópia, configurar secrets GitHub e gerar release. Conferir versionCode maior que qualquer anterior, exigências do Console, declaração de saúde/dados, testes fechados e material da loja.
7. Fazer teste de volume com 2 anos de dados/4 perfis em aparelho simples. O armazenamento continua localStorage; snapshots e stashes consomem quota. A migração para IndexedDB não foi feita. Aviso de falha de armazenamento permanece.
8. Fluxos ainda merecem ensaio concorrente: editar durante saída/exclusão, desligar rede no meio de upload, restauração com conflito, aparelho antigo voltando depois de exclusão. Testes locais não substituem isso.

## Arquivos-chave
- index.html: app atualizado.
- supabase/migration.sql: executar inteiro antes das funções novas.
- supabase/functions/: webhook, exclusão e helper server-only.
- scripts/ + .github/workflows/android.yml: geração/assinatura.
- tests/: testes reproduzíveis. Não enviados no app Android.
- PREMIUM.md / LOJA.md / supabase/EXECUTAR.md: configuração e testes reais pendentes.

## Referências técnicas usadas
https://capacitorjs.com/docs/updating/8-0
https://www.revenuecat.com/docs/api-v1/customer-info-model
https://www.revenuecat.com/docs/integrations/webhooks/event-types-and-fields
https://supabase.com/docs/guides/auth/auth-email-templates
https://support.google.com/googleplay/android-developer/answer/11926878
