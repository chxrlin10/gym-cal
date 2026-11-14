# Ranking compartilhado — plano (SÓ PLANEJAMENTO, nada implementado)

## Escopo v1
- Ranking **mensal e privado entre amigos**. Entrada opcional por **código de convite** (6–8 caracteres, expira, revogável pelo dono).
- Mostra **apelido** (nunca nome real/e-mail). Apelido único por grupo, filtro de palavras ofensivas.
- **Pontos competitivos ≠ pontos pessoais.** Só atividade física elegível (treino válido; cardio ≥ 20 min). Alimentação não entra.
- Teto comum: **4 dias pontuáveis por semana** (3 pts/dia → máx. 12/sem + bônus de meta opcional).
- Zera todo mês; histórico de meses anteriores fica só como "campeão do mês".

## Servidor (Supabase)
- Tabelas (futuras): `rk_profiles(user_id, nick, adult_confirmed, created)`, `rk_groups(id, owner, code, month_scope)`, `rk_members(group_id, user_id, joined, left)`, `rk_events(id, user_id, day, kind, minutes, valid, created)`, `rk_reports`.
- **Nunca confiar em pontuação vinda do celular.** O app envia só o *evento* (dia, tipo, duração, nº exercícios/séries); uma **Edge Function** valida (regras iguais ao app, dia dentro de ±1 dia da data do servidor, limite de 4 dias/semana, 1 evento pontuável/dia) e grava. Pontos são calculados no servidor (view/função SQL).
- **ID estável do evento** = hash(user_id + dia + id local do treino/cardio) com `UNIQUE` → evita duplicação em reenvio, edição ou sync de 2 aparelhos.
- Edição/exclusão de registro antigo no app → evento marcado `valid=false` (recalcula).
- **RLS**: membro só lê `rk_members`/pontos agregados do próprio grupo; escreve apenas o próprio perfil; `rk_events` só via Edge Function (service role). Sem acesso a `user_data` de ninguém.
- Anti-abuso: limite de taxa por usuário, máx. de grupos/membros (ex.: 30), eventos com data futura rejeitados.

## Privacidade, LGPD e segurança
- Opt-in explícito, tela dizendo o que é compartilhado (apelido, pontos, dias ativos). Nada de peso, fotos, comida, calorias.
- Controles: sair do grupo, ocultar-me, **denunciar apelido/usuário**, dono remove membro, trocar apelido.
- **Menores desativados** na v1 (confirmação de 18+). Antes de liberar: análise jurídica (LGPD art. 14, ECA Digital) e consentimento parental.
- Exclusão: função `delete_account` apaga perfil/eventos; ao sair do grupo, anonimiza ("Ex-membro") e remove eventos após 30 dias. Política de privacidade e retenção publicadas antes do lançamento.
- Base legal: consentimento; minimização de dados; registro de denúncias com prazo de resposta.

## Custo / manutenção
- Baixo: poucas linhas por usuário/mês; 1 Edge Function + 1 de moderação; sem tempo real (atualiza ao abrir).
- Riscos: moderação de apelidos, suporte a denúncias, trapaça (mitigada por validação servidor + teto de 4 dias).
- Recomendação: lançar só depois de RevenueCat/loja, com piloto fechado de ~20 amigos.

## Fases
1. Política de privacidade + termos + tela de consentimento.
2. Tabelas + RLS + Edge Function de eventos (testes de duplicação/data).
3. UI mínima (entrar por código, lista do mês, sair/denunciar).
4. Piloto fechado → revisão → abertura.


## Manutenção v77
As regras de pontuação, ranks e pausas foram preservadas. Corrigida a perda de metadados antigos: wm e ps não são mais podados após 60/30 semanas. O cálculo deixa de descartar silenciosamente registros com mais de 1.200 dias (limite defensivo de 100 anos). Metadados já descartados por versões anteriores não podem ser reconstruídos com certeza. A migração não inventa metas históricas.
