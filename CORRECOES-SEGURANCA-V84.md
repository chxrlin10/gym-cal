# Gym.cal v84 — Correções de segurança local (ChatGPT)

> Integradas na v85. Decisões, ajuste e resultados dos testes em `REVISAO-CLAUDE.md`.

## Correções feitas
- `stash()` e `snapSet()` retornam sucesso/falha; deixam de ignorar falhas silenciosamente.
- Troca de conta, atualização remota, restauração e substituições manuais exigem cópia local bem-sucedida antes de sobrescrever dados.
- Conflito com ambos os lados alterados e sem snapshot de base deixa de gerar merge automático; exige decisão manual.
- `cPush0()` registra o payload confirmado pelo servidor e programa novo envio se houve edição durante a requisição.
- `cOut(true)` confirma que o conteúdo local atual coincide com o último payload confirmado antes de limpar, com no máximo 3 tentativas adicionais.
- Descrição de alimentos atualizada no texto de loja.

## NÃO corrigido nesta rodada — depende de arquitetura ou validação real
- Merge por conteúdo de registros editados: ainda pode duplicar versões do mesmo treino/refeição. Precisa de IDs por evento e migração cuidadosa.
- `updated_at` controlado pelo cliente: colisões de relógio e ordenação pedem versão de servidor/RPC.
- RLS, exclusão real e RevenueCat precisam ser verificados no projeto do Supabase e Android/Google Play.
- A integridade de `save()` quando o localStorage está cheio ainda requer tratamento transacional mais amplo.
- Este patch é propositalmente conservador e precisa de testes de navegador e 2 aparelhos antes de publicar.
- `applyRemote()` agora recusa substituir a versão local em memória se não conseguir persistir os dados remotos, e `save()` retorna sucesso/falha.
