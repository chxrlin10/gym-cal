## Atualização v79
Minhas refeições/receitas: salvar a partir do diário, informar rendimento e lançar porções. Troca individual de alimentos recalcula calorias e macros; lista acompanha a troca. Referência do treino anterior junto das séries. Tudo por perfil, com validação de backup. Após expiração, receitas salvas continuam consultáveis; criação/lançamento rápido são Premium. Cobrança permanece desligada. Não há garantia de conversão: testar usabilidade e retorno de usuários antes de novas funções.

## Atualização v78
A tela de oferta apresenta planejamento da despensa, revisão semanal e evolução no treino. Preferências por perfil excluem alimentos do modo despensa; lista do dia agrega porções e permite copiar. Revisão mostra últimos 7 dias, evita julgamentos com poucos registros e permite salvar um foco. Não muda ranking, meta ou compra. Cobrança segue desligada com RC_KEY vazio. Recursos novos não têm chamadas externas nem telemetria.

# Premium — v77

Cobrança permanece DESLIGADA no HTML entregue: `RC_KEY=""` mantém PREM_OPEN. Não houve compra nem configuração nas suas contas.

## Configuração
- Google Play: produto `gymcal_premium`, planos base mensal/anual; preços pretendidos R$12,90/mês e R$99,90/ano; sem teste grátis.
- RevenueCat: entitlement `premium`, offering atual com pacotes MONTHLY/ANNUAL, produtos vinculados; configure credenciais da Play e a política de transferência/restauração.
- Servidor: seguir `supabase/EXECUTAR.md` e executar a migração ANTES de publicar as funções novas.
- Cliente Android: variável de repositório GitHub `RC_PUBLIC_KEY=goog_...` ou preencher RC_KEY no HTML. É chave pública. Build release exige chave; APK debug pode permanecer aberto.
- Se quiser Premium também no site web, preencher RC_KEY no index publicado; o site consulta Supabase e não tenta comprar fora da Play.

## O que mudou
- SDK oficial importado e empacotado pelo esbuild para Android; interface continua em um HTML, sem framework.
- Capacitor 8.6.0 + purchases-capacitor 14.1.0 (peer dependency >=8), Node 22+, Java 21, target API36.
- Operações vinculadas ao UUID e geração de sessão; respostas atrasadas são descartadas.
- Atualização ao retomar, reconectar e receber alteração do CustomerInfo; verificação aguarda SDK e servidor.
- Cache SDK usa requestDate da consulta, evitando renovar sete dias indefinidamente com resposta offline antiga.
- Webhook consulta API RevenueCat: verifica entitlement, Google Play, ambiente, reembolso, validade e carência. Transferência reconcilia as duas contas; nunca concede acesso sem consultar.
- RPC aplica snapshots por data de consulta; evento repetido é idempotente quanto ao estado. Não há tabela de auditoria de eventos.
- Exclusão pede remoção do cliente RevenueCat e depois exclui usuário Supabase com CASCADE; pendência bloqueia uploads.

## Antes de cobrar
Testar pela faixa interna Play: mensal/anual, desistência, pendente, pagamento, restauração, expiração, renovação, carência, account hold, reembolso, troca de conta, reinstalação e sete dias offline. Verificar acknowledgment pelo SDK/painéis. O código não é certificação desses fluxos.

O acesso continua local e modificável por quem alterar o próprio código (decisão mantida). Não adicione recursos pagos de servidor sem verificar entitlement no servidor.
